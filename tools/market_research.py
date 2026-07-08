# tools/market_research.py (from the golden path file ref)
WARNING = "WARNING: Hardcoded demo comparable data; verify before using as market evidence."

_RAW_COMPARABLES = [
    "Senior React developer, 5 yrs, $45/hr, e-commerce projects",
    "Junior frontend dev, 1 yr, $18/hr, portfolio sites",
    "Full-stack engineer, 4 yrs, $50/hr, Shopify integrations",
    "Mid-level React dev, 3 yrs, $35/hr, SaaS dashboards",
]

COMPARABLES = [
    {"text": text, "description": f"{WARNING} {text}"}
    for text in _RAW_COMPARABLES
]

def get_comparables(skill: str | None = None) -> list[dict]:
    """Returns hardcoded comparable rate data for the demo. skill param
    reserved for future filtering — currently returns full golden-path set."""
    return COMPARABLES