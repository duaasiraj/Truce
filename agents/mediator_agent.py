"""
agents/mediator_agent.py
Runs a bounded price negotiation between client ceiling and freelancer floor.

Hackathon MVP: budget_hint (client) and PriceFloor.amount (freelancer) must use
the same unit — demo briefs use hourly-equivalent values.

Deterministic logic (offer math, clamping, round cap, termination) lives in
plain Python. The LLM only generates natural-language messages per round.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone

from pydantic import ValidationError

from config.settings import settings
from db import operations as db
from models.schemas import NegotiationState
from tools.llm_client import GemmaCallError, call_gemma

STRICT_JSON_SUFFIX = (
    "\n\nReturn ONLY valid JSON, no other text. "
    "Do not include markdown fences or explanations."
)

OFFER_TOLERANCE = 0.01

NEGOTIATION_MESSAGE_PROMPT = """You are a neutral mediator helping a client and freelancer agree on an hourly rate.

Context:
- Freelancer floor (minimum): ${floor}/hr
- Client ceiling (maximum): ${ceiling}/hr
- This round's offer: ${offer}/hr
- Round {round_number} of {round_cap}

Recent history:
{history}

Write a brief, professional message explaining this round's offer to both parties.
Return JSON with exactly this structure:
{{
  "message": "<string, 2-4 sentences>"
}}
"""


class MediatorAgentError(Exception):
    pass


def get_negotiation_summary(project_id: str) -> NegotiationState | None:
    """Load existing negotiation_state row for a project, if any."""
    row = db.get_negotiation_state(project_id)
    if row is None:
        return None
    return NegotiationState(**row)


def run_negotiation(project_id: str, version_id: str) -> NegotiationState:
    """
    Initialize negotiation, run bounded loop, persist state + rounds,
    return terminal NegotiationState.
    """
    existing = get_negotiation_summary(project_id)
    if existing is not None and existing.status != "open":
        return existing

    floor = _resolve_floor(version_id)
    ceiling = _resolve_ceiling(version_id)
    round_cap = settings.NEGOTIATION_ROUND_CAP

    if floor > ceiling:
        if existing is not None:
            return _persist_terminal_state(
                project_id=project_id,
                floor=floor,
                ceiling=ceiling,
                current_offer=ceiling,
                round_count=existing.round_count,
                status="capped_no_deal",
                negotiation_id=str(existing.negotiation_id),
            )
        return _persist_terminal_state(
            project_id=project_id,
            floor=floor,
            ceiling=ceiling,
            current_offer=ceiling,
            round_count=0,
            status="capped_no_deal",
        )

    if existing is not None and existing.status == "open":
        negotiation_id = str(existing.negotiation_id)
        state = existing
    else:
        midpoint = round((floor + ceiling) / 2, 2)
        state_row = db.save_negotiation_state({
            "project_id": project_id,
            "floor": floor,
            "ceiling": ceiling,
            "current_offer": midpoint,
            "round_count": 0,
            "status": "open",
        })
        if state_row is None:
            raise MediatorAgentError("Failed to save negotiation state")
        state = NegotiationState(**state_row)
        negotiation_id = str(state.negotiation_id)

    db.update_project_status(project_id, "negotiating")

    if floor == ceiling:
        return _finalize_converged(
            project_id=project_id,
            negotiation_id=negotiation_id,
            floor=floor,
            ceiling=ceiling,
            offer=floor,
            round_count=1,
            message=(
                f"Both parties align at ${floor:.2f}/hr — no negotiation needed."
            ),
        )

    previous_offer: float | None = None
    prior_messages: list[str] = []

    while state.round_count < round_cap and state.status == "open":
        round_number = state.round_count + 1
        offer = _next_offer(floor, ceiling, round_number, round_cap)
        message = _call_negotiation_message_llm(
            project_id=project_id,
            floor=floor,
            ceiling=ceiling,
            offer=offer,
            round_number=round_number,
            round_cap=round_cap,
            prior_messages=prior_messages,
        )

        round_row = db.save_negotiation_round({
            "negotiation_id": negotiation_id,
            "round_number": round_number,
            "actor": "mediator",
            "offer": offer,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if round_row is None:
            raise MediatorAgentError(f"Failed to save negotiation round {round_number}")

        prior_messages.append(f"Round {round_number}: ${offer:.2f}/hr — {message}")
        if len(prior_messages) > 3:
            prior_messages = prior_messages[-3:]

        converged = (
            previous_offer is not None
            and abs(offer - previous_offer) < OFFER_TOLERANCE
        )

        if converged:
            return _finalize_converged(
                project_id=project_id,
                negotiation_id=negotiation_id,
                floor=floor,
                ceiling=ceiling,
                offer=offer,
                round_count=round_number,
                message=message,
            )

        updated = db.update_negotiation_state(negotiation_id, {
            "current_offer": offer,
            "round_count": round_number,
            "status": "open",
        })
        if updated is None:
            raise MediatorAgentError("Failed to update negotiation state")
        state = NegotiationState(**updated)
        previous_offer = offer

    if state.round_count >= round_cap:
        return _finalize_converged(
            project_id=project_id,
            negotiation_id=negotiation_id,
            floor=floor,
            ceiling=ceiling,
            offer=state.current_offer,
            round_count=state.round_count,
            message=(
                f"Agreement reached at ${state.current_offer:.2f}/hr after "
                f"{state.round_count} rounds — the offer represents a fair midpoint."
            ),
        )

    # This fallback should only be hit if the loop exited abnormally (e.g., status changed).
    return _persist_terminal_state(
        project_id=project_id,
        floor=floor,
        ceiling=ceiling,
        current_offer=state.current_offer,
        round_count=state.round_count,
        status="capped_no_deal",
        negotiation_id=negotiation_id,
    )


def _resolve_floor(version_id: str) -> float:
    floor_row = db.get_price_floor_by_version(version_id)
    if not floor_row:
        raise MediatorAgentError(f"No price floor for version {version_id}")
    return float(floor_row["amount"])


def _resolve_ceiling(version_id: str) -> float:
    reqs = db.get_requirements_by_version(version_id)
    budget_req = next((r for r in reqs if r["type"] == "budget"), None)
    if not budget_req or budget_req.get("budget_hint") is None:
        raise MediatorAgentError("No client budget ceiling available")
    return float(budget_req["budget_hint"])


def _next_offer(floor: float, ceiling: float, round_index: int, cap: int) -> float:
    """
    Dynamic Convergence: Concessions slow down exponentially as rounds progress,
    converging smoothly toward a fair midpoint while respecting limits.
    """
    if floor == ceiling or cap <= 1:
        return round(floor, 2)

    midpoint = (floor + ceiling) / 2.0
    progress = round_index / cap
    k = 3.0
    weight = 1.0 - math.exp(-k * progress)
    max_weight = 1.0 - math.exp(-k)
    normalized_weight = weight / max_weight

    raw_offer = ceiling - normalized_weight * (ceiling - midpoint)
    return round(max(floor, min(ceiling, raw_offer)), 2)


def _call_negotiation_message_llm(
    project_id: str,
    floor: float,
    ceiling: float,
    offer: float,
    round_number: int,
    round_cap: int,
    prior_messages: list[str],
) -> str:
    history = "\n".join(prior_messages) if prior_messages else "(none yet)"
    prompt = NEGOTIATION_MESSAGE_PROMPT.format(
        floor=floor,
        ceiling=ceiling,
        offer=offer,
        round_number=round_number,
        round_cap=round_cap,
        history=history,
    )
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            current_prompt = prompt if attempt == 0 else prompt + STRICT_JSON_SUFFIX
            raw = call_gemma(
                agent_name="mediator_agent",
                purpose="negotiation_move",
                prompt=current_prompt,
                project_id=project_id,
                temperature=0.1 if attempt == 1 else 0.3,
            )
            return _parse_negotiation_message(raw)
        except (
            GemmaCallError,
            MediatorAgentError,
            json.JSONDecodeError,
            ValidationError,
        ) as exc:
            last_error = exc

    raise MediatorAgentError(
        f"Negotiation message generation failed after retry: {last_error}"
    ) from last_error


def _parse_negotiation_message(raw: str) -> str:
    text = raw.strip()
    fence_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        # Try to find a standalone JSON object
        obj_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if obj_match:
            text = obj_match.group(1)
    data = json.loads(text)
    return data.get("message", "").strip()


def _persist_terminal_state(
    project_id: str,
    floor: float,
    ceiling: float,
    current_offer: float,
    round_count: int,
    status: str,
    negotiation_id: str | None = None,
) -> NegotiationState:
    """Save final state and update project status."""
    if negotiation_id is None:
        state_row = db.save_negotiation_state({
            "project_id": project_id,
            "floor": floor,
            "ceiling": ceiling,
            "current_offer": current_offer,
            "round_count": round_count,
            "status": status,
        })
        if state_row is None:
            raise MediatorAgentError("Failed to save terminal negotiation state")
        state = NegotiationState(**state_row)
        negotiation_id = str(state.negotiation_id)
    else:
        updated = db.update_negotiation_state(negotiation_id, {
            "current_offer": current_offer,
            "round_count": round_count,
            "status": status,
        })
        if updated is None:
            raise MediatorAgentError("Failed to update terminal negotiation state")
        state = NegotiationState(**updated)

    # Update project status based on outcome
    if status == "converged":
        db.update_project_status(project_id, "pricing_ready")
    else:
        db.update_project_status(project_id, "no_deal_possible")

    return state


def _finalize_converged(
    project_id: str,
    negotiation_id: str,
    floor: float,
    ceiling: float,
    offer: float,
    round_count: int,
    message: str,
) -> NegotiationState:
    """Helper to persist a converged state and save a final mediator message."""
    # Save the final round message if not already saved (e.g., floor==ceiling case)
    # For the normal flow, the last round is already saved, but we add a final record
    # to clearly mark convergence.
    round_row = db.save_negotiation_round({
        "negotiation_id": negotiation_id,
        "round_number": round_count + 1,  # one extra to signal settlement
        "actor": "mediator",
        "offer": offer,
        "message": f"Agreement confirmed: {message}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if round_row is None:
        raise MediatorAgentError("Failed to save convergence round")

    return _persist_terminal_state(
        project_id=project_id,
        floor=floor,
        ceiling=ceiling,
        current_offer=offer,
        round_count=round_count,
        status="converged",
        negotiation_id=negotiation_id,
    )