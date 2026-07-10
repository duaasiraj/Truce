"""
ui/theme.py
Color tokens, typography, and CSS injection. Warm neutral base,
citrus palette reserved for small accents (buttons, badges, highlights).
Call apply_theme() once at the top of app.py, before anything else renders.
"""
import streamlit as st

# --- Accent palette (used sparingly: buttons, badges, highlights) ---
OLIVE = "#BDC749"
CREAM_ORANGE = "#F8D084"
BRICK_RED = "#B53209"
AMBER = "#E59113"

LIGHT = {
    "bg": "#FAF6EF",
    "surface": "#FFFFFF",
    "surface_glass": "rgba(255, 255, 255, 0.6)",
    "text": "#2B2620",
    "text_muted": "#6B6459",
    "border": "#E8E1D4",
}

DARK = {
    "bg": "#211D1A",
    "surface": "#2C2722",
    "surface_glass": "rgba(44, 39, 34, 0.6)",
    "text": "#F5F0E8",
    "text_muted": "#A69C8C",
    "border": "#3D362E",
}

STATUS_COLORS = {
    "draft": "#A69C8C",
    "requirements_extracted": AMBER,
    "clarifications_pending": AMBER,
    "pricing_ready": CREAM_ORANGE,
    "negotiating": AMBER,
    "contract_generated": OLIVE,
    "signed": OLIVE,
    "completed": OLIVE,
    "cancelled": BRICK_RED,
}


def apply_theme(mode: str = "light") -> None:
    """mode: 'light' or 'dark'. Injects CSS variables + base styling."""
    palette = DARK if mode == "dark" else LIGHT

    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {palette['bg']};
            --surface: {palette['surface']};
            --surface-glass: {palette['surface_glass']};
            --text: {palette['text']};
            --text-muted: {palette['text_muted']};
            --border: {palette['border']};
            --accent-olive: {OLIVE};
            --accent-cream: {CREAM_ORANGE};
            --accent-red: {BRICK_RED};
            --accent-amber: {AMBER};
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp {{
            background-color: var(--bg);
            color: var(--text);
        }}

        .truce-card {{
            background: var(--surface-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }}
        .truce-card:hover {{
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.10);
            transform: translateY(-2px);
        }}

        .stButton > button {{
            border-radius: 12px;
            border: none;
            background: var(--accent-amber);
            color: #FFFFFF;
            padding: 0.6rem 1.4rem;
            font-weight: 600;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 2px 8px rgba(229, 145, 19, 0.25);
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(229, 145, 19, 0.35);
        }}

        .truce-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #FFFFFF;
        }}

        h1, h2, h3 {{
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .block-container {{
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }}
        /* Fix low-contrast text inputs -- Streamlit's own classes need direct targeting */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {{
            color: var(--text) !important;
            background-color: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }}
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: var(--text-muted) !important;
            opacity: 1 !important;
        }}
        label, .stRadio label p {{
            color: var(--text) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_badge_html(status: str) -> str:
    color = STATUS_COLORS.get(status, "#A69C8C")
    label = status.replace("_", " ").title()
    return f'<span class="truce-badge" style="background:{color};">{label}</span>'