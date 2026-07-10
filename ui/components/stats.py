"""
ui/components/stats.py
Dashboard stat cards -- computed at read time from an already-fetched
project list, not a stored table.
"""
import streamlit as st

ACTIVE_STATUSES = {
    "requirements_extracted", "clarifications_pending",
    "pricing_ready", "negotiating",
}


def render_stats(projects: list[dict]) -> None:
    total = len(projects)
    active = sum(1 for p in projects if p.get("status") in ACTIVE_STATUSES)
    signed = sum(1 for p in projects if p.get("status") in ("signed", "completed"))
    cancelled = sum(1 for p in projects if p.get("status") == "cancelled")

    cols = st.columns(4)
    labels_values = [
        ("Total Projects", total),
        ("Active", active),
        ("Signed", signed),
        ("No Deal", cancelled),
    ]
    for col, (label, value) in zip(cols, labels_values):
        with col:
            st.markdown(
                f"""
                <div class="truce-card" style="text-align:center;">
                    <p style="color:var(--text-muted); margin:0; font-size:0.85rem;">{label}</p>
                    <p style="font-size:2rem; font-weight:700; margin:0.25rem 0 0 0;">{value}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )