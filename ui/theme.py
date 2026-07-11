"""
ui/theme.py
Color tokens, typography, and CSS injection. Warm neutral base,
citrus palette reserved for small accents (buttons, badges, highlights).
Call apply_theme() once at the top of app.py, before anything else renders.
"""
import streamlit as st

# --- Accent palette (used sparingly: buttons, badges, highlights) ---
# Source: latest palette reference (Avocado / Chili Red / Peach).
# AMBER has no direct match in that reference -- kept as a distinct 4th
# accent (mid-tone between Peach and Chili Red) since the UI uses 4 status
# tones. Flag if you'd rather collapse to 3 and repurpose one elsewhere.
OLIVE = "#72891B"         # was #BDC749 (Avocado)
CREAM_ORANGE = "#F8D78F"  # was #F8D084 (Peach)
BRICK_RED = "#CB2602"     # was #B53209 (Chili Red)
AMBER = "#E08A2B"         # was #E59113 (derived, not in source image)

LIGHT = {
    "bg": "#FAF6EF",
    "bg_end": "#F3E6D2",
    "surface": "#FFFFFF",
    "surface_glass": "rgba(255, 255, 255, 0.72)",
    "text": "#2B2620",
    "text_muted": "#6B6459",
    "border": "#DDD2C0",
    "sidebar_bg": "#F2EBDD",
    "glow1": "rgba(224, 138, 43, 0.14)",
    "glow2": "rgba(114, 137, 27, 0.10)",
}

DARK = {
    "bg": "#211D1A",
    "bg_end": "#2A2019",
    "surface": "#2C2722",
    "surface_glass": "rgba(44, 39, 34, 0.82)",
    "text": "#F5F0E8",
    "text_muted": "#BBB0A0",
    "border": "#4A4038",
    "sidebar_bg": "#18140F",
    "glow1": "rgba(224, 138, 43, 0.16)",
    "glow2": "rgba(114, 137, 27, 0.12)",
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
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Explora&display=swap');

        :root {{
            --bg: {palette['bg']};
            --bg-end: {palette['bg_end']};
            --surface: {palette['surface']};
            --surface-glass: {palette['surface_glass']};
            --text: {palette['text']};
            --text-muted: {palette['text_muted']};
            --border: {palette['border']};
            --sidebar-bg: {palette['sidebar_bg']};
            --accent-olive: {OLIVE};
            --accent-cream: {CREAM_ORANGE};
            --accent-red: {BRICK_RED};
            --accent-amber: {AMBER};
            --glow-1: {palette['glow1']};
            --glow-2: {palette['glow2']};
            --font-display: 'Explora', 'Plus Jakarta Sans', cursive;
        }}

        /* --- Typography: force it everywhere Streamlit renders, --- */
        /* --- since [class*="css"] doesn't match modern Streamlit's real classes --- */
        /* IMPORTANT: Streamlit's built-in icons (sidebar collapse, expander */
        /* chevron, password reveal, etc.) are rendered as text ligatures in */
        /* a dedicated icon font. A blanket `.stApp *` rule clobbers that font */
        /* on those elements too, so the browser falls back to showing the */
        /* literal ligature name ("keyboard_double_arrow_left") as plain text */
        /* instead of the glyph. Excluding them here keeps Streamlit's own */
        /* icon-font rule (which directly targets these elements) in charge. */
        html, body, .stApp,
        .stApp *:not([data-testid="stIconMaterial"]):not([class*="material-symbols"]):not([class*="material-icons"]) {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        /* Keep icon glyphs colored consistently with our palette without */
        /* touching their font-family. */
        [data-testid="stIconMaterial"] {{
            color: var(--text) !important;
        }}

        .stApp {{
            background: linear-gradient(160deg, var(--bg) 0%, var(--bg-end) 100%) fixed;
            color: var(--text);
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        /* Soft ambient glow blobs behind the content -- fixed so they don't */
        /* move with scroll, low-opacity so they read as atmosphere not noise. */
        [data-testid="stAppViewContainer"] {{
            position: relative;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(600px circle at 12% 8%, var(--glow-1), transparent 60%),
                radial-gradient(680px circle at 88% 82%, var(--glow-2), transparent 60%);
        }}
        [data-testid="stAppViewContainer"] > .main {{
            position: relative;
            z-index: 1;
        }}

        /* Streamlit's own chrome (top toolbar) -- blend it, but keep it opaque */
        /* enough that scrolled content doesn't show through the sticky bar. */
        header[data-testid="stHeader"] {{
            background: var(--bg) !important;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }}

        /* Sidebar collapse / expand control + password reveal button: both */
        /* are Material-icon ligatures, fixed by the font-family exclusion */
        /* above -- this just keeps their color/background on-theme too. */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        button[kind="header"] {{
            color: var(--text) !important;
            background: transparent !important;
            overflow: visible !important;
        }}
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg,
        button[kind="header"] svg {{
            fill: var(--text) !important;
            opacity: 1 !important;
        }}

        /* Sidebar never inherited our theme vars before -- explicit now */
        section[data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border);
        }}

        /* --- Force real text contrast: Streamlit hardcodes its own default --- */
        /* --- paragraph/heading colors regardless of our theme, so anything --- */
        /* --- without one of our own truce- classes needs an explicit override --- */
        .stMarkdown p:not([class*="truce-"]),
        .stMarkdown li:not([class*="truce-"]),
        .stMarkdown span:not([class*="truce-"]):not(.truce-badge) {{
            color: var(--text);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text) !important;
        }}
        [data-testid="stCaptionContainer"] p {{
            color: var(--text-muted) !important;
        }}
        label, .stRadio label p, .stCheckbox label p {{
            color: var(--text) !important;
        }}

        /* --- Generic glass cards (used by static markdown blocks) --- */
        .truce-card {{
            background: var(--surface-glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
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

        .truce-card-glass {{
            background: var(--surface-glass); backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border); border-radius: 20px; padding: 1.5rem;
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }}
        .truce-card-glass:hover {{
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
            transform: translateY(-1px);
        }}

        /* --- Real st.container(key=...) cards --- */
        /* Use key="cardwrap_<anything>" on any container to get card styling */
        /* that actually wraps its children (unlike splitting <div> across */
        /* separate st.markdown calls, which does NOT nest in the real DOM). */
        div[class*="st-key-cardwrap_"] > div,
        div[class*="st-key-project_card"] > div {{
            background: var(--surface-glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 14px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
            transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
        }}
        div[class*="st-key-project_card"] > div {{
            cursor: pointer;
        }}
        div[class*="st-key-project_card"] > div:hover {{
            box-shadow: 0 10px 32px rgba(0, 0, 0, 0.10);
            transform: translateY(-2px);
            border-color: var(--accent-amber);
        }}
        div[class*="st-key-project_card"] > div:active {{
            transform: translateY(-1px) scale(0.995);
        }}

        /* --- Buttons: ghost by default, amber only for primary actions --- */
        .stButton > button {{
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text) !important;
            padding: 0.6rem 1.4rem;
            font-weight: 600;
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            cursor: pointer;
        }}
        .stButton > button p {{ color: inherit !important; }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            border-color: var(--accent-amber);
            color: var(--accent-amber) !important;
        }}
        .stButton > button:active {{
            transform: translateY(0) scale(0.97);
        }}
        .stButton > button[kind="primary"] {{
            background: var(--accent-amber);
            color: #FFFFFF !important;
            border: none;
            box-shadow: 0 2px 8px rgba(224, 138, 43, 0.25);
        }}
        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 4px 16px rgba(224, 138, 43, 0.35);
            color: #FFFFFF !important;
        }}
        /* Newer Streamlit builds render the real <button> with these testids;
           force the same ghost styling here too so icon-only buttons (e.g. "←")
           never fall back to the browser/Streamlit default (which renders as a
           solid dark square with invisible text). */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondaryFormSubmit"] {{
            background: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
        }}
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primaryFormSubmit"] {{
            background: var(--accent-amber) !important;
            color: #FFFFFF !important;
            border: none !important;
        }}
        button[data-testid^="stBaseButton-"] p,
        button[data-testid^="stBaseButton-"] span {{
            color: inherit !important;
        }}

        /* --- Tabs: force explicit contrast on both states (baseweb's own --- */
        /* --- inline colors otherwise win on some Streamlit builds) --- */
        .stTabs [data-baseweb="tab"] p {{
            color: var(--text-muted) !important;
        }}
        .stTabs [aria-selected="true"] p {{
            color: var(--text) !important;
        }}

        /* Sidebar buttons stay quiet -- no amber glow floating in the nav */
        section[data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            background: transparent;
            border: 1px solid transparent;
            box-shadow: none;
            font-weight: 500;
            text-align: left;
            justify-content: flex-start;
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            transition: background-color 0.15s ease, border-color 0.15s ease, padding-left 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: var(--surface);
            border-color: var(--border);
            padding-left: 1.7rem;
            box-shadow: none;
        }}

        .truce-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #FFFFFF;
            transition: transform 0.15s ease;
        }}
        .truce-badge:hover {{ transform: translateY(-1px) scale(1.04); }}

        /* Plain content links get the same warm accent + a soft animated underline */
        .stMarkdown a, [data-testid="stAppViewContainer"] a:not(.stButton *):not([data-testid="stLinkButton"] *) {{
            color: var(--accent-amber) !important;
            text-decoration: none;
            background-image: linear-gradient(var(--accent-amber), var(--accent-amber));
            background-repeat: no-repeat;
            background-position: 0 100%;
            background-size: 0% 2px;
            transition: background-size 0.2s ease;
        }}
        .stMarkdown a:hover, [data-testid="stAppViewContainer"] a:not(.stButton *):not([data-testid="stLinkButton"] *):hover {{
            background-size: 100% 2px;
        }}

        h1, h2, h3 {{
            font-weight: 800;
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
        /* Password-visibility toggle icon button sits inside the input's own */
        /* root element -- keep it transparent and correctly colored, and make */
        /* sure it isn't clipped by the input's rounded-corner overflow. */
        .stTextInput button, [data-testid="textInputRootElement"] button,
        [data-testid="textInputRootElement"] button[data-testid^="stBaseButton-"] {{
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            color: var(--text-muted) !important;
            box-shadow: none !important;
        }}
        [data-testid="textInputRootElement"] button svg {{
            fill: var(--text-muted) !important;
        }}
        [data-testid="textInputRootElement"] {{
            overflow: visible !important;
        }}

        .truce-secondary {{ color: var(--text-muted) !important; }}
        .truce-badge-success {{ background: var(--accent-olive); color:#fff; padding:4px 12px; border-radius:999px; font-size:0.75rem; font-weight:600; }}
        .truce-badge-pending {{ background: var(--accent-cream); color:#5A4A28; padding:4px 12px; border-radius:999px; font-size:0.75rem; font-weight:600; }}
        .truce-badge-active {{ background: var(--accent-amber); color:#fff; padding:4px 12px; border-radius:999px; font-size:0.75rem; font-weight:600; }}
        .truce-badge-warning {{ background: var(--accent-red); color:#fff; padding:4px 12px; border-radius:999px; font-size:0.75rem; font-weight:600; }}
        .truce-bubble {{
            border-radius: 14px; padding: 0.75rem 1rem; margin: 6px 0; max-width: 80%;
            animation: truce-bubble-in 0.35s ease both;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .truce-bubble:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        }}
        .truce-bubble-offer {{ background: var(--surface); border: 1px solid var(--border); font-weight:600; }}
        .truce-bubble-mediator {{ background: var(--accent-cream); color:#5A4A28; margin-left: auto; }}
        .truce-loading-text {{ color: var(--accent-amber); font-style: italic; }}

        @keyframes truce-bubble-in {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .truce-round-marker {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 22px; height: 22px; border-radius: 50%;
            background: var(--surface); border: 1px solid var(--border);
            color: var(--text-muted); font-size: 0.7rem; font-weight: 700;
            margin-right: 8px; flex-shrink: 0;
            transition: border-color 0.15s ease, color 0.15s ease;
        }}
        .truce-bubble:hover .truce-round-marker {{
            border-color: var(--accent-amber);
            color: var(--accent-amber);
        }}

        .truce-empty-state {{
            text-align: center; padding: 2rem 1rem;
            color: var(--text-muted);
        }}
        .truce-empty-state .truce-empty-icon {{
            font-size: 1.8rem; margin-bottom: 0.4rem; opacity: 0.7;
        }}

        /* --- Native alert boxes (st.info / st.success / st.warning / st.error) --- */
        /* Streamlit's defaults clash hard with a warm palette, so we soften them */
        /* into tinted glass cards instead of stark red/green/blue banners. */
        div[data-testid="stAlert"],
        div[data-testid*="stNotification"],
        [data-baseweb="notification"] {{
            border-radius: 16px !important;
            border: 1px solid var(--border) !important;
            background: var(--surface-glass) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
        }}
        div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {{
            color: var(--text) !important;
        }}
        div[data-testid="stAlert"]:has(svg[title="Info"]),
        div[data-testid="stAlert"]:has([data-testid="stIconInfo"]) {{
            border-left: 4px solid var(--accent-amber) !important;
        }}
        div[data-testid="stAlert"]:has(svg[title="Success"]),
        div[data-testid="stAlert"]:has([data-testid="stIconSuccess"]) {{
            border-left: 4px solid var(--accent-olive) !important;
        }}
        div[data-testid="stAlert"]:has(svg[title="Warning"]),
        div[data-testid="stAlert"]:has([data-testid="stIconWarning"]) {{
            border-left: 4px solid var(--accent-cream) !important;
        }}
        div[data-testid="stAlert"]:has(svg[title="Error"]),
        div[data-testid="stAlert"]:has([data-testid="stIconError"]) {{
            border-left: 4px solid var(--accent-red) !important;
        }}

        /* --- Expanders: match the glass card language --- */
        div[data-testid="stExpander"] {{
            background: var(--surface-glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border) !important;
            border-radius: 16px !important;
            overflow: hidden;
        }}
        div[data-testid="stExpander"] summary {{
            font-weight: 600;
            transition: color 0.15s ease;
        }}
        div[data-testid="stExpander"] summary:hover {{
            color: var(--accent-amber) !important;
        }}
        div[data-testid="stExpander"] summary svg {{
            transition: transform 0.2s ease;
        }}
        details[data-testid="stExpander"][open] summary svg {{
            transform: rotate(180deg);
        }}

        /* --- Tabs: pill-style with an animated amber underline --- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            border-bottom: 1px solid var(--border);
        }}
        .stTabs [data-baseweb="tab"] {{
            color: var(--text-muted);
            font-weight: 600;
            transition: color 0.15s ease;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: var(--accent-amber);
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--text) !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: var(--accent-amber) !important;
            transition: left 0.25s ease, width 0.25s ease;
        }}

        /* --- Spinner: recolor to accent-amber instead of default red --- */
        div[data-testid="stSpinner"] p {{
            color: var(--accent-amber) !important;
            font-style: italic;
        }}
        div[data-testid="stSpinner"] svg {{
            color: var(--accent-amber) !important;
        }}

        /* --- Forms: strip Streamlit's default border box, our own card wraps it --- */
        div[data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
        }}

        /* --- Link buttons (st.link_button) mirror regular buttons --- */
        a[data-testid="stBaseButtonSecondary"], a[data-testid="stBaseButton-secondary"],
        div[data-testid="stLinkButton"] a {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }}
        a[data-testid="stBaseButtonPrimary"], a[data-testid="stBaseButton-primary"],
        div[data-testid="stLinkButton"] a[kind="primary"] {{
            background: var(--accent-amber) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(224, 138, 43, 0.25) !important;
        }}
        div[data-testid="stLinkButton"] a:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(224, 138, 43, 0.3) !important;
        }}

        /* --- Radio & checkbox indicators: swap Streamlit red for accent-amber --- */
        [role="radio"][aria-checked="true"] svg,
        [role="checkbox"][aria-checked="true"] svg {{
            fill: var(--accent-amber) !important;
        }}
        [role="radio"][aria-checked="true"] {{
            border-color: var(--accent-amber) !important;
        }}

        /* --- Number input steppers --- */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"] {{
            background: var(--surface) !important;
            border-color: var(--border) !important;
        }}
        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover {{
            border-color: var(--accent-amber) !important;
        }}

        /* --- Focus rings: warm instead of default blue/red --- */
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--accent-amber) !important;
            box-shadow: 0 0 0 3px rgba(224, 138, 43, 0.15) !important;
            outline: none !important;
        }}

        /* --- Selection + scrollbar: small, everywhere touches --- */
        ::selection {{
            background: var(--accent-amber);
            color: #FFFFFF;
        }}
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 999px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-amber); }}

        /* --- Gentle page-load fade so re-runs don't feel like a hard flash --- */
        .block-container {{
            animation: truce-page-in 0.35s ease both;
        }}
        @keyframes truce-page-in {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .block-container, .truce-bubble {{ animation: none !important; }}
        }}

        /* --- Responsive tightening on small screens --- */
        @media (max-width: 640px) {{
            .truce-card, .truce-card-glass {{ padding: 1rem; }}
            div[class*="st-key-project_card"] > div,
            div[class*="st-key-cardwrap_"] > div {{ padding: 1rem; }}
            .block-container {{ padding-top: 1.5rem; padding-left: 1rem; padding-right: 1rem; }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle() -> None:
    """Renders a light/dark mode toggle button. Call once, inside the sidebar."""
    current = st.session_state.get("theme_mode", "light")
    if current == "light":
        icon, label, next_mode = "🌙", "Dark mode", "dark"
    else:
        icon, label, next_mode = "☀️", "Light mode", "light"

    if st.button(f"{icon}  {label}", key="theme_toggle", use_container_width=True):
        st.session_state["theme_mode"] = next_mode
        st.rerun()


def status_badge_html(status: str) -> str:
    color = STATUS_COLORS.get(status, "#A69C8C")
    label = status.replace("_", " ").title()
    return f'<span class="truce-badge" style="background:{color};">{label}</span>'