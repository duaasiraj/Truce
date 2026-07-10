# api.py
# Production-ready Flask API wrapper for Truce CrewAI/Procedural backend.
# NOTE: Do NOT import torch, transformers, or accelerate at the top level of this file.
# Heavy ML imports are guarded inside rate_ranking.py and will not be loaded at startup.

import os
import sys
import dataclasses
from flask import Flask, request, jsonify

# Import the main orchestration function
from crew import run_truce_pipeline, PipelineResult
from db import operations as db
from models.schemas import (
    ScopeDocument,
    PriceFloor,
    NegotiationState,
    ClarificationRequest,
)

app = Flask(__name__)

def serialize_pydantic(obj):
    """Recursively serializes Pydantic models, dataclasses, lists, and dicts."""
    if obj is None:
        return None
    if isinstance(obj, list):
        return [serialize_pydantic(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize_pydantic(v) for k, v in obj.items()}
    
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    # Pydantic v1
    if hasattr(obj, "dict"):
        return obj.dict()
    # Dataclass (like PipelineResult)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return serialize_pydantic(dataclasses.asdict(obj))
    
    # Fallback for primitives
    return obj

def serialize_pipeline_result(result: PipelineResult) -> dict:
    """Serializes a PipelineResult object to a JSON-serializable dictionary."""
    return {
        "stage": result.stage,
        "project_id": result.project_id,
        "version_id": result.version_id,
        "pending_clarifications": serialize_pydantic(result.pending_clarifications),
        "scope": serialize_pydantic(result.scope),
        "price_floor": serialize_pydantic(result.price_floor),
        "negotiation": serialize_pydantic(result.negotiation),
        "error": result.error,
        "orchestration": result.orchestration,
    }

@app.route("/", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route("/run", methods=["POST"])
def run_pipeline():
    """
    Main pipeline execution endpoint.
    Accepts JSON:
    {
      "brief": "I need some help getting my small business online...",
      "budget": 1500.0,                  # optional
      "rate": 35.0,                       # optional
      "clarification_answers": {...},     # optional
      "project_id": "...",                # optional (for resume)
      "version_id": "..."                 # optional (for resume)
    }
    """
    try:
        # Read profile IDs from environment variables
        client_profile_id = os.environ.get("CLIENT_PROFILE_ID")
        freelancer_profile_id = os.environ.get("FREELANCER_PROFILE_ID")

        if not client_profile_id or not freelancer_profile_id:
            return jsonify({
                "error": "Configuration error: CLIENT_PROFILE_ID and FREELANCER_PROFILE_ID environment variables must be set."
            }), 500

        data = request.get_json() or {}
        brief = data.get("brief")
        budget = data.get("budget")
        rate = data.get("rate")
        clarification_answers = data.get("clarification_answers")
        project_id = data.get("project_id")
        version_id = data.get("version_id")

        # Validate minimum input needed to either start or resume the pipeline
        if not brief and not (project_id and version_id):
            return jsonify({
                "error": "Invalid request: 'brief' is required to start a project, or both 'project_id' and 'version_id' are required to resume."
            }), 400

        # Construct brief_text including the budget hint if provided
        brief_text = brief or ""
        if budget is not None:
            brief_text = f"{brief_text}\nBudget: {budget}"

        # Resolve rate expectation
        rate_expectation = None
        if rate is not None:
            try:
                rate_expectation = float(rate)
            except ValueError:
                return jsonify({"error": "Invalid rate value: must be a float number."}), 400
        else:
            # Attempt to read rate_expectation from the freelancer profile database row
            try:
                profile = db.get_freelancer_profile(freelancer_profile_id)
                if profile:
                    rate_expectation = float(profile.get("rate_expectation", 50.0))
            except Exception as e:
                print(f"[WARN] Failed to fetch rate expectation from freelancer profile: {e}", file=sys.stderr)
            
            if rate_expectation is None:
                rate_expectation = 50.0

        title = data.get("title", "Truce Project from API")

        # Call the Truce backend pipeline (run procedural mode to fit memory limits on Render)
        result = run_truce_pipeline(
            client_profile_id=client_profile_id,
            title=title,
            brief_text=brief_text,
            freelancer_profile_id=freelancer_profile_id,
            rate_expectation=rate_expectation,
            clarification_answers=clarification_answers,
            project_id=project_id,
            version_id=version_id,
            use_crewai=False
        )

        serialized = serialize_pipeline_result(result)

        if result.stage == "awaiting_clarifications":
            return jsonify(serialized), 202
        elif result.stage == "failed":
            return jsonify(serialized), 400
        else:
            return jsonify(serialized), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/project/<project_id>", methods=["GET"])
def get_project_status(project_id):
    """
    Fetches the project details and current negotiation state from database.
    """
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({"error": f"Project {project_id} not found"}), 404

        # Use the same function crew.py uses
        from crew import get_negotiation_summary
        negotiation = get_negotiation_summary(project_id)
        
        return jsonify({
            "project": project,
            "negotiation": negotiation
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)