"""
ui/components/project_card.py
Reusable card for a project row: title, status badge, assigned-to name, date.
"""
import streamlit as st

from ui.theme import status_badge_html
from db import operations as db


def _resolve_freelancer_name(freelancer_profile_id: str | None) -> str:
    if not freelancer_profile_id:
        return "Unassigned"
    fp = db.get_freelancer_profile(freelancer_profile_id)
    if not fp:
        return "Unassigned"
    profile = db.get_profile(fp["user_id"])
    return profile["name"] if profile else "Unknown"


def _resolve_client_name(client_profile_id: str | None) -> str:
    if not client_profile_id:
        return "Unknown client"
    cp = db.get_client_profile(client_profile_id)
    if not cp:
        return "Unknown client"
    profile = db.get_profile(cp["user_id"])
    return profile["name"] if profile else "Unknown client"


def render_project_card(project: dict, viewer_role: str) -> None:
    title = project.get("title") or "Untitled project"
    status = project.get("status", "draft")
    created = project.get("created_at", "")[:10]

    if viewer_role == "client":
        counterpart_label = "Freelancer"
        counterpart_name = _resolve_freelancer_name(project.get("freelancer_profile_id"))
    else:
        counterpart_label = "Client"
        counterpart_name = _resolve_client_name(project.get("client_profile_id"))

    st.markdown(
        f"""
        <div class="truce-card" style="margin-bottom: 1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0;">{title}</h4>
                {status_badge_html(status)}
            </div>
            <p style="color:var(--text-muted); margin: 0.5rem 0 0 0;">
                {counterpart_label}: {counterpart_name} &nbsp;&middot;&nbsp; Created: {created}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    