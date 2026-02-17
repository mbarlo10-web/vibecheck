import os
import json
import re
import time
import base64
import hashlib
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="VibeCheck",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Styling
# ----------------------------
APP_CSS = """
<style>
/* Hide Streamlit chrome (top white banner, menus) */
header { visibility: hidden; height: 0px; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
div[data-testid="stToolbar"] { visibility: hidden; height: 0px; }

/* Less padding at top so banner sits higher */
.block-container { padding-top: 0.5rem !important; }

/* Background – brighter default (Spring Training); overridden by theme classes */
.stApp {
  background: radial-gradient(circle at 20% 10%, rgba(255,255,255,0.18), rgba(0,0,0,0) 45%),
              linear-gradient(180deg, #1a4a8a 0%, #0d3565 50%, #082548 100%);
  color: #fff;
}
.stApp.theme-bachelorette {
  background: radial-gradient(circle at 20% 10%, rgba(255,20,147,0.25), rgba(0,0,0,0) 45%),
              linear-gradient(180deg, #c71585 0%, #9e0a6a 40%, #6b0848 100%);
}
.stApp.theme-wmpo {
  background: radial-gradient(circle at 20% 10%, rgba(34,139,34,0.2), rgba(0,0,0,0) 45%),
              linear-gradient(180deg, #1a5c3a 0%, #0d3320 50%, #062018 100%);
}

/* Section headers */
.h1 {
  font-size: 54px;
  font-weight: 800;
  margin: 0 0 6px 0;
}
.subhead {
  font-size: 18px;
  opacity: 0.85;
  margin: 0 0 16px 0;
}

/* Cards – brighter, min-height so action buttons fit inside visual bounds */
.card {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
}

/* Radio button labels - high contrast for readability - make ALL text white */
.stRadio > label,
.stRadio > div > label,
div[data-baseweb="radio"] label,
.stRadio label,
.stRadio span,
.stRadio div,
.stRadio p,
.stRadio * {
  color: #ffffff !important;
  font-weight: 800 !important;
  font-size: 17px !important;
}
.stRadio > div[role="radiogroup"] > label {
  color: #ffffff !important;
  font-weight: 800 !important;
  font-size: 17px !important;
}
/* Radio button option text - make bolder and more readable */
.stRadio label[data-baseweb="radio"] span,
.stRadio > div > label > span,
div[data-baseweb="radio"] label span,
.stRadio [data-baseweb="radio"] span,
.stRadio [data-baseweb="radio"] label,
.stRadio [data-baseweb="radio"] div {
  color: #ffffff !important;
  font-weight: 800 !important;
  font-size: 17px !important;
}
/* Force all text inside radio button containers to be white */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] span,
div[data-testid="stRadio"] div,
div[data-testid="stRadio"] p,
div[data-testid="stRadio"] * {
  color: #ffffff !important;
  font-weight: 800 !important;
}

/* -------------------------------------------------------
   BUTTON UX: easier clicks + hover darken + selected stays dark
   ------------------------------------------------------- */

/* Base: make buttons easier to click everywhere */
.stButton > button,
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] a {
  min-height: 33px !important;
  padding: 0.70rem 1.10rem !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  touch-action: manipulation !important;
  transition: background-color 180ms ease, border-color 180ms ease, color 180ms ease, opacity 180ms ease !important;
}

/* Default "secondary" look: light background, dark text */
.stButton > button {
  color: #0b2b5a !important;
  background-color: rgba(255,255,255,0.92) !important;
  border: 2px solid rgba(255,255,255,0.35) !important;
}

/* Hover on secondary: clear darken to blue */
.stButton > button:hover {
  background-color: #1a3a5f !important;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.6) !important;
}
.stButton > button:focus-visible {
  outline: 2px solid rgba(255,255,255,0.7) !important;
  outline-offset: 2px !important;
}

/* Selected (primary): stay dark blue */
[data-testid="stBaseButton-primary"] button,
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background-color: #0b2b5a !important;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.60) !important;
  font-weight: 800 !important;
}

/* Hover on primary: slightly lighter so it's visible */
[data-testid="stBaseButton-primary"] button:hover,
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
  background-color: #1a4a7a !important;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.75) !important;
}

/* Prevent text wrapping on vibe buttons */
.stButton > button {
  white-space: nowrap !important;
}

/* Export / download buttons: visible on dark background */
[data-testid="stDownloadButton"] a,
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] label,
a[download],
button[kind="download"] {
  background-color: #1e3a5f !important;
  color: #fff !important;
  border: 2px solid rgba(255,255,255,0.5) !important;
  font-weight: 700 !important;
}
[data-testid="stDownloadButton"] a:hover,
[data-testid="stDownloadButton"] button:hover,
a[download]:hover,
button[kind="download"]:hover {
  background-color: #2563c7 !important;
  color: #fff !important;
}
[data-testid="stDownloadButton"] a *,
[data-testid="stDownloadButton"] button * {
  color: #fff !important;
}

/* Dates, Group & Budget labels and values: big, bold, high contrast on dark background */
[data-testid="stDateInput"] label,
[data-testid="stDateInput"] p,
[data-testid="stNumberInput"] label,
[data-testid="stNumberInput"] p,
[data-testid="stSlider"] label,
[data-testid="stSlider"] p {
  color: #fff !important;
  font-size: 17px !important;
  font-weight: 700 !important;
}

/* Page 2 swap options: high contrast, easy to read */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] .stExpander summary {
  color: #fff !important;
  font-size: 17px !important;
  font-weight: 800 !important;
  background: transparent !important;
}
[data-testid="stExpander"] .stRadio label { color: #fff !important; font-size: 16px !important; font-weight: 600 !important; }
[data-testid="stExpander"] p { color: rgba(255,255,255,0.95) !important; font-size: 15px !important; }
[data-testid="stExpander"] .stExpander { border: 1px solid rgba(255,255,255,0.25) !important; border-radius: 10px !important; }
/* Apply swap button: always readable (dark bg, white text) */
[data-testid="stExpander"] .stButton > button {
  background-color: #1e3a5f !important;
  color: #ffffff !important;
  border: 2px solid rgba(255,255,255,0.5) !important;
  font-weight: 700 !important;
}
[data-testid="stExpander"] .stButton > button:hover {
  background-color: #1a4a7a !important;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.7) !important;
}

/* Instructions at top: high contrast so they're easy to read */
div[data-testid="stAlert"] { background-color: rgba(255,255,255,0.95) !important; border: 1px solid rgba(0,0,0,0.1) !important; }
div[data-testid="stAlert"] p, div[data-testid="stAlert"] div, div[data-testid="stAlert"] span { color: #1a1a1a !important; }
div[data-testid="stAlert"] a { color: #0b2b5a !important; font-weight: 700 !important; }

/* TextArea readability on light background */
[data-testid="stTextArea"] textarea { color: #1a1a1a !important; }
[data-testid="stTextArea"] label { color: #1a1a1a !important; }

/* Section labels */
.section-label, .team-label {
  color: #fff !important;
  font-size: 18px !important;
  font-weight: 800 !important;
  opacity: 1 !important;
  margin-bottom: 8px !important;
}

/* ---------- Readability: force headings + captions + body text to be bright ---------- */
h1, h2, h3, h4, h5, h6 {
  color: rgba(255,255,255,0.98) !important;
  font-weight: 800 !important;
}

[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li,
[data-testid="stMarkdown"] span,
[data-testid="stText"] {
  color: rgba(255,255,255,0.95) !important;
}

/* Captions sometimes render too dark depending on theme/state */
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span,
[data-testid="stCaptionContainer"] div {
  color: rgba(255,255,255,0.88) !important;
  font-weight: 650 !important;
}

/* Any accidental dark text inside cards */
.card, .card * {
  color: rgba(255,255,255,0.95) !important;
}

/* --- FIX: EVENT CARD AND ACTION BUTTON ALIGNMENT --- */
.card.slot-card {
  min-height: 200px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start !important;
  margin: 0 !important;
  padding: 18px !important;
  padding-top: 18px !important; /* Changed from 30px to 18px */
}

/* Push the card content down to align with first button */
.card.slot-card > div:first-child {
  margin-top: 2px !important;
}

/* Force the horizontal block container to use flexbox with top alignment */
[data-testid="stHorizontalBlock"]:has(.slot-card) {
  display: flex !important;
  align-items: flex-start !important;
  gap: 1rem !important;
}

/* Remove ALL padding and margin from both columns and their children */
[data-testid="stHorizontalBlock"]:has(.slot-card) > [data-testid="column"] {
  padding: 0 !important;
  margin: 0 !important;
}

[data-testid="stHorizontalBlock"]:has(.slot-card) > [data-testid="column"] > div {
  padding: 0 !important;
  margin: 0 !important;
}

[data-testid="stHorizontalBlock"]:has(.slot-card) > [data-testid="column"] > div > div {
  padding: 0 !important;
  margin: 0 !important;
}

/* Style the buttons */
[data-testid="stHorizontalBlock"]:has(.slot-card) [data-testid="stButton"] {
  margin-bottom: 8px !important;
}

[data-testid="stHorizontalBlock"]:has(.slot-card) [data-testid="stButton"]:first-child {
  margin-top: 0 !important;
}

[data-testid="stHorizontalBlock"]:has(.slot-card) [data-testid="stButton"]:last-child {
  margin-bottom: 0 !important;
}

[data-testid="stHorizontalBlock"]:has(.slot-card) [data-testid="stButton"] > button {
  min-height: 40px !important;
  padding: 0.5rem 0.75rem !important;
  font-size: 0.95rem !important;
  border-radius: 10px !important;
  width: 100% !important;
}

/* Page banners – full width, tall height; contain so full image fits (no cropping) */
.page-banner {
  width: 100%;
  max-width: 100%;
  height: 480px;
  overflow: hidden;
  border-radius: 0 0 18px 18px;
  margin-top: -0.5rem;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-banner img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)


# ----------------------------
# Banner images (optional local file, else default URL)
# ----------------------------
# Default banners when no theme-specific image is set (Unsplash fallbacks)
BANNER_WELCOME_DEFAULT = "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200&q=80"   # Scottsdale/resort
BANNER_ITINERARY_DEFAULT = "https://images.unsplash.com/photo-1529963183134-61a90db47eae?w=1200&q=80"  # Pool/outdoor

# Per-theme banner paths (welcome, itinerary). Use a list to rotate multiple images every BANNER_ROTATE_SECS.
BANNER_ROTATE_SECS = 5
BANNERS_BY_THEME = {
    "spring_training": {
        "welcome": ["assets/Salt River FIelds.png", "assets/Cactus League.png"],
        "itinerary": ["assets/Salt River FIelds.png", "assets/Cactus League.png"],
    },
    "bachelorette": {
        "welcome": [
            "assets/Sanctuary-Camelback-Mountain-Resort-and-Spa__2018_Infinity-Pool.png",
            "assets/Bacherlorette pool.png",
            "assets/pool.png",
        ],
        "itinerary": [
            "assets/Bacherlorette pool.png",
            "assets/Sanctuary-Camelback-Mountain-Resort-and-Spa__2018_Infinity-Pool.png",
            "assets/pool.png",
        ],
    },
    "wmpo": {
        "welcome": ["assets/WMPO Sunset.png", "assets/WMPO Premium.png", "assets/WMPO.png"],
        "itinerary": ["assets/WMPO Premium.png", "assets/WMPO Sunset.png", "assets/WMPO.png"],
    },
}


def _banner_src(path_or_url: str) -> str:
    """Return a valid src for banner: base64 data URL if path exists, else treat as URL."""
    if not path_or_url:
        return ""
    p = path_or_url.strip()
    if p.startswith(("http://", "https://")):
        return p
    if os.path.isfile(p):
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(p)[1].lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        return f"data:{mime};base64,{b64}"
    return p


def _banner_for_page(theme: str, page: str) -> List[str]:
    """Return list of paths/URLs for the banner (one or more for rotation)."""
    by_theme = BANNERS_BY_THEME.get(theme, {})
    raw = by_theme.get(page)
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        default = BANNER_WELCOME_DEFAULT if page == "welcome" else BANNER_ITINERARY_DEFAULT
        return [default]
    if isinstance(raw, str):
        return [raw.strip()]
    return [p.strip() for p in raw if p and str(p).strip()]


def render_page_banner(paths_or_urls: List[str], alt: str = "Banner") -> None:
    """Render a full-width banner; if multiple images, rotate every BANNER_ROTATE_SECS."""
    srcs = []
    for p in paths_or_urls:
        s = _banner_src(p) if p else ""
        if s:
            srcs.append(s.replace('"', "&quot;").replace("\\", "\\\\"))
    if not srcs:
        return
    alt_safe = alt.replace('"', "&quot;")
    if len(srcs) == 1:
        st.markdown(
            f'<div class="page-banner"><img src="{srcs[0]}" alt="{alt_safe}"/></div>',
            unsafe_allow_html=True,
        )
        return
    # Multiple images: rotate via CSS animation (no script – works in Streamlit)
    n = len(srcs)
    duration_sec = n * BANNER_ROTATE_SECS
    bid = f"rb-{int(time.time() * 1000)}"
    keyframes = []
    for i in range(n):
        start_pct = 100 * i / n
        end_pct = 100 * (i + 1) / n
        # Image i visible from start_pct to end_pct; otherwise opacity 0
        if i == 0:
            seg1 = f"0%, {end_pct - 0.02:.2f}% {{ opacity:1; }} "
            seg2 = f"{end_pct:.2f}%, 100% {{ opacity:0; }}"
        else:
            seg1 = f"0%, {start_pct - 0.02:.2f}% {{ opacity:0; }} "
            seg2 = f"{start_pct:.2f}%, {end_pct - 0.02:.2f}% {{ opacity:1; }} {end_pct:.2f}%, 100% {{ opacity:0; }}"
        keyframes.append(f"@keyframes {bid}-fade-{i} {{ {seg1}{seg2} }}")
    keyframes_css = "\n".join(keyframes)
    imgs_html = ""
    for i, src in enumerate(srcs):
        imgs_html += (
            f'<img class="rotating-banner-img" src="{src}" alt="{alt_safe}" '
            f'style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;'
            f'animation:{bid}-fade-{i} {duration_sec}s linear infinite;">'
        )
    html = f'''
<style>{keyframes_css}</style>
<div class="page-banner page-banner-rotating" id="{bid}" style="position:relative;">
  {imgs_html}
</div>
'''
    st.markdown(html, unsafe_allow_html=True)


# ----------------------------
# Utilities
# ----------------------------
def safe_read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_venues(raw: Any) -> List[Dict[str, Any]]:
    """
    Accepts venues.json in any of these shapes:
      1) list[dict]
      2) dict with "venues" key -> use raw["venues"] (e.g. {"venues": [...], "spring_training_teams": ...})
      3) dict[str, dict] (like {"0": {...}, "1": {...}}) -> use values
    Returns a clean list[dict].

    Normalization rules:
      - Only allow themes in ALLOWED_THEMES_RAW; drop others (e.g. legacy "bachelor").
      - Map legacy theme label "WMPO" to internal key "wmpo".
      - If a venue ends up with no themes, default it to all three themes.
      - Convert legacy category "shopping" -> "activity" and ensure "shopping" is in vibes.
    """
    if raw is None:
        return []

    if isinstance(raw, list):
        venues = raw
    elif isinstance(raw, dict):
        if "venues" in raw and isinstance(raw["venues"], list):
            venues = raw["venues"]
        else:
            venues = list(raw.values())
    else:
        return []

    # Themes as they may appear in the JSON.
    ALLOWED_THEMES_RAW = {"spring_training", "bachelorette", "WMPO"}

    cleaned: List[Dict[str, Any]] = []
    for v in venues:
        if not isinstance(v, dict):
            continue

        name = str(v.get("name", "")).strip()
        category_raw = (v.get("category", "") or "").strip().lower()
        if not name or not category_raw:
            continue

        # Start from raw vibes/themes.
        vibes = [str(x).strip().lower() for x in (v.get("vibes") or [])]
        raw_themes = [str(x).strip() for x in (v.get("themes") or [])]

        # Normalize category: treat legacy "shopping" as an activity with a
        # "shopping" vibe so it appears in the daytime activity pool.
        if category_raw == "shopping":
            category = "activity"
            if "shopping" not in vibes:
                vibes.append("shopping")
        else:
            category = category_raw

        # Normalize / filter themes.
        norm_themes: List[str] = []
        for t in raw_themes:
            if t not in ALLOWED_THEMES_RAW:
                # Drop legacy labels like "bachelor" but do not fail.
                continue
            if t == "WMPO":
                norm_themes.append("wmpo")
            else:
                norm_themes.append(t.lower())

        # If there are no remaining themes, default to all three.
        if not norm_themes:
            norm_themes = ["spring_training", "bachelorette", "wmpo"]

        v2 = {
            "name": name,
            "category": category,
            "price_tier": v.get("price_tier", 0),
            "vibes": vibes,
            "themes": norm_themes,
            "teams": [str(x).strip() for x in (v.get("teams") or [])],
        }
        if v.get("lat") is not None and v.get("lon") is not None:
            try:
                v2["lat"] = float(v["lat"])
                v2["lon"] = float(v["lon"])
            except (TypeError, ValueError):
                pass
        if v.get("area"):
            v2["area"] = str(v["area"]).strip()
        cleaned.append(v2)

    return cleaned


@st.cache_data(ttl=300)
def load_venues() -> List[Dict[str, Any]]:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(app_dir, "venues.json")
    if not os.path.exists(path):
        path = os.path.join(os.getcwd(), "venues.json")
    if not os.path.exists(path):
        st.error("venues.json not found in the project folder.")
        return []

    try:
        raw = safe_read_json(path)
    except (json.JSONDecodeError, OSError) as e:
        st.error(f"Could not load venues.json: {e}")
        return []
    venues = normalize_venues(raw)
    if not venues:
        st.error("venues.json loaded, but no valid venues were found. Check the JSON structure.")
    return venues


def get_stripe_payment_link() -> str:
    try:
        stripe_block = st.secrets.get("stripe", {})
        if isinstance(stripe_block, dict):
            link = stripe_block.get("payment_link", "")
            if isinstance(link, str) and link.strip():
                return link.strip()
    except Exception:
        pass

    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        secrets_path = os.path.join(app_dir, ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r", encoding="utf-8") as f:
                content = f.read()
            in_stripe = False
            for line in content.splitlines():
                line = line.strip()
                if line == "[stripe]":
                    in_stripe = True
                    continue
                if in_stripe and line.startswith("payment_link"):
                    idx = line.find("=")
                    if idx >= 0:
                        val = line[idx + 1:].strip().strip('"').strip("'")
                        if val.startswith("https://"):
                            return val.strip()
                    break
                if in_stripe and line.startswith("["):
                    break
    except Exception:
        pass

    link2 = os.getenv("VIBECHECK_STRIPE_PAYMENT_LINK", "")
    return link2.strip() if isinstance(link2, str) else ""


def category_reservation_providers(category: str, provider_name: str = "") -> str:
    """
    Human-friendly hint for how bookings are handled.
    
    VibeCheck handles all bookings via APIs (OpenTable, Resy, Ticketmaster, etc.),
    so these messages indicate what VibeCheck will book, not what the user needs to do.
    """
    category = (category or "").lower()
    name = (provider_name or "").strip().lower()

    # Concerts, WMPO, stadium/arena/ballpark-style events -> tickets via VibeCheck.
    concert_keywords = (
        "concert",
        "birds nest",
        "wm phoenix open",
        "stadium",
        "ballpark",
        "arena",
        "game",
    )
    if any(k in name for k in concert_keywords):
        return "VibeCheck will book tickets via Ticketmaster or event site"

    # Golf-specific booking via VibeCheck.
    if category == "golf":
        return "VibeCheck will book tee times via GolfNow"

    # Ball games that are categorized as baseball.
    if category == "baseball":
        return "VibeCheck will book tickets via MLB or Ticketmaster"

    # Topgolf / PopStroke / Puttshack and similar golf-entertainment venues.
    if any(k in name for k in ("topgolf", "popstroke", "puttshack")):
        return "VibeCheck will handle reservations"

    # Dining / brunch / nightlife (restaurants, bars, clubs).
    if category in {"dining", "brunch", "nightlife"}:
        return "VibeCheck will book via OpenTable, Resy, or venue"

    if category == "activity":
        return "VibeCheck will handle booking"
    if category == "spa":
        return "VibeCheck will book via resort or spa site"
    if category == "pool":
        return "VibeCheck will book resort or daybed reservation"
    if category == "shopping":
        return "VibeCheck will coordinate shopping stops"
    if category == "transport":
        pretty_name = provider_name.strip() if provider_name else ""
        if pretty_name:
            return f"VibeCheck will arrange {pretty_name}"
        return "VibeCheck will arrange transportation"
    return ""


def _bachelorette_ok_venue(v: Dict[str, Any]) -> bool:
    if not isinstance(v, dict):
        return False
    name = (v.get("name") or "").lower()
    vibes = [x.lower() for x in (v.get("vibes") or [])]
    skip_names = (
        "golf", "baseball", "popstroke", "topgolf", "puttshack", "stadium", "sloan",
        "salt river", "talking stick", "hohokam", "diablo", "dback", "octane",
        "dbat", "taroko", "baseballism"
    )
    if any(s in name for s in skip_names) or "golf" in vibes or "baseball" in vibes:
        return False
    return True


def filter_venues(
    venues: List[Dict[str, Any]],
    theme: str,
    vibes: List[str],
    category: str,
) -> List[Dict[str, Any]]:
    theme = (theme or "").lower()
    category = (category or "").lower()
    vibes = [v.lower() for v in vibes]

    active_aliases = {"active", "hiking", "gym", "outdoor", "fitness"}
    party_aliases = {"party", "drinks", "dancing"}
    out: List[Dict[str, Any]] = []
    for v in venues:
        if not isinstance(v, dict):
            continue
        if (v.get("category") or "").strip().lower() != category:
            continue
        # Brunch is valid across all themes; for other categories, only
        # apply theme filtering when the venue has explicit themes set.
        venue_themes = [str(x).strip().lower() for x in (v.get("themes") or [])]
        if category != "brunch" and theme and venue_themes and theme not in venue_themes:
            continue
        vv = [x.lower() for x in (v.get("vibes") or [])]
        if vibes:
            def vibe_match(user_v: str, venue_vibes: List[str]) -> bool:
                if user_v in venue_vibes:
                    return True
                if user_v == "active" and any(a in venue_vibes for a in active_aliases):
                    return True
                # Party should behave like "party + drinks + dancing"
                if user_v == "party" and any(a in venue_vibes for a in party_aliases):
                    return True
                return False
            if not any(vibe_match(uv, vv) for uv in vibes):
                continue
        out.append(v)

    return out


def pick_best(candidates: List[Dict[str, Any]], exclude_names: Optional[set] = None) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None
    exclude_names = exclude_names or set()
    for v in candidates:
        if v.get("name") not in exclude_names:
            return v
    return candidates[0]


def pick_best_rotating(
    candidates: List[Dict[str, Any]],
    used_names: set,
    day_index: int,
    last_used_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None
    available = [v for v in candidates if v.get("name") not in used_names]
    if available:
        if last_used_name and len(available) > 1:
            available = [v for v in available if v.get("name") != last_used_name] or available
        return available[day_index % len(available)]
    if last_used_name:
        other = [v for v in candidates if v.get("name") != last_used_name]
        if other:
            return other[day_index % len(other)]
    return candidates[day_index % len(candidates)]


def _time_to_minutes(time_str: str) -> int:
    if not time_str or not isinstance(time_str, str):
        return 0
    time_str = time_str.strip().upper()
    try:
        parts = time_str.replace(".", "").split()
        if len(parts) < 2:
            return 0
        hm = parts[0]
        am_pm = parts[1] if len(parts) > 1 else ""
        if ":" in hm:
            h, m = hm.split(":", 1)
            hour, minute = int(h.strip()), int(m.strip()[:2])
        else:
            hour, minute = int(hm[:2]), 0
        if "PM" in am_pm and hour != 12:
            hour += 12
        elif "AM" in am_pm and hour == 12:
            hour = 0
        return hour * 60 + minute
    except (ValueError, IndexError):
        return 0


def fmt_day(d: date) -> str:
    if hasattr(d, "strftime"):
        try:
            return d.strftime("%a %b %-d")
        except ValueError:
            day_str = d.strftime("%d").lstrip("0") or "0"
            return d.strftime(f"%a %b {day_str}")
    return str(d)


def generate_ical(itinerary: List[Dict[str, Any]]) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//VibeCheck//EN"]
    for s in itinerary:
        if s.get("venue") or s.get("type") == "Transportation":
            day = s.get("day", "")
            time_str = (s.get("time") or "12:00 PM").replace(".", "").strip()
            try:
                dt_str = f"{day} {time_str}"
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
            except Exception:
                dt_obj = datetime.strptime(day + " 12:00", "%Y-%m-%d %H:%M")
            start = dt_obj.strftime("%Y%m%dT%H%M00")
            end_dt = dt_obj + timedelta(hours=1)
            end = end_dt.strftime("%Y%m%dT%H%M00")
            v = s.get("venue") or {}
            name = v.get("name", s.get("type", "Event"))
            desc = s.get("type", "")
            lines.append("BEGIN:VEVENT")
            lines.append(f"DTSTART:{start}")
            lines.append(f"DTEND:{end}")
            lines.append(f"SUMMARY:{name} ({desc})")
            lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def generate_html(itinerary: List[Dict[str, Any]], title: str = "VibeCheck Plan", theme: str = "", day_descriptions: Optional[Dict[str, str]] = None) -> str:
    by_day_iso: Dict[str, List[Dict]] = {}
    for s in itinerary:
        by_day_iso.setdefault(s.get("day", ""), []).append(s)
    for slist in by_day_iso.values():
        slist.sort(key=lambda x: (_time_to_minutes(x.get("time") or ""), x.get("type") or ""))
    day_order = sorted(by_day_iso.keys())
    total_days = len(day_order)
    day_descriptions = day_descriptions or {}

    rows = []
    for day_index, day_iso in enumerate(day_order):
        slots = by_day_iso[day_iso]
        day_label = slots[0].get("day_label", day_iso) if slots else day_iso
        is_arrival = day_index == 0
        is_departure = day_index == total_days - 1
        day_key = f"{theme}_{day_index}"
        desc = day_descriptions.get(day_key)

        if theme == "bachelorette":
            headline, one_liner, _ = bachelorette_day_headline(day_index, is_arrival, is_departure, total_days)
            desc = desc or one_liner
            rows.append(f"<h2>{day_label} — <em>{headline}</em></h2>")
        else:
            if not desc and theme == "spring_training":
                _, desc = _spring_training_day_headline(day_index, is_arrival, is_departure, total_days)
            if not desc and theme == "wmpo":
                _, desc = _wmpo_day_headline(day_index, is_arrival, is_departure, total_days)
            rows.append(f"<h2>{day_label}</h2>")
        if desc:
            desc_html = (desc or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
            rows.append(f"<p class=\"day-intro\">{desc_html}</p>")

        for s in slots:
            v = s.get("venue") or {}
            name = v.get("name", "—")
            rows.append(f"<p><strong>{s.get('time', '')}</strong> {s.get('type', '')}: {name}</p>")
    body = "\n".join(rows)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:sans-serif;max-width:640px;margin:2rem auto;padding:1rem;}} h1{{margin-bottom:0.5rem;}} h2{{margin-top:1.5rem;margin-bottom:0.25rem;}} .day-intro{{margin-top:0;margin-bottom:1rem;opacity:0.9;font-size:0.95rem;}} p{{margin:0.4rem 0;}}</style></head>
<body><h1>{title}</h1>{body}</body></html>"""


def parse_emails(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"[,\n; ]+", text.strip())
    emails = []
    for p in parts:
        if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", p):
            emails.append(p)
    seen = set()
    out = []
    for e in emails:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


# ----------------------------
# Team logos (assets/)
# ----------------------------
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

TEAM_OPTIONS = [
    {"key": "dbacks", "label": "Diamondbacks", "logo": "assets/dbacks.png"},
    {"key": "rockies", "label": "Rockies", "logo": "assets/rockies.png"},
    {"key": "cubs", "label": "Cubs", "logo": "assets/cubs.png"},
    {"key": "as", "label": "A's", "logo": "assets/as.png"},
    {"key": "giants", "label": "SF Giants", "logo": "assets/giants.png"},
]
TEAM_KEY_TO_VENUE_NAMES = {
    "dbacks": ["AZ Diamondbacks"],
    "rockies": ["CO Rockies"],
    "cubs": ["Chicago Cubs"],
    "as": ["A's"],
    "giants": ["SF Giants"],
}


# ----------------------------
# Trip Management & Group Voting
# ----------------------------
def generate_trip_id() -> str:
    """Generate a unique trip ID."""
    return str(uuid.uuid4())[:8]


def get_trips_dir() -> str:
    """Get the directory for storing trip data."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    trips_dir = os.path.join(app_dir, "trips")
    os.makedirs(trips_dir, exist_ok=True)
    return trips_dir


def save_trip(trip_id: str, trip_data: Dict[str, Any]) -> None:
    """Save trip data to a JSON file."""
    trips_dir = get_trips_dir()
    trip_file = os.path.join(trips_dir, f"{trip_id}.json")
    with open(trip_file, "w", encoding="utf-8") as f:
        json.dump(trip_data, f, indent=2, default=str)


def load_trip(trip_id: str) -> Optional[Dict[str, Any]]:
    """Load trip data from a JSON file."""
    trips_dir = get_trips_dir()
    trip_file = os.path.join(trips_dir, f"{trip_id}.json")
    if not os.path.exists(trip_file):
        return None
    try:
        with open(trip_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def create_trip(
    theme: str,
    arrival: date,
    departure: date,
    group_size: int,
    budget_min: int,
    budget_max: int,
    team: str = "cubs",
    trip_name: Optional[str] = None,
) -> str:
    """Create a new trip and return the trip ID."""
    trip_id = generate_trip_id()
    trip_data = {
        "trip_id": trip_id,
        "created_at": datetime.now().isoformat(),
        "theme": theme,
        "arrival": arrival.isoformat(),
        "departure": departure.isoformat(),
        "group_size": group_size,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "team": team,
        "trip_name": trip_name or f"{theme.title()} Trip",
        "votes": [],
        "reconciled_preferences": None,
        "plan_a": None,
        "plan_b": None,
        "selected_plan": None,
    }
    save_trip(trip_id, trip_data)
    return trip_id


def submit_vote(trip_id: str, voter_name: str, vibes: List[str], free_text: Optional[str] = None) -> bool:
    """Submit a vote for a trip. Returns True if successful."""
    trip = load_trip(trip_id)
    if not trip:
        return False
    
    # Check if this voter already voted
    existing_vote_idx = None
    for idx, vote in enumerate(trip.get("votes", [])):
        if vote.get("voter_name", "").strip().lower() == voter_name.strip().lower():
            existing_vote_idx = idx
            break
    
    vote_data = {
        "voter_name": voter_name.strip(),
        "vibes": [v.lower().strip() for v in vibes],
        "free_text": free_text.strip() if free_text else None,
        "submitted_at": datetime.now().isoformat(),
    }
    
    if existing_vote_idx is not None:
        trip["votes"][existing_vote_idx] = vote_data
    else:
        trip.setdefault("votes", []).append(vote_data)
    
    save_trip(trip_id, trip)
    return True


def reconcile_preferences(votes: List[Dict[str, Any]], group_size: int) -> Dict[str, float]:
    """
    Reconcile group votes into a weighted preference profile.
    Returns a dict mapping vibe names to weights (0.0 to 1.0).
    """
    if not votes:
        return {}
    
    # Count votes per vibe
    vibe_counts: Dict[str, int] = {}
    total_voters = len(votes)
    
    for vote in votes:
        vibes = vote.get("vibes", [])
        for vibe in vibes:
            vibe_counts[vibe] = vibe_counts.get(vibe, 0) + 1
    
    # Convert counts to weights (normalize by total voters)
    # Also apply a boost for vibes that appear in multiple votes
    reconciled: Dict[str, float] = {}
    for vibe, count in vibe_counts.items():
        # Base weight: percentage of voters who selected this vibe
        base_weight = count / total_voters
        
        # Boost: if a vibe appears in many votes, it's more important
        # This handles conflicts: if 70% vote "party" and 30% vote "relax",
        # party gets 0.7 weight, relax gets 0.3 weight
        reconciled[vibe] = min(1.0, base_weight * 1.2)  # Slight boost for consensus
    
    # Normalize so top vibes are more prominent
    if reconciled:
        max_weight = max(reconciled.values())
        if max_weight > 0:
            for vibe in reconciled:
                reconciled[vibe] = reconciled[vibe] / max_weight
    
    return reconciled


# Must-have keywords: free text phrase -> internal key
MUST_HAVE_KEYWORDS: Dict[str, List[str]] = {
    "pool": ["pool", "pool day", "must have pool"],
    "spa": ["spa", "spa day", "must have spa"],
    "nice_dinner": ["nice dinner", "fancy dinner", "one nice dinner", "upscale dinner", "fine dining"],
    "golf": ["golf", "tee time", "round of golf"],
    "baseball": ["baseball", "game", "spring training", "ball game"],
    "brunch": ["brunch", "must have brunch"],
}


def extract_must_haves_from_text(text: Optional[str]) -> List[str]:
    """
    Extract must-have preferences from free text (e.g. "must have pool day", "we want spa").
    Returns a list of normalized keys: pool, spa, nice_dinner, golf, baseball, brunch.
    """
    if not text or not str(text).strip():
        return []
    t = str(text).strip().lower()
    found: List[str] = []
    for key, phrases in MUST_HAVE_KEYWORDS.items():
        if any(p in t for p in phrases):
            found.append(key)
    return found


# Trip clusters: theme + area recommendations (e.g. "WMPO + North Scottsdale")
TRIP_CLUSTERS = [
    {"theme": "wmpo", "area": "North Scottsdale", "label": "WMPO + North Scottsdale"},
    {"theme": "wmpo", "area": "Old Town", "label": "WMPO + Old Town"},
    {"theme": "bachelorette", "area": "Old Town", "label": "Bachelorette + Old Town"},
    {"theme": "bachelorette", "area": "North Scottsdale", "label": "Bachelorette + North Scottsdale"},
    {"theme": "spring_training", "area": "Old Town", "label": "Spring Training + Old Town"},
    {"theme": "spring_training", "area": "Talking Stick", "label": "Spring Training + Talking Stick"},
]


def get_recommended_cluster(theme: str, vibes: List[str], venues: List[Dict[str, Any]]) -> Optional[str]:
    """
    Recommend a trip cluster (theme + area) based on theme and vibes.
    Uses venue counts per area for the theme; returns cluster label or None.
    """
    if not theme or not venues:
        return None
    theme_lower = (theme or "").lower()
    area_counts: Dict[str, int] = {}
    for v in venues:
        if not isinstance(v, dict):
            continue
        if theme_lower not in [t.lower() for t in (v.get("themes") or [])]:
            continue
        area = (v.get("area") or "").strip()
        if not area:
            continue
        area_counts[area] = area_counts.get(area, 0) + 1
    if not area_counts:
        return None
    best_area = max(area_counts, key=area_counts.get)
    for c in TRIP_CLUSTERS:
        if c.get("theme", "").lower() == theme_lower and (c.get("area") or "").strip() == best_area:
            return c.get("label")
    return f"{theme.replace('_', ' ').title()} + {best_area}"


def get_must_haves_for_trip() -> List[str]:
    """
    Aggregate must-haves from all votes' free text (and organizer notes).
    Used when building Plan A/B so itineraries respect "must have X".
    """
    trip_id = st.session_state.get("trip_id")
    if not trip_id:
        return []
    trip = load_trip(trip_id)
    if not trip:
        return []
    votes = trip.get("votes", [])
    all_keys: set = set()
    for v in votes:
        for key in extract_must_haves_from_text(v.get("free_text")):
            all_keys.add(key)
    return list(all_keys)


def preferences_to_vibes(preferences: Dict[str, float], max_vibes: int = 3) -> List[str]:
    """
    Convert weighted preferences back to a list of vibes.
    Takes top N vibes by weight.
    """
    if not preferences:
        return []
    
    # Sort by weight (descending) and take top N
    sorted_vibes = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
    return [vibe for vibe, weight in sorted_vibes[:max_vibes]]


def compare_plans(plan_a: List[Dict[str, Any]], plan_b: List[Dict[str, Any]], venues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare Plan A and Plan B to generate trade-off metrics.
    Returns a dict with comparison data.
    """
    def get_venue_price_tier(slot: Dict[str, Any]) -> int:
        venue = slot.get("venue") or {}
        venue_name = venue.get("name", "")
        if not venue_name:
            return 0
        for v in venues:
            if v.get("name") == venue_name:
                return v.get("price_tier", 0)
        return 0
    
    def calculate_avg_price_tier(plan: List[Dict[str, Any]]) -> float:
        price_tiers = [get_venue_price_tier(slot) for slot in plan if slot.get("venue")]
        if not price_tiers:
            return 0.0
        return sum(price_tiers) / len(price_tiers)
    
    def count_venue_types(plan: List[Dict[str, Any]]) -> Dict[str, int]:
        counts = {}
        for slot in plan:
            venue = slot.get("venue") or {}
            category = venue.get("category", "")
            if category:
                counts[category] = counts.get(category, 0) + 1
        return counts
    
    avg_tier_a = calculate_avg_price_tier(plan_a)
    avg_tier_b = calculate_avg_price_tier(plan_b)
    
    venues_a = count_venue_types(plan_a)
    venues_b = count_venue_types(plan_b)
    
    # Estimate budget difference (rough: higher price_tier = higher cost)
    budget_diff_per_person = int((avg_tier_a - avg_tier_b) * 50)  # Rough estimate
    
    return {
        "plan_a_avg_price_tier": round(avg_tier_a, 1),
        "plan_b_avg_price_tier": round(avg_tier_b, 1),
        "budget_difference_per_person": budget_diff_per_person,
        "plan_a_label": "Premium Experience",
        "plan_b_label": "Balanced & Value",
        "key_differences": [
            f"Plan A focuses on higher-end venues (avg tier {avg_tier_a:.1f})",
            f"Plan B balances quality and value (avg tier {avg_tier_b:.1f})",
            f"Estimated difference: ${abs(budget_diff_per_person)}/person" if budget_diff_per_person != 0 else "Similar budget impact",
        ],
    }


def get_active_vibes() -> List[str]:
    """
    Get the active vibes for itinerary generation.
    If trip has reconciled preferences, use those. Otherwise, use organizer's direct selection.
    """
    trip_id = st.session_state.get("trip_id")
    if trip_id:
        trip = load_trip(trip_id)
        if trip and trip.get("reconciled_preferences"):
            reconciled = trip["reconciled_preferences"]
            return preferences_to_vibes(reconciled, max_vibes=3)
    
    # Fall back to organizer's direct selection (backward compatible)
    return st.session_state.get("vibes", [])


# ----------------------------
# Session state
# ----------------------------
def init_state():
    st.session_state.setdefault("page", "welcome")  # "welcome" | "itinerary" | "confirmed"
    st.session_state.setdefault("planning_mode", None)  # "solo" | "group" | None
    st.session_state.setdefault("theme", "spring_training")
    st.session_state.setdefault("vibes", [])
    st.session_state.setdefault("arrival", date.today())
    st.session_state.setdefault("departure", date.today() + timedelta(days=4))
    st.session_state.setdefault("group_size", 6)
    st.session_state.setdefault("budget_min", 600)
    st.session_state.setdefault("budget_max", 1200)

    valid_teams = [t["key"] for t in TEAM_OPTIONS]
    team = st.session_state.get("team", "cubs")
    if team not in valid_teams:
        st.session_state.team = valid_teams[0]
    else:
        st.session_state.setdefault("team", "cubs")

    st.session_state.setdefault("itinerary", [])
    st.session_state.setdefault("slot_status", {})
    st.session_state.setdefault("skipped_slots", set())
    st.session_state.setdefault("swap_choices", {})
    st.session_state.setdefault("emails_text", "")
    st.session_state.setdefault("last_error", "")
    st.session_state.setdefault("plan_paid", False)
    st.session_state.setdefault("enthusiastic_summary", "")
    st.session_state.setdefault("day_descriptions", {})
    st.session_state.setdefault("scroll_itinerary_to_top", False)
    
    # Trip management
    st.session_state.setdefault("trip_id", None)
    st.session_state.setdefault("trip_name", None)
    st.session_state.setdefault("itinerary_plan_a", [])
    st.session_state.setdefault("itinerary_plan_b", [])
    st.session_state.setdefault("selected_plan", None)  # "A", "B", or None
    st.session_state.setdefault("plan_comparison", {})


init_state()


# ----------------------------
# Scroll helper (reliable for Streamlit)
# ----------------------------
def scroll_main_to_top_once(flag_key: str = "scroll_itinerary_to_top"):
    """
    Streamlit's scrollable container is usually section.main.
    We run a few retries because the page height changes as content renders.
    """
    if st.session_state.pop(flag_key, False):
        components.html(
            """
            <script>
              (function() {
                function scrollMain() {
                  const main = window.parent.document.querySelector('section.main');
                  if (main) {
                    main.scrollTo({ top: 0, left: 0, behavior: 'instant' });
                  }
                  window.parent.scrollTo(0,0);
                }
                scrollMain();
                requestAnimationFrame(scrollMain);
                setTimeout(scrollMain, 50);
                setTimeout(scrollMain, 150);
                setTimeout(scrollMain, 300);
              })();
            </script>
            """,
            height=0,
        )


# ----------------------------
# Travel time (distance-based)
# ----------------------------
def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two points in miles (Haversine)."""
    import math
    R = 3959  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _estimate_drive_minutes(miles: float) -> int:
    """Rough drive time in minutes (~25 mph avg in metro area)."""
    if miles <= 0:
        return 0
    mph = 25.0
    return max(5, int(round((miles / mph) * 60)))


def _venue_coords(venue: Optional[Dict[str, Any]]) -> Optional[Tuple[float, float]]:
    """Return (lat, lon) if venue has coordinates."""
    if not venue or not isinstance(venue, dict):
        return None
    lat, lon = venue.get("lat"), venue.get("lon")
    if lat is not None and lon is not None:
        try:
            return (float(lat), float(lon))
        except (TypeError, ValueError):
            pass
    return None


def add_travel_times_to_slots(slots: List[Dict[str, Any]], venues: List[Dict[str, Any]]) -> None:
    """Fill travel_minutes (and from/to names) on transport slots using venue lat/lon."""
    name_to_venue: Dict[str, Dict[str, Any]] = {}
    for v in venues:
        if isinstance(v, dict) and v.get("name"):
            name_to_venue[str(v["name"]).strip()] = v

    for i, slot in enumerate(slots):
        if "Transport" not in (slot.get("type") or ""):
            continue
        prev_slot = slots[i - 1] if i > 0 else None
        next_slot = slots[i + 1] if i < len(slots) - 1 else None
        prev_venue = (prev_slot or {}).get("venue") or {}
        next_venue = (next_slot or {}).get("venue") or {}
        prev_name = prev_venue.get("name") if isinstance(prev_venue, dict) else None
        next_name = next_venue.get("name") if isinstance(next_venue, dict) else None

        # Look up full venue for coords (slot venue may be minimal)
        from_venue = name_to_venue.get(prev_name) if prev_name else prev_venue
        to_venue = name_to_venue.get(next_name) if next_name else next_venue
        from_coords = _venue_coords(from_venue)
        to_coords = _venue_coords(to_venue)

        if from_coords and to_coords:
            miles = _haversine_miles(from_coords[0], from_coords[1], to_coords[0], to_coords[1])
            slot["travel_minutes"] = _estimate_drive_minutes(miles)
            slot["from_venue_name"] = prev_name
            slot["to_venue_name"] = next_name


# ----------------------------
# Itinerary generation
# ----------------------------
def build_itinerary(
    venues: List[Dict[str, Any]],
    theme: str,
    vibes: List[str],
    arrival: date,
    departure: date,
    team: str,
    variant: str = "balanced",  # "premium" or "balanced"
    must_haves: Optional[List[str]] = None,  # from free text: pool, spa, nice_dinner, etc.
) -> List[Dict[str, Any]]:
    if departure <= arrival:
        raise ValueError("Departure date must be after arrival date.")

    days: List[date] = []
    d = arrival
    while d <= departure:
        days.append(d)
        d += timedelta(days=1)

    brunch = filter_venues(venues, theme, vibes, "brunch")
    dining = filter_venues(venues, theme, vibes, "dining")
    nightlife = filter_venues(venues, theme, vibes, "nightlife")
    activities = filter_venues(venues, theme, vibes, "activity")
    transport = filter_venues(venues, theme, vibes, "transport")
    shopping = filter_venues(venues, theme, vibes, "shopping")
    
    # Apply variant preference: premium prefers higher price_tier, balanced prefers mid-range
    def apply_variant_preference(venue_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not venue_list or variant == "balanced":
            return venue_list
        # Premium: sort by price_tier descending (higher tier first)
        # Balanced: keep original order (already filtered by vibes)
        if variant == "premium":
            return sorted(venue_list, key=lambda v: v.get("price_tier", 0), reverse=True)
        return venue_list
    
    brunch = apply_variant_preference(brunch)
    dining = apply_variant_preference(dining)
    nightlife = apply_variant_preference(nightlife)
    activities = apply_variant_preference(activities)

    team_venue_names = TEAM_KEY_TO_VENUE_NAMES.get(team, [])
    baseball_venues = []
    if theme == "spring_training":
        for v in venues:
            if not isinstance(v, dict) or (v.get("category") or "").lower() != "activity":
                continue
            if "baseball" not in (v.get("vibes") or []):
                continue
            if theme not in (v.get("themes") or []):
                continue
            if team_venue_names and not any(tn in (v.get("teams") or []) for tn in team_venue_names):
                continue
            baseball_venues.append(v)
        if not baseball_venues:
            baseball_venues = [
                v for v in venues
                if isinstance(v, dict)
                and "baseball" in (v.get("vibes") or [])
                and (v.get("category") or "").lower() == "activity"
            ]

    if not brunch:
        brunch = [v for v in venues if v.get("category") == "brunch"]
    if not dining:
        dining = [v for v in venues if v.get("category") == "dining"]
    if not nightlife:
        nightlife = [v for v in venues if v.get("category") == "nightlife"]
    if not transport:
        transport = [v for v in venues if v.get("category") == "transport"]

    slots: List[Dict[str, Any]] = []
    slot_id = 0

    used_brunch_names: set = set()
    used_dining_names: set = set()
    used_nightlife_names: set = set()
    used_activity_names: set = set()
    used_golf_names: set = set()
    used_transport_names: set = set()

    last_brunch_name: Optional[str] = None
    last_dining_name: Optional[str] = None
    last_nightlife_name: Optional[str] = None
    last_activity_name: Optional[str] = None
    last_golf_name: Optional[str] = None
    last_transport_name: Optional[str] = None

    # Simple, predictable rotation for transport recommendations so it
    # doesn't always suggest "Party Bus".
    transport_rotation = ["Lyft", "Uber", "Party Bus", "Private SUV"]
    transport_index = 0

    def next_transport_slot() -> Optional[Dict[str, Any]]:
        nonlocal transport_index, last_transport_name
        # If we ever want to return real transport venues from venues.json again,
        # we can fall back to pick_best_rotating here.
        if transport_rotation:
            name = transport_rotation[transport_index % len(transport_rotation)]
            transport_index += 1
            last_transport_name = name
            return {"name": name, "category": "transport"}
        # Fallback to venue-based transport list (not expected for now)
        v = pick_best_rotating(transport, used_transport_names, transport_index, last_used_name=last_transport_name)
        if v:
            used_transport_names.add(v.get("name"))
            last_transport_name = v.get("name")
        return v

    def add_slot(day: date, time_label: str, slot_type: str, venue: Optional[Dict[str, Any]]):
        nonlocal slot_id
        slot_id += 1
        slots.append(
            {
                "id": f"s{slot_id}",
                "day": day.isoformat(),
                "day_label": fmt_day(day),
                "time": time_label,
                "type": slot_type,
                "venue": venue,
            }
        )

    full_days = days[1:-1] if len(days) > 2 else []
    game_times_by_day = ["1:00 PM", "6:00 PM"]  # Day 2 = 1 PM, Day 3 = 6 PM

    must_haves_set = set(must_haves or [])
    placed_nice_dinner = False
    placed_pool = False
    placed_spa = False

    for i, day in enumerate(days):
        is_arrival_day = (day == arrival)
        is_departure_day = (day == departure)
        full_day_index = full_days.index(day) if day in full_days else -1

        if is_arrival_day:
            add_slot(day, "5:30 PM", "Welcome drinks at accommodations", {"name": "At your accommodations", "category": "welcome"})
            # Must-have: one "nice dinner" from free text -> prefer high-tier dining
            if "nice_dinner" in must_haves_set and not placed_nice_dinner:
                high_tier_dining = [v for v in dining if (v.get("price_tier") or 0) >= 3]
                dinner_venue = pick_best_rotating(high_tier_dining or dining, used_dining_names, i, last_used_name=last_dining_name)
                if dinner_venue:
                    placed_nice_dinner = True
            else:
                dinner_venue = pick_best_rotating(dining, used_dining_names, i, last_used_name=last_dining_name)
            if dinner_venue:
                used_dining_names.add(dinner_venue.get("name"))
                last_dining_name = dinner_venue.get("name")

            transport_venue = next_transport_slot()

            add_slot(day, "6:00 PM", "Transportation", transport_venue)
            add_slot(day, "7:30 PM", "Dinner", dinner_venue)

            night_venue = pick_best_rotating(
                nightlife, used_nightlife_names, i, last_used_name=last_nightlife_name
            )
            if night_venue:
                used_nightlife_names.add(night_venue.get("name"))
                last_nightlife_name = night_venue.get("name")
            add_slot(day, "10:15 PM", "Nightlife", night_venue)

            transport_venue2 = next_transport_slot()
            add_slot(day, "11:30 PM", "Transportation", transport_venue2)
            continue

        if is_departure_day:
            brunch_venue = pick_best_rotating(brunch, used_brunch_names, i, last_used_name=last_brunch_name)
            if brunch_venue:
                used_brunch_names.add(brunch_venue.get("name"))
                last_brunch_name = brunch_venue.get("name")
            add_slot(day, "9:00 AM", "Breakfast / Brunch", brunch_venue)

            dep_transport = next_transport_slot()
            add_slot(day, "10:30 AM", "Transportation (departure)", dep_transport)
            continue

        brunch_venue = pick_best_rotating(brunch, used_brunch_names, i, last_used_name=last_brunch_name)
        if brunch_venue:
            used_brunch_names.add(brunch_venue.get("name"))
            last_brunch_name = brunch_venue.get("name")
        add_slot(day, "10:00 AM", "Breakfast / Brunch", brunch_venue)

        transport_am = next_transport_slot()
        add_slot(day, "11:45 AM", "Transportation", transport_am)

        if theme == "spring_training" and baseball_venues and 0 <= full_day_index < len(game_times_by_day):
            game_time = game_times_by_day[full_day_index]
            add_slot(day, game_time, "Baseball Game", pick_best(baseball_venues))
        elif theme == "bachelorette":
            spa_venues = [v for v in venues if isinstance(v, dict) and (v.get("category") or "").lower() == "spa" and theme in (v.get("themes") or [])]
            pool_venues = [v for v in venues if isinstance(v, dict) and (v.get("category") or "").lower() == "pool" and theme in (v.get("themes") or [])]
            shopping_venues = shopping
            # Must-haves from free text: prefer pool or spa on one day if requested
            if "pool" in must_haves_set and not placed_pool and pool_venues:
                act_venue = pick_best(pool_venues, exclude_names=used_activity_names)
                if act_venue:
                    placed_pool = True
                    used_activity_names.add(act_venue.get("name"))
                    last_activity_name = act_venue.get("name")
            elif "spa" in must_haves_set and not placed_spa and spa_venues:
                act_venue = pick_best(spa_venues, exclude_names=used_activity_names)
                if act_venue:
                    placed_spa = True
                    used_activity_names.add(act_venue.get("name"))
                    last_activity_name = act_venue.get("name")
            else:
                act_venue = None
            if not act_venue:
                activity_venues = [v for v in (activities + pool_venues + shopping_venues) if isinstance(v, dict) and _bachelorette_ok_venue(v)]
                if not activity_venues:
                    activity_venues = [{"name": "Hiking", "category": "activity"}, {"name": "Pool Day", "category": "pool"}, {"name": "Shopping at Fashion Square Mall", "category": "shopping"}, {"name": "Rancher Hat Bar", "category": "activity"}]
                act_venue = pick_best_rotating(activity_venues, used_activity_names, i, last_used_name=last_activity_name)
            if act_venue:
                used_activity_names.add(act_venue.get("name"))
                last_activity_name = act_venue.get("name")
            add_slot(day, "12:30 PM", "Activity", act_venue)
        elif theme == "wmpo":
            # WM Phoenix Open theme: ALWAYS prioritize the actual tournament day
            # over golf entertainment venues like PopStroke/Topgolf.
            def _name(vdict: Dict[str, Any]) -> str:
                return str((vdict.get("name") or "")).lower()

            activity_venues = [
                v
                for v in venues
                if isinstance(v, dict)
                and (v.get("category") or "").lower() == "activity"
            ]

            # 1) True WM Phoenix Open tournament experiences (MUST come first).
            tournament_venues = [
                v for v in activity_venues if "wm phoenix open" in _name(v)
            ]

            # 2) Golf / golf-entertainment (Topgolf, PopStroke, Puttshack, etc.).
            golf_entertainment = [
                v
                for v in activity_venues
                if v not in tournament_venues
                and (
                    "golf" in (v.get("vibes") or [])
                    or any(
                        g in _name(v)
                        for g in ("golf", "topgolf", "popstroke", "putt", "puttshack")
                    )
                )
            ]

            # CRITICAL: Always try tournament venues first, only fall back to
            # golf entertainment if all tournament days are already used.
            day_venue = None
            if tournament_venues:
                # Try to pick an unused tournament venue.
                available_tournament = [
                    v for v in tournament_venues if v.get("name") not in used_golf_names
                ]
                if available_tournament:
                    day_venue = available_tournament[i % len(available_tournament)]
                elif tournament_venues:
                    # All tournament venues used, but still prefer tournament over golf entertainment.
                    day_venue = tournament_venues[i % len(tournament_venues)]
            
            # Only if no tournament venues exist or all are exhausted, use golf entertainment.
            if not day_venue and golf_entertainment:
                day_venue = pick_best_rotating(
                    golf_entertainment, used_golf_names, i, last_used_name=last_golf_name
                )
            
            # Final fallback to generic activities.
            if not day_venue:
                day_venue = pick_best(activities)

            if day_venue:
                used_golf_names.add(day_venue.get("name"))
                last_golf_name = day_venue.get("name")

            is_tournament = "wm phoenix open" in _name(day_venue or {})
            slot_label = (
                "WM Phoenix Open — Tournament Day"
                if is_tournament
                else "Golf / WM Phoenix Open Day"
            )
            add_slot(day, "12:30 PM", slot_label, day_venue)
        else:
            add_slot(day, "12:30 PM", "Activity", pick_best(activities))

        # Must-have: one "nice dinner" on a full day if not yet placed
        if "nice_dinner" in must_haves_set and not placed_nice_dinner:
            high_tier_dining = [v for v in dining if (v.get("price_tier") or 0) >= 3]
            dinner_venue = pick_best_rotating(high_tier_dining or dining, used_dining_names, i, last_used_name=last_dining_name)
            if dinner_venue:
                placed_nice_dinner = True
        else:
            dinner_venue = pick_best_rotating(dining, used_dining_names, i, last_used_name=last_dining_name)
        if dinner_venue:
            used_dining_names.add(dinner_venue.get("name"))
            last_dining_name = dinner_venue.get("name")
        add_slot(day, "7:30 PM", "Dinner", dinner_venue)

        night_venue = pick_best_rotating(nightlife, used_nightlife_names, i, last_used_name=last_nightlife_name)
        if night_venue:
            used_nightlife_names.add(night_venue.get("name"))
            last_nightlife_name = night_venue.get("name")
        add_slot(day, "10:15 PM", "Nightlife", night_venue)

        transport_pm = next_transport_slot()
        add_slot(day, "11:30 PM", "Transportation", transport_pm)

    add_travel_times_to_slots(slots, venues)
    return slots


def bachelorette_day_headline(day_index: int, is_arrival: bool, is_departure: bool, total_days: int) -> Tuple[str, str, str]:
    if is_arrival:
        return (
            "We're here — let's get this weekend started",
            "Welcome drinks at the place, then we're hitting dinner and going out. The ultimate Scottsdale weekend starts now.",
            "Your table and experience are ready for the squad.",
        )
    if is_departure:
        return (
            "One last brunch before we head out",
            "Final brunch and one more photo op. Don't forget Old Town or a cactus pic on the way.",
            "One last stop in Old Town or at a cactus garden if you have time.",
        )
    if day_index == 1:
        return (
            "Brunch, pool & bottle service",
            "The full day: brunch, pool or cabana, then dinner and going out. This is what we came for.",
            "Reserve cabana or glam ahead if you want the full vibe.",
        )
    if day_index >= 2:
        return (
            "Recovery & recharge — your pace",
            "Spa or chill time, then dinner and nightlife. We can go hard or take it easy—your call.",
            "Yoga by the pool, ATV, hot air balloon, or wine tasting—on the table if the squad wants it.",
        )
    return ("Your day in Scottsdale", "Brunch, activity, dinner, and nightlife—built for the ultimate weekend.", "")


def _spring_training_day_headline(day_index: int, is_arrival: bool, is_departure: bool, total_days: int) -> Tuple[str, str]:
    if is_arrival:
        return ("Touchdown — let's go", "Welcome to Scottsdale. Check in, then dinner and a night out to start the trip.\nGet some rest — game day is tomorrow.")
    if is_departure:
        return ("One more brunch, then head out", "Final brunch and hit the road.\nSafe travels — see you next spring.")
    if day_index == 1:
        return ("Game day — early game", "Brunch, then head to the ballpark for a 1 PM game.\nAfter the game, dinner and nightlife.")
    if day_index == 2:
        return ("Game day — evening game", "Brunch and activity or rest during the day.\n6 PM game, then dinner and nightlife.")
    return ("Spring Training in Scottsdale", "Brunch, baseball, dinner, and nightlife.\nFull day at the ballpark and around town.")


def _wmpo_day_headline(day_index: int, is_arrival: bool, is_departure: bool, total_days: int) -> Tuple[str, str]:
    if is_arrival:
        return (
            "Arrival — warm up",
            "You’ll roll in, grab dinner, and get ready for golf and the tournament. Think of this as your warm‑up day before the WM Phoenix Open action.",
        )
    if is_departure:
        return (
            "Last round or brunch, then out",
            "You’ll squeeze in one more round or brunch, then head out after an easy morning. Travel day, with one last Scottsdale stop if you want it.",
        )
    if day_index == 1:
        return (
            "Tournament day + Birds Nest",
            "You’ll spend the day at the WM Phoenix Open with on-course food, drinks, cabanas, and party tents, then head to the Coors Light Birds Nest or another concert that night.",
        )
    if day_index == 2:
        return (
            "More WM Phoenix Open action",
            "You’ll be back at the WM Phoenix Open or on the course all day with plenty of food and drinks on-site, then go out for a concert, Birds Nest, or Old Town afterward.",
        )
    return (
        "Golf and Scottsdale",
        "You’ll mix tee times or tournament time with dinners and nightlife around Scottsdale, keeping the WM Phoenix Open energy going.",
    )


def get_day_description(theme: str, day_index: int, is_arrival: bool, is_departure: bool, total_days: int, day_label: str) -> str:
    day_key = f"{theme}_{day_index}"
    cache = st.session_state.get("day_descriptions", {})
    if day_key in cache:
        return cache[day_key]

    if theme == "bachelorette":
        _, one_liner, _ = bachelorette_day_headline(day_index, is_arrival, is_departure, total_days)
        out = one_liner
    elif theme == "spring_training":
        _, one_liner = _spring_training_day_headline(day_index, is_arrival, is_departure, total_days)
        out = one_liner
    elif theme == "wmpo":
        _, one_liner = _wmpo_day_headline(day_index, is_arrival, is_departure, total_days)
        out = one_liner
    else:
        out = "Your day in Scottsdale."

    api_key = os.getenv("OPENAI_API_KEY") or (st.secrets.get("openai", {}) or {}).get("api_key", "")
    if api_key and theme in ("spring_training", "wmpo", "bachelorette"):
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            theme_desc = "Spring Training baseball trip" if theme == "spring_training" else "WM Phoenix Open golf trip" if theme == "wmpo" else "bachelorette weekend"
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You write exactly two short sentences (each under 25 words) describing this upcoming day of a Scottsdale {theme_desc}. No bullet points. Output only two sentences separated by a newline."},
                    {"role": "user", "content": f"Day {day_index + 1} of {total_days}. Arrival: {is_arrival}, Departure: {is_departure}. Current draft: {out}"},
                ],
                max_tokens=120,
            )
            llm_out = (r.choices[0].message.content or "").strip()
            if llm_out:
                out = llm_out
        except Exception:
            pass

    st.session_state.setdefault("day_descriptions", {})[day_key] = out
    return out


def theme_summary(theme: str, vibes: List[str], arrival: date, departure: date, team_label: str) -> str:
    days = (departure - arrival).days + 1
    vibe_txt = ", ".join([v.title() for v in vibes]) if vibes else "Balanced"

    if theme == "spring_training":
        return (
            f"Your {days}-day Scottsdale trip will be a mix of a friends trip and baseball. Spring Training with {vibe_txt}, "
            f"team: {team_label}. Games, dinners, and nightlife—confirm or swap any slot, then lock in tickets and reservations."
        )
    if theme == "bachelorette":
        return (
            f"Your {days}-day Scottsdale bachelorette will be planned for the ultimate weekend. "
            f"Welcome drinks, brunch, pool, spa, dinner, and nightlife will all be lined up so you and the squad can focus on having the best time."
        )
    if theme == "wmpo":
        return (
            f"Your {days}-day Scottsdale trip will be built for the WM Phoenix Open—golf, watching golf, and going out. "
            f"Tee times, dinners, and nightlife will be set up for the crew. Confirm or swap slots, then lock in reservations."
        )
    return (
        f"Your {days}-day Scottsdale trip will be reserved and curated with {vibe_txt}. "
        f"Confirm or swap any slot, then export and invite your group."
    )


def _summary_system_prompt(theme: str) -> str:
    theme = (theme or "").lower()
    highlights_instruction = (
        "Write 2–3 sentences (2–3 lines) that call out the big highlights from the itinerary: "
        "e.g. golf (if present), the baseball game and which team (if present), spa or pool party (if present). "
        "Use the exact team/venue names from the itinerary. No bullet points."
    )
    if theme == "bachelorette":
        return (
            "You are the maid of honor writing an upcoming trip summary for the bachelorette squad. "
            "Tone: fun, excited, warm and inclusive. "
            f"{highlights_instruction}"
        )
    if theme == "wmpo":
        return (
            "You write upcoming trip summaries for a guys trip to the WM Phoenix Open. "
            "Tone: laid-back, not cringe. "
            f"{highlights_instruction}"
        )
    if theme == "spring_training":
        return (
            "You write upcoming trip summaries for a Scottsdale Spring Training trip. "
            "Tone: sports + good times. "
            f"{highlights_instruction}"
        )
    return (
        "You write Scottsdale group trip plan descriptions. Tone: helpful, upbeat. "
        f"{highlights_instruction}"
    )


def generate_enthusiastic_summary(base_summary: str, itinerary_by_day: str, theme: str = "") -> str:
    api_key = os.getenv("OPENAI_API_KEY") or (st.secrets.get("openai", {}) or {}).get("api_key", "")
    if not api_key:
        return base_summary
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        system = _summary_system_prompt(theme)
        user = (
            "Write the upcoming trip summary in the tone described. "
            "Give 2–3 lines with the big highlights: golf, the baseball game (name the team), spa or pool party—using what’s actually in the itinerary.\n\n"
            f"Base context: {base_summary}\n\nItinerary by day:\n{itinerary_by_day}"
        )
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=400,
        )
        text = (r.choices[0].message.content or "").strip()
        return text if text else base_summary
    except Exception:
        return base_summary


# ----------------------------
# UI helpers
# ----------------------------
def team_label_from_key(key: str) -> str:
    for t in TEAM_OPTIONS:
        if t["key"] == key:
            return t["label"]
    return key


def _is_valid_image(path: str) -> bool:
    try:
        from PIL import Image
        with Image.open(path) as img:
            img.load()
        return True
    except Exception:
        return False


def render_team_picker():
    try:
        st.markdown('<div class="section-label">Teams</div>', unsafe_allow_html=True)
        valid_keys = [t["key"] for t in TEAM_OPTIONS]
        if st.session_state.get("team") not in valid_keys:
            st.session_state.team = TEAM_OPTIONS[0]["key"]
        n = len(TEAM_OPTIONS)
        cols = st.columns(n)
        for i, t in enumerate(TEAM_OPTIONS):
            with cols[i]:
                logo_path = os.path.join(_APP_DIR, t["logo"])
                is_selected = st.session_state.team == t["key"]
                
                # --- LOGO & SQUEEZED BUTTON ---
                if os.path.exists(logo_path) and _is_valid_image(logo_path):
                    with open(logo_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                    st.markdown(
                        f'<div style="height: 65px; display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">'
                        f'<img src="data:image/png;base64,{b64}" style="max-height: 100%; max-width: 100%; object-fit: contain;">'
                        f'</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f'<div style="height: 65px; display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><p class="team-label">{t["label"]}</p></div>', unsafe_allow_html=True)
                
                # Use nested columns to naturally squeeze the button width!
                _, btn_col, _ = st.columns([1, 1.5, 1]) # Tightened ratio to match logo width
                with btn_col:
                    if st.button("Select", key=f"team_btn_{i}_{t['key']}", use_container_width=True, type="primary" if is_selected else "secondary"):
                        st.session_state.team = t["key"]
                # -----------------------------

    except Exception as e:
        st.warning(f"Team logos could not load: {e}")
        st.caption("Select team below:")
        cols = st.columns(len(TEAM_OPTIONS))
        for i, t in enumerate(TEAM_OPTIONS):
            with cols[i]:
                is_selected = st.session_state.team == t["key"]
                if st.button(t["label"], key=f"team_fb_{i}_{t['key']}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    st.session_state.team = t["key"]


def swap_alternatives(
    venues: List[Dict[str, Any]],
    theme: str,
    vibes: List[str],
    slot: Dict[str, Any],
    k: int = 2,
) -> List[Dict[str, Any]]:
    venue = slot.get("venue") or {}
    category = ""
    slot_type = slot.get("type", "").lower()
    if "breakfast" in slot_type or "brunch" in slot_type:
        category = "brunch"
    elif "dinner" in slot_type:
        category = "dining"
    elif "nightlife" in slot_type:
        category = "nightlife"
    elif "transport" in slot_type:
        category = "transport"
    else:
        category = "activity"

    # Special handling for WMPO tournament day swaps: include golf entertainment
    # (PopStroke, Topgolf, Puttshack) and actual golf tee times as alternatives.
    is_wmpo_tournament_swap = (
        theme == "wmpo"
        and ("wm phoenix open" in slot_type.lower() or "wm phoenix open" in str((venue.get("name") or "")).lower())
    )

    if is_wmpo_tournament_swap:
        def _name(vdict: Dict[str, Any]) -> str:
            return str((vdict.get("name") or "")).lower()

        # Collect golf-related alternatives:
        # 1) Golf entertainment venues (PopStroke, Topgolf, Puttshack)
        golf_ent = [
            v
            for v in venues
            if isinstance(v, dict)
            and (v.get("category") or "").lower() == "activity"
            and theme in (v.get("themes") or [])
            and (
                "golf" in (v.get("vibes") or [])
                or any(
                    g in _name(v)
                    for g in ("topgolf", "popstroke", "putt", "puttshack")
                )
            )
        ]

        # 2) Actual golf courses (category "golf" or venues with golf tee time vibes)
        golf_courses = [
            v
            for v in venues
            if isinstance(v, dict)
            and (
                (v.get("category") or "").lower() == "golf"
                or (
                    (v.get("category") or "").lower() == "activity"
                    and "golf" in (v.get("vibes") or [])
                    and theme in (v.get("themes") or [])
                    and not any(
                        ent in _name(v)
                        for ent in ("topgolf", "popstroke", "putt", "puttshack")
                    )
                )
            )
        ]

        # Combine: golf entertainment first, then golf courses
        cands = golf_ent + golf_courses
        current_name = (venue.get("name") or "").strip()
        exclude = {current_name} if current_name else set()

        out = []
        for v in cands:
            if v.get("name") in exclude:
                continue
            out.append(v)
            if len(out) >= k:
                break

        # If we still need more options, fall back to generic activity filtering
        if len(out) < k:
            fallback = filter_venues(venues, theme, vibes, "activity")
            for v in fallback:
                if v.get("name") in exclude or v in out:
                    continue
                out.append(v)
                if len(out) >= k:
                    break

        return out

    # Standard swap logic for non-WMPO tournament swaps
    cands = filter_venues(venues, theme, vibes, category)
    if theme == "bachelorette":
        cands = [v for v in cands if _bachelorette_ok_venue(v)]
    current_name = (venue.get("name") or "").strip()
    exclude = {current_name} if current_name else set()

    out = []
    for v in cands:
        if v.get("name") in exclude:
            continue
        out.append(v)
        if len(out) >= k:
            break

    if len(out) < k:
        all_in_category = [
            v
            for v in venues
            if isinstance(v, dict)
            and (v.get("category") or "").strip().lower() == category
        ]
        if theme == "bachelorette":
            all_in_category = [v for v in all_in_category if _bachelorette_ok_venue(v)]
        for v in all_in_category:
            if v.get("name") in exclude or v in out:
                continue
            out.append(v)
            if len(out) >= k:
                break
    return out


def _dedupe_future_venue_occurrences(
    anchor_slot_id: str,
    chosen_venue: Dict[str, Any],
    venues: List[Dict[str, Any]],
    theme: str,
    vibes: List[str],
) -> None:
    """
    After a user locks in a venue (swap+apply or confirm), avoid recommending
    the exact same place again on later days where we still have alternatives.
    """
    try:
        chosen_name = (chosen_venue.get("name") or "").strip()
        if not chosen_name:
            return

        # Don't dedupe transport suggestions – it's fine to see Lyft/Uber, etc.
        cat = (chosen_venue.get("category") or "").strip().lower()
        if cat == "transport":
            return

        itin = st.session_state.itinerary
        anchor_idx = next(
            (idx for idx, sl in enumerate(itin) if sl.get("id") == anchor_slot_id),
            None,
        )
        if anchor_idx is None:
            return

        for j in range(anchor_idx + 1, len(itin)):
            future_slot = itin[j]
            fv = (future_slot.get("venue") or {})
            if (fv.get("name") or "").strip() != chosen_name:
                continue

            # Pick an alternative for the future slot that is *not* the
            # newly chosen venue.
            fut_alts = swap_alternatives(
                venues,
                theme,
                vibes,
                future_slot,
                k=3,
            )
            replacement = next(
                (a for a in fut_alts if (a.get("name") or "").strip() != chosen_name),
                None,
            )
            if replacement:
                future_slot["venue"] = replacement
            else:
                # As a fallback, mark this as an open choice so the user can
                # fill it in themselves.
                future_slot["venue"] = {
                    "name": "Your choice",
                    "category": fv.get("category", ""),
                }
    except Exception:
        # If anything goes wrong, keep the main choice; duplicates are better
        # than breaking the itinerary.
        pass


def _render_one_slot(s: Dict[str, Any], venues: List[Dict[str, Any]], theme: str) -> None:
    sid = s["id"]
    status = st.session_state.slot_status.get(sid, "PENDING")
    v = s.get("venue") or {}
    is_skipped = sid in st.session_state.get("skipped_slots", set())
    vname = "Your choice (skipped)" if is_skipped else v.get("name", "TBD")
    vcat = v.get("category", "")

    # Order matters: WM Phoenix Open days should be treated as activities
    # (ticketed events), even if the label also mentions "Golf".
    if "WM Phoenix Open" in s["type"]:
        slot_category = "activity"
    elif "Baseball" in s["type"]:
        slot_category = "baseball"
    elif "Golf" in s["type"] or "Tee time" in s["type"]:
        slot_category = "golf"
    else:
        slot_category = vcat

    providers = category_reservation_providers(slot_category, vname)
    travel_note = ""
    if (s.get("type") or "").startswith("Transport") and s.get("travel_minutes"):
        from_n = s.get("from_venue_name") or "previous stop"
        to_n = s.get("to_venue_name") or "next stop"
        travel_note = f" ~{s['travel_minutes']} min from {from_n} to {to_n}"

    # Use TOP alignment so the card and buttons line up beautifully
    left, right = st.columns([0.82, 0.18])
    
    with left:
        st.markdown(
            f"""
            <div class="card slot-card" style="margin-top: -14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                <div style="font-size:22px; font-weight:800;">{s["time"]} <span style="opacity:0.8; font-weight:700; margin-left:10px;">{s["type"]}</span></div>
                <div style="padding:6px 12px; border-radius:999px; border:1px solid rgba(255,255,255,0.20); background:rgba(255,255,255,0.06); font-weight:800;">
                  {status}
                </div>
              </div>
              <div style="margin-top:10px; font-size:20px; font-weight:800;">{vname}</div>
              <div style="margin-top:6px; opacity:0.9;">{providers}{travel_note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="slot-actions-wrap">', unsafe_allow_html=True)

        has_swap = bool(st.session_state.swap_choices.get(sid))
        confirm_primary = (status == "CONFIRMED") and not is_skipped
        skip_primary = (status == "SKIPPED") or is_skipped
        swap_primary = has_swap and not confirm_primary and not skip_primary

        c1 = st.button(
            "Confirm",
            key=f"confirm_{sid}",
            use_container_width=True,
            type="primary" if confirm_primary else "secondary",
        )
        c2 = st.button(
            "Swap",
            key=f"swap_{sid}",
            use_container_width=True,
            type="primary" if swap_primary else "secondary",
        )
        c3 = st.button(
            "Skip",
            key=f"skip_{sid}",
            use_container_width=True,
            type="primary" if skip_primary else "secondary",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if c1:
            st.session_state.slot_status[sid] = "CONFIRMED"
            st.session_state.skipped_slots.discard(sid)
            st.session_state.swap_choices.pop(sid, None)

            # When a user confirms this slot, don't recommend the
            # same venue again later in the trip if we can avoid it.
            if not is_skipped and vname not in ("Your choice (skipped)", "Your choice"):
                _dedupe_future_venue_occurrences(
                    sid,
                    v,
                    venues,
                    st.session_state.theme,
                    st.session_state.vibes,
                )

        if c2:
            alts = swap_alternatives(venues, st.session_state.theme, st.session_state.vibes, s, k=2)
            st.session_state.swap_choices[sid] = alts
            st.session_state.slot_status[sid] = "PENDING"
            st.session_state.skipped_slots.discard(sid)

        if c3:
            st.session_state.skipped_slots.add(sid)
            st.session_state.slot_status[sid] = "SKIPPED"
            st.session_state.swap_choices.pop(sid, None)

    alts = st.session_state.swap_choices.get(sid, [])
    if alts:
        with st.expander("Swap options", expanded=True):
            st.markdown(
                '<p style="color:#fff; font-size:16px; font-weight:700; margin-bottom:8px;">Pick one alternative:</p>',
                unsafe_allow_html=True,
            )
            options = [a["name"] for a in alts]
            pick = st.radio("Alternative", options, key=f"swap_pick_{sid}", horizontal=True, label_visibility="collapsed")
            if st.button("Apply swap", key=f"apply_swap_{sid}"):
                chosen = next((a for a in alts if a["name"] == pick), None)
                if chosen:
                    for x in st.session_state.itinerary:
                        if x["id"] == sid:
                            x["venue"] = chosen
                            break
                    # After applying a swap, avoid recommending the same place again
                    # later in the trip (e.g., don't show Boondocks again tomorrow
                    # after swapping to it and confirming it today).
                    _dedupe_future_venue_occurrences(
                        sid,
                        chosen,
                        venues,
                        st.session_state.theme,
                        st.session_state.vibes,
                    )
                st.session_state.swap_choices[sid] = []


def render_itinerary(venues: List[Dict[str, Any]]):
    itin = st.session_state.itinerary
    if not itin:
        st.info("Choose theme, vibes, dates, group size, budget. Then click Generate Itinerary.")
        return

    theme = st.session_state.get("theme", "")
    arrival = st.session_state.get("arrival")
    departure = st.session_state.get("departure")

    if isinstance(arrival, str):
        try:
            arrival = date.fromisoformat(arrival)
        except Exception:
            arrival = date.today()
    if isinstance(departure, str):
        try:
            departure = date.fromisoformat(departure)
        except Exception:
            departure = date.today() + timedelta(days=4)

    by_day_iso: Dict[str, List[Dict[str, Any]]] = {}
    for s in itin:
        by_day_iso.setdefault(s["day"], []).append(s)
    for slist in by_day_iso.values():
        slist.sort(key=lambda x: (_time_to_minutes(x.get("time") or ""), x.get("type") or ""))
    day_order = sorted(by_day_iso.keys())
    total_days = len(day_order)

    for day_index, day_iso in enumerate(day_order):
        slots = by_day_iso[day_iso]
        day_label = slots[0]["day_label"] if slots else day_iso
        is_arrival = (day_iso == arrival.isoformat()) if arrival else (day_index == 0)
        is_departure = (day_iso == departure.isoformat()) if departure else (day_index == total_days - 1)

        if theme == "bachelorette":
            headline, one_liner, optional_tip = bachelorette_day_headline(day_index, is_arrival, is_departure, total_days)
            st.session_state.setdefault("day_descriptions", {})[f"{theme}_{day_index}"] = one_liner
            st.markdown(f"### {day_label} — *{headline}*")
            st.markdown(f"<p style='opacity:0.95; margin-top:-6px; margin-bottom:12px; font-size:15px;'>{one_liner}</p>", unsafe_allow_html=True)
            if optional_tip:
                st.caption(f"💡 {optional_tip}")
        else:
            day_desc = get_day_description(theme, day_index, is_arrival, is_departure, total_days, day_label)
            st.markdown(f"### {day_label}")
            day_desc_html = (day_desc or "").replace("\n", "<br/>")
            st.markdown(f"<p style='opacity:0.95; margin-top:-6px; margin-bottom:12px; font-size:15px;'>{day_desc_html}</p>", unsafe_allow_html=True)
            st.session_state.setdefault("day_descriptions", {})[f"{theme}_{day_index}"] = day_desc

        for s in slots:
            def _make_slot_fragment(slot: Dict[str, Any], vens: List[Dict[str, Any]], th: str):
                @st.fragment
                def _slot():
                    _render_one_slot(slot, vens, th)
                _slot.__name__ = f"itinerary_slot_{slot['id']}"
                return _slot
            _make_slot_fragment(s, venues, theme)()

    if theme == "bachelorette" and itin:
        st.markdown("---")
        st.markdown(
            "<p style='opacity:0.9; font-size:15px;'>Your experience is curated and reserved for your group through our partners and APIs. "
            "Confirm or swap any slot above, then proceed to payment to lock your plan and unlock exports.</p>",
            unsafe_allow_html=True,
        )


# ----------------------------
# Main layout
# ----------------------------
venues = load_venues()
theme = st.session_state.theme

# Check for trip ID in URL query params (for voting links)
query_params = st.query_params
if "trip" in query_params and not st.session_state.get("trip_id"):
    trip_id_from_url = query_params["trip"]
    trip = load_trip(trip_id_from_url)
    if trip:
        st.session_state.trip_id = trip_id_from_url
        st.session_state.page = "vote"
        # Sync trip params to session state
        st.session_state.theme = trip.get("theme", "spring_training")
        st.session_state.arrival = date.fromisoformat(trip.get("arrival", date.today().isoformat()))
        st.session_state.departure = date.fromisoformat(trip.get("departure", (date.today() + timedelta(days=4)).isoformat()))
        st.session_state.group_size = trip.get("group_size", 6)
        st.session_state.budget_min = trip.get("budget_min", 600)
        st.session_state.budget_max = trip.get("budget_max", 1200)
        st.session_state.team = trip.get("team", "cubs")

current_page = st.session_state.get("page", "welcome")
if current_page == "itinerary" and not st.session_state.get("itinerary") and not st.session_state.get("itinerary_plan_a"):
    st.session_state.page = "welcome"
    current_page = "welcome"
if current_page == "confirmed":
    if not st.session_state.get("itinerary") or not st.session_state.get("plan_paid", False):
        st.session_state.page = "itinerary"
        current_page = "itinerary"

THEME_BG = {
    "bachelorette": "radial-gradient(circle at 20% 10%, rgba(255,20,147,0.28), rgba(0,0,0,0) 50%), linear-gradient(180deg, #c71585 0%, #9e0a6a 40%, #6b0848 100%)",
    "wmpo": "radial-gradient(circle at 20% 10%, rgba(34,139,34,0.22), rgba(0,0,0,0) 45%), linear-gradient(180deg, #1a5c3a 0%, #0d3320 50%, #062018 100%)",
}
bg = THEME_BG.get(theme, "radial-gradient(circle at 20% 10%, rgba(255,255,255,0.18), rgba(0,0,0,0) 45%), linear-gradient(180deg, #1a4a8a 0%, #0d3565 50%, #082548 100%)")
st.markdown(f'<style>.stApp {{ background: {bg}; }}</style>', unsafe_allow_html=True)


def _share_link_with_copy(share_link: str, key_suffix: str = "", label: str = "") -> None:
    """Render share link with a copy-to-clipboard icon button. Optional label shown above for alignment."""
    el_id = f"copy-btn-{hash(share_link) % 100000}{key_suffix}".replace("-", "m")
    link_escaped = share_link.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    # Store link in data attribute as base64 to avoid escaping issues
    link_b64 = base64.b64encode(share_link.encode("utf-8")).decode("ascii")
    label_block = f'<div style="color:rgba(255,255,255,0.9); font-size:14px; font-weight:600; margin-bottom:8px;">{label}</div>' if label else ""
    html = f"""
    <div style="margin:0; padding:0; width:100%; box-sizing:border-box;">
        {label_block}
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; width:100%; box-sizing:border-box;">
            <code style="background:rgba(0,0,0,0.2); color:#ffffff; padding:8px 12px; border-radius:6px; font-size:13px; flex:1; min-width:0; word-break:break-all;">{link_escaped}</code>
            <button type="button" id="{el_id}" data-link="{link_b64}" title="Copy link" style="cursor:pointer; background:rgba(255,255,255,0.25); border:1px solid rgba(255,255,255,0.4); border-radius:6px; padding:8px 12px; color:#fff; font-size:14px; flex-shrink:0;">
                &#128203; Copy
            </button>
        </div>
    </div>
    <script>
    (function() {{
        var btn = document.getElementById("{el_id}");
        if (!btn) return;
        var link = atob(btn.getAttribute("data-link"));
        btn.onclick = function() {{
            navigator.clipboard.writeText(link).then(function() {{
                btn.textContent = "Copied!";
                btn.style.color = "#4ade80";
                setTimeout(function() {{ btn.innerHTML = "&#128203; Copy"; btn.style.color = "#fff"; }}, 1500);
            }});
        }};
    }})();
    </script>
    """
    # Height: one row; add a bit if we have a label
    h = 56 if label else 48
    components.html(html, height=h)


# ----------------------------
# Page 1: Welcome
# ----------------------------
if current_page == "welcome":
    render_page_banner(_banner_for_page(theme, "welcome"), "Welcome")
    top_left, top_right = st.columns([0.68, 0.32], vertical_alignment="center")
    with top_left:
        st.markdown('<div class="h1">VibeCheck</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subhead">Scottsdale group trips made effortless. Pick your trip, generate your itinerary, and lock it in.</div>',
            unsafe_allow_html=True,
        )

    with top_right:
        # Demo mode toggle
        demo_mode = st.session_state.get("demo_mode", True)
        if st.checkbox("Demo Mode", value=demo_mode, key="demo_mode_toggle"):
            st.session_state.demo_mode = True
        else:
            st.session_state.demo_mode = False
        
        trip_id = st.session_state.get("trip_id")
        if trip_id:
            trip = load_trip(trip_id)
            if trip:
                vote_count = len(trip.get("votes", []))
                group_size = trip.get("group_size", st.session_state.group_size)
                share_link = f"http://localhost:8502/?trip={trip_id}"
                st.markdown(
                    f'<div class="card" style="text-align:center;"><b>Trip Active</b><br/>'
                    f'{vote_count}/{group_size} votes received<br/>'
                    f'<small>Trip ID: {trip_id}</small></div>',
                    unsafe_allow_html=True,
                )
                if st.button("View Vote Results", key="btn_view_vote_results", use_container_width=True):
                    st.session_state.page = "vote_results"
                    st.rerun()
                st.markdown("**Share link:**")
                _share_link_with_copy(share_link, "sidebar")
            else:
                st.markdown('<div class="card" style="text-align:center;"><b>Demo Mode</b><br/>All features enabled</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="text-align:center;"><b>Demo Mode</b><br/>All features enabled</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Step-by-step instructions
    trip_id = st.session_state.get("trip_id")
    
    if not trip_id:
        # Mode selection FIRST - Solo Trip Planner vs Group Trip Planner
        planning_mode = st.session_state.get("planning_mode", None)
        
        st.markdown(
            '<div style="background:rgba(11,43,90,0.95); color:#ffffff; padding:24px 28px; border-radius:12px; font-size:17px; margin-bottom:20px; border:2px solid rgba(255,255,255,0.3); box-shadow:0 6px 20px rgba(0,0,0,0.3);">'
            '<h3 style="margin:0 0 18px 0; color:#ffffff; font-weight:900; font-size:24px; text-shadow:0 2px 4px rgba(0,0,0,0.3);">Choose Your Planning Mode</h3>'
            '<p style="margin:0 0 16px 0; color:#ffffff; font-weight:700; font-size:17px; line-height:1.6;">Select how you want to plan your trip:</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        
        # Mode selector buttons
        mode_col1, mode_col2 = st.columns(2)
        with mode_col1:
            solo_selected = planning_mode == "solo"
            solo_style = "primary" if solo_selected else "secondary"
            if st.button("🗺️ Solo Trip Planner", key="btn_mode_solo", use_container_width=True, type=solo_style):
                st.session_state.planning_mode = "solo"
                st.rerun()
        with mode_col2:
            group_selected = planning_mode == "group"
            group_style = "primary" if group_selected else "secondary"
            if st.button("👥 Group Trip Planner", key="btn_mode_group", use_container_width=True, type=group_style):
                st.session_state.planning_mode = "group"
                st.rerun()
        
        # Show instructions based on selected mode
        if planning_mode == "solo":
            st.markdown(
                '<div style="background:rgba(11,43,90,0.85); color:#ffffff; padding:20px 24px; border-radius:10px; font-size:16px; margin-bottom:20px; border:2px solid rgba(255,255,255,0.25);">'
                '<h4 style="margin:0 0 12px 0; color:#ffffff; font-weight:800; font-size:20px;">Solo Trip Planning Steps:</h4>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 1:</strong> Choose your theme</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 2:</strong> Select up to 3 vibes</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 3:</strong> Set your travel dates and group size</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 4:</strong> Choose your budget range</p>'
                '<p style="margin:0 0 0 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 5:</strong> Click "Generate Itinerary" to create your plan</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        elif planning_mode == "group":
            st.markdown(
                '<div style="background:rgba(11,43,90,0.85); color:#ffffff; padding:20px 24px; border-radius:10px; font-size:16px; margin-bottom:20px; border:2px solid rgba(255,255,255,0.25);">'
                '<h4 style="margin:0 0 12px 0; color:#ffffff; font-weight:800; font-size:20px;">Group Trip Planning Steps:</h4>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 1:</strong> Choose your theme</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 2:</strong> Select up to 3 vibes (your preferences will count as the first vote)</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 3:</strong> Set your travel dates and group size</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 4:</strong> Choose your budget range</p>'
                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 5:</strong> Click "Create Trip for Group" to start collecting votes</p>'
                '<p style="margin:0 0 0 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 6:</strong> Share the voting link with your group, then generate Plan A/B</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("👆 Please select a planning mode above to continue.")
    else:
        # Trip is active - show status and cancel option
        trip = load_trip(trip_id)
        if trip:
            vote_count = len(trip.get("votes", []))
            group_size = trip.get("group_size", st.session_state.group_size)
            # Keep session in sync with trip for when we generate plans
            st.session_state.theme = trip.get("theme", st.session_state.theme)
            st.session_state.arrival = date.fromisoformat(trip.get("arrival", st.session_state.arrival.isoformat())) if isinstance(trip.get("arrival"), str) else st.session_state.arrival
            st.session_state.departure = date.fromisoformat(trip.get("departure", st.session_state.departure.isoformat())) if isinstance(trip.get("departure"), str) else st.session_state.departure
            st.session_state.group_size = trip.get("group_size", st.session_state.group_size)
            st.session_state.budget_min = trip.get("budget_min", st.session_state.budget_min)
            st.session_state.budget_max = trip.get("budget_max", st.session_state.budget_max)
            st.session_state.team = trip.get("team", st.session_state.team)
            
            trip_status_col1, trip_status_col2 = st.columns([0.85, 0.15])
            with trip_status_col1:
                full_share_link = f"http://localhost:8502/?trip={trip_id}"
                _link_b64 = base64.b64encode(full_share_link.encode("utf-8")).decode("ascii")
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.95); color:#0b2b5a; padding:16px 20px; border-radius:10px; font-size:18px; font-weight:700; margin-bottom:16px; border:1px solid rgba(0,0,0,0.08);">'
                    f'<strong>✓ Trip Active:</strong> {trip.get("trip_name", "Untitled Trip")} | '
                    f'{vote_count}/{group_size} votes received | '
                    f'Share link: <code style="background:rgba(0,0,0,0.06); color:#0b2b5a; padding:4px 8px; border-radius:4px; font-size:17px;">/?trip={trip_id}</code> '
                    f'<a href="#" onclick="navigator.clipboard.writeText(atob(\'{_link_b64}\')); this.textContent=\'Copied!\'; return false;" style="margin-left:6px; color:#0b2b5a; text-decoration:none; font-size:18px;" title="Copy full link">&#128203;</a></div>',
                    unsafe_allow_html=True,
                )
            with trip_status_col2:
                if st.button("Cancel Trip", key="btn_cancel_trip", use_container_width=True, type="secondary"):
                    # Delete trip file
                    trips_dir = get_trips_dir()
                    trip_file = os.path.join(trips_dir, f"{trip_id}.json")
                    if os.path.exists(trip_file):
                        os.remove(trip_file)
                    st.session_state.trip_id = None
                    st.session_state.trip_name = None
                    st.session_state.itinerary_plan_a = []
                    st.session_state.itinerary_plan_b = []
                    st.session_state.selected_plan = None
                    st.success("Trip cancelled. You can now plan solo or create a new group trip.")
                    st.rerun()
            
            # When trip is active: show only vote results + generate — no theme/vibes/dates/budget form
            st.markdown("---")
            st.markdown(
                '<div style="background:rgba(11,43,90,0.9); color:#ffffff; padding:20px 24px; border-radius:10px; font-size:16px; margin-bottom:20px; border:2px solid rgba(255,255,255,0.25);">'
                '<h4 style="margin:0 0 12px 0; color:#fff; font-weight:800;">Next steps</h4>'
                '<p style="margin:0 0 10px 0; color:#fff; font-weight:600;">Share the link above so your group can vote. When you’re ready, view results or generate your two plans.</p>'
                '</div>',
                unsafe_allow_html=True,
            )
            view_col, gen_col = st.columns(2)
            with view_col:
                if st.button("View Vote Results", key="btn_view_results_active", use_container_width=True, type="primary"):
                    st.session_state.page = "vote_results"
                    st.rerun()
            with gen_col:
                share_link = f"http://localhost:8502/?trip={trip_id}"
                _share_link_with_copy(share_link, "gen", label="Share link")
        else:
            st.session_state.trip_id = None

    # Only show theme/vibes/dates/budget when no active trip (so creator doesn’t re-fill the form)
    if not trip_id:
        @st.fragment
        def theme_fragment():
            current_theme = st.session_state.theme
            bg_local = THEME_BG.get(current_theme, "radial-gradient(circle at 20% 10%, rgba(255,255,255,0.18), rgba(0,0,0,0) 45%), linear-gradient(180deg, #1a4a8a 0%, #0d3565 50%, #082548 100%)")
            st.markdown(f'<style>.stApp {{ background: {bg_local}; }}</style>', unsafe_allow_html=True)

            theme_label_map = {
                "spring_training": "Spring Training",
                "bachelorette": "Bachelorette",
                "wmpo": "WM Phoenix Open",
            }
            st.markdown('<div class="section-label">Theme</div>', unsafe_allow_html=True)
            tcol1, tcol2, tcol3 = st.columns(3)

            for idx, (theme_key, theme_label) in enumerate(theme_label_map.items()):
                is_selected = current_theme == theme_key
                label = f"✓ {theme_label}" if is_selected else theme_label
                col = [tcol1, tcol2, tcol3][idx]
                with col:
                    if st.button(label, key=f"theme_{theme_key}", use_container_width=True, type="primary" if is_selected else "secondary"):
                        st.session_state.theme = theme_key
                        st.rerun()

            # Party covers the high-energy going-out vibes and implicitly
            # includes drinks + dancing so we can surface Shopping and Casino
            # as their own top-level vibes.
            vibe_options = [
                "party",
                "relax",
                "balanced",
                "foodie",
                "active",
                "sports",
                "luxury",
                "spa",
                "shopping",
                "casino",
            ]
            # Single source of truth: always read from session state so all selected buttons stay blue
            current_vibes = [v for v in (st.session_state.get("vibes") or []) if v in vibe_options][:3]
            st.session_state.vibes = current_vibes
            st.markdown('<div class="section-label">Pick up to 3 vibes</div>', unsafe_allow_html=True)
            st.caption("Active = hiking, gym, outdoor activities | Casino = nightlife venues with casino gaming")
            num_cols = 5
            vibe_cols = st.columns(num_cols)
            for idx, vibe in enumerate(vibe_options):
                col_idx = idx % num_cols
                with vibe_cols[col_idx]:
                    is_selected = vibe in current_vibes
                    label = f"✓ {vibe.title()}" if is_selected else vibe.title()
                    if st.button(label, key=f"vibe_{vibe}", use_container_width=True, type="primary" if is_selected else "secondary"):
                        next_vibes = list(current_vibes)
                        if vibe in next_vibes:
                            next_vibes.remove(vibe)
                        else:
                            if len(next_vibes) < 3:
                                next_vibes.append(vibe)
                            else:
                                st.session_state.vibe_limit_msg = "Max 3 vibes — deselect one to add another."
                        st.session_state.vibes = next_vibes
                        # Prevent scroll jump
                        st.session_state.scroll_welcome_to_top = False
                        st.rerun()
            selected = st.session_state.vibes[:3]
            if st.session_state.pop("vibe_limit_msg", None):
                st.caption("Max 3 vibes — deselect one to add another.")
            if selected:
                st.caption(f"Selected: {', '.join([v.title() for v in selected])} ({len(selected)}/3)")

            if st.session_state.theme == "spring_training":
                render_team_picker()

        theme_fragment()

        # Cluster recommendation (theme + area) based on venue data
        cluster_rec = get_recommended_cluster(
            st.session_state.theme or "",
            st.session_state.vibes or [],
            venues,
        )
        if cluster_rec:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.12); color:#fff; padding:12px 16px; border-radius:10px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.2); font-weight:700;">'
                f'📍 Recommended for you: {cluster_rec}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-label">Dates</div>', unsafe_allow_html=True)
        arrival = st.date_input("Arrival date", value=st.session_state.arrival)

        if arrival != st.session_state.arrival:
            st.session_state.arrival = arrival
            st.session_state.departure = arrival + timedelta(days=4)

        departure = st.date_input("Departure date", value=st.session_state.departure)
        st.session_state.departure = departure

        st.markdown('<div class="section-label">Group & Budget</div>', unsafe_allow_html=True)
        st.session_state.group_size = st.number_input("Group size (max 10)", min_value=1, max_value=10, value=int(st.session_state.group_size))
        bmin, bmax = st.slider(
            "Budget range per person (trip total)",
            min_value=200,
            max_value=2500,
            value=(int(st.session_state.budget_min), int(st.session_state.budget_max)),
            step=50,
        )
        st.session_state.budget_min, st.session_state.budget_max = bmin, bmax

    # Create Group Trip section - only when no active trip
    planning_mode = st.session_state.get("planning_mode")
    if planning_mode == "group" and not trip_id:
        st.markdown("---")
        st.markdown('<div class="section-label">Create Group Trip</div>', unsafe_allow_html=True)
        
        # Group trip creation options with bold, readable text
        create_mode = st.radio(
            "Invite method",
            ["Create Trip & Share Link", "Invite via Email"],
            horizontal=True,
            key="create_mode",
        )
        
        if create_mode == "Create Trip & Share Link":
            if st.button("Create Trip for Group", key="btn_create_trip", use_container_width=True, type="primary"):
                # Validate that basic info is set
                if not st.session_state.theme:
                    st.warning("Please select a theme first.")
                elif not st.session_state.vibes:
                    st.warning("Please select at least one vibe first.")
                elif st.session_state.group_size < 2:
                    st.warning("Group trips require at least 2 people.")
                else:
                    # Create trip with current settings
                    trip_id = create_trip(
                        theme=st.session_state.theme,
                        arrival=st.session_state.arrival,
                        departure=st.session_state.departure,
                        group_size=st.session_state.group_size,
                        budget_min=st.session_state.budget_min,
                        budget_max=st.session_state.budget_max,
                        team=st.session_state.team,
                    )
                    st.session_state.trip_id = trip_id
                    trip = load_trip(trip_id)
                    if trip:
                        st.session_state.trip_name = trip.get("trip_name")
                        
                        # Automatically submit organizer's vote with their selected theme/vibes
                        organizer_name = "Trip Organizer"
                        organizer_vibes = st.session_state.vibes[:3]  # Use organizer's selected vibes
                        if organizer_vibes:
                            submit_vote(trip_id, organizer_name, organizer_vibes, "Organizer's initial preferences")
                            trip = load_trip(trip_id)  # Reload to get updated vote count
                        
                        # Generate shareable link
                        share_link = f"http://localhost:8502/?trip={trip_id}"
                        vote_count = len(trip.get("votes", []))
                        st.success(f"✅ Trip created! Your preferences have been recorded as the first vote ({vote_count}/{st.session_state.group_size}).")
                        _share_link_with_copy(share_link, "create")
                        
                        # Step-by-step instructions for next steps
                        st.markdown(
                            '<div style="background:rgba(11,43,90,0.95); color:#ffffff; padding:20px 24px; border-radius:10px; font-size:16px; margin-top:16px; border:2px solid rgba(255,255,255,0.3);">'
                            '<h4 style="margin:0 0 12px 0; color:#ffffff; font-weight:800; font-size:18px;">Next Steps:</h4>'
                            '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 1:</strong> Share the voting link above with your group members</p>'
                            '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 2:</strong> Wait for group members to submit their votes</p>'
                            '<p style="margin:0 0 0 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 3:</strong> Once all votes are received, click "Generate Plan A & B" below to create your itinerary options</p>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                    st.rerun()
        else:
            # Email invite mode
            email_input = st.text_area(
                "Group member emails (one per line or comma-separated)",
                placeholder="sarah@email.com\nmike@email.com\njess@email.com",
                height=100,
                key="group_emails_input",
            )
            if st.button("Create Trip & Send Invites", key="btn_create_email", use_container_width=True, type="primary"):
                if not st.session_state.theme:
                    st.warning("Please select a theme first.")
                elif not st.session_state.vibes:
                    st.warning("Please select at least one vibe first.")
                elif st.session_state.group_size < 2:
                    st.warning("Group trips require at least 2 people.")
                elif not email_input or not email_input.strip():
                    st.warning("Please enter at least one email address.")
                else:
                    # Parse emails
                    emails = parse_emails(email_input)
                    if not emails:
                        st.warning("Please enter valid email addresses.")
                    else:
                        # Create trip
                        trip_id = create_trip(
                            theme=st.session_state.theme,
                            arrival=st.session_state.arrival,
                            departure=st.session_state.departure,
                            group_size=st.session_state.group_size,
                            budget_min=st.session_state.budget_min,
                            budget_max=st.session_state.budget_max,
                            team=st.session_state.team,
                        )
                        st.session_state.trip_id = trip_id
                        trip = load_trip(trip_id)
                        if trip:
                            # Automatically submit organizer's vote with their selected theme/vibes
                            organizer_name = "Trip Organizer"
                            organizer_vibes = st.session_state.vibes[:3]  # Use organizer's selected vibes
                            if organizer_vibes:
                                submit_vote(trip_id, organizer_name, organizer_vibes, "Organizer's initial preferences")
                                trip = load_trip(trip_id)  # Reload to get updated vote count
                            
                            # Store emails in trip data
                            trip["invited_emails"] = emails
                            save_trip(trip_id, trip)
                            
                            share_link = f"http://localhost:8502/?trip={trip_id}"
                            vote_count = len(trip.get("votes", []))
                            st.success(f"✅ Trip created! Your preferences recorded ({vote_count}/{st.session_state.group_size}). Invites would be sent to {len(emails)} group member(s).")
                            st.info(f"📧 Demo mode: In production, emails would be sent with voting link: {share_link}")
                            st.code(f"Emails: {', '.join(emails)}", language=None)
                            
                            # Step-by-step instructions for next steps
                            st.markdown(
                                '<div style="background:rgba(11,43,90,0.95); color:#ffffff; padding:20px 24px; border-radius:10px; font-size:16px; margin-top:16px; border:2px solid rgba(255,255,255,0.3);">'
                                '<h4 style="margin:0 0 12px 0; color:#ffffff; font-weight:800; font-size:18px;">Next Steps:</h4>'
                                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 1:</strong> Group members will receive voting links via email</p>'
                                '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 2:</strong> Wait for group members to submit their votes</p>'
                                '<p style="margin:0 0 0 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 3:</strong> Once all votes are received, click "Generate Plan A & B" below to create your itinerary options</p>'
                                '</div>',
                                unsafe_allow_html=True,
                            )
                        st.rerun()

    g1, g2 = st.columns([0.65, 0.35], vertical_alignment="top")
    with g1:
        # Check if we have a trip with votes that need reconciliation
        trip_id = st.session_state.get("trip_id")
        planning_mode = st.session_state.get("planning_mode", "solo" if not trip_id else "group")
        trip = load_trip(trip_id) if trip_id else None
        has_votes = trip and len(trip.get("votes", [])) > 0
        
        # Show appropriate button based on planning mode and trip status
        button_clicked = False
        
        # Only show Generate Itinerary for solo mode (and no active trip)
        if planning_mode == "solo" and not trip_id:
            generate_label = "Generate Itinerary"
            button_clicked = st.button(generate_label, use_container_width=True, type="primary", key="btn_gen_solo")
        # Show Plan A/B generation for group trips
        elif planning_mode == "group" and trip_id:
            vote_count = len(trip.get("votes", []))
            group_size = trip.get("group_size", st.session_state.group_size)
            
            # Show instructions if votes are pending
            if vote_count < group_size:
                st.markdown(
                    '<div style="background:rgba(11,43,90,0.85); color:#ffffff; padding:16px 20px; border-radius:10px; font-size:15px; margin-bottom:16px; border:2px solid rgba(255,255,255,0.25);">'
                    f'<p style="margin:0 0 8px 0; color:#ffffff; font-weight:700; font-size:15px;"><strong>Waiting for Votes:</strong> {vote_count}/{group_size} votes received</p>'
                    '<p style="margin:0 0 0 0; color:#ffffff; font-weight:600; font-size:14px;">Once all group members have voted, click "Generate Plan A & B" below to create your itinerary options.</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            
            generate_label = f"Generate Plan A & B ({vote_count}/{group_size} votes)"
            
            button_clicked = st.button(generate_label, use_container_width=True, type="primary", key="btn_gen_plan_ab")
            if button_clicked and vote_count == 0:
                st.warning("No votes received yet. Share the voting link with your group members first.")
        
        # Only proceed with generation if button was clicked and conditions are met
        if button_clicked and ((planning_mode == "solo" and not trip_id) or (planning_mode == "group" and trip_id and has_votes)):
            try:
                st.session_state.last_error = ""
                st.session_state.swap_choices = {}
                st.session_state.slot_status = {}
                st.session_state.skipped_slots = set()
                st.session_state.enthusiastic_summary = ""
                st.session_state.day_descriptions = {}

                st.session_state.scroll_itinerary_to_top = True

                # Get active vibes (reconciled if trip has votes, otherwise organizer's selection)
                active_vibes = get_active_vibes()
                
                # If trip has votes, reconcile preferences
                if trip_id and has_votes:
                    votes = trip.get("votes", [])
                    group_size = trip.get("group_size", st.session_state.group_size)
                    reconciled = reconcile_preferences(votes, group_size)
                    
                    # Save reconciled preferences to trip
                    trip["reconciled_preferences"] = reconciled
                    save_trip(trip_id, trip)
                    st.session_state.reconciled_preferences = reconciled
                    
                    # Generate Plan A (premium) and Plan B (balanced)
                    must_haves = get_must_haves_for_trip()
                    plan_a = build_itinerary(
                        venues=venues,
                        theme=st.session_state.theme,
                        vibes=active_vibes,
                        arrival=st.session_state.arrival,
                        departure=st.session_state.departure,
                        team=st.session_state.team,
                        variant="premium",
                        must_haves=must_haves,
                    )
                    
                    plan_b = build_itinerary(
                        venues=venues,
                        theme=st.session_state.theme,
                        vibes=active_vibes,
                        arrival=st.session_state.arrival,
                        departure=st.session_state.departure,
                        team=st.session_state.team,
                        variant="balanced",
                        must_haves=must_haves,
                    )
                    
                    st.session_state.itinerary_plan_a = plan_a
                    st.session_state.itinerary_plan_b = plan_b
                    
                    # Calculate comparison metrics
                    st.session_state.plan_comparison = compare_plans(plan_a, plan_b, venues)
                    
                    # Default to Plan A
                    st.session_state.selected_plan = "A"
                    st.session_state.itinerary = plan_a
                else:
                    # Solo organizer: generate single plan (backward compatible)
                    st.session_state.itinerary = build_itinerary(
                        venues=venues,
                        theme=st.session_state.theme,
                        vibes=active_vibes,
                        arrival=st.session_state.arrival,
                        departure=st.session_state.departure,
                        team=st.session_state.team,
                        variant="balanced",
                        must_haves=get_must_haves_for_trip(),
                    )
                    st.session_state.selected_plan = None
                
                st.session_state.page = "itinerary"
                st.rerun()
            except Exception as e:
                st.session_state.last_error = str(e)

    with g2:
        if st.button("Reset", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_state()
            st.session_state.page = "welcome"
            st.rerun()

    if st.session_state.last_error:
        st.markdown(
            f'<div style="background:rgba(220,38,38,0.2); border:2px solid rgba(220,38,38,0.5); border-radius:8px; padding:16px; margin:12px 0; color:#fff; font-size:16px; font-weight:700;">'
            f'⚠️ Error: {st.session_state.last_error}'
            f'</div>',
            unsafe_allow_html=True
        )


# ----------------------------
# Page: Vote (Group Voting)
# ----------------------------
elif current_page == "vote":
    # Prevent scroll jump on vibe selection
    if not st.session_state.get("scroll_vote_to_top", True):
        scroll_main_to_top_once("scroll_vote_to_top")
        st.session_state.scroll_vote_to_top = True
    
    trip_id = st.session_state.get("trip_id")
    if not trip_id:
        st.error("No trip found. Please use a valid voting link.")
        st.session_state.page = "welcome"
        st.rerun()
    
    trip = load_trip(trip_id)
    if not trip:
        st.error("Trip not found.")
        st.session_state.page = "welcome"
        st.rerun()
    
    render_page_banner(_banner_for_page(trip.get("theme", "spring_training"), "welcome"), "Vote on Trip Preferences")
    
    # Back button for organizers (if they're viewing the voting page)
    back_col1, back_col2 = st.columns([0.9, 0.1])
    with back_col1:
        st.markdown('<div class="h1">Vote on Trip Preferences</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="subhead">{trip.get("trip_name", "Group Trip")} — Share your preferences to help plan the perfect trip.</div>',
            unsafe_allow_html=True,
        )
    with back_col2:
        if st.button("← Back", key="btn_back_vote", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()
    
    st.markdown("---")
    
    # Show trip details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Theme:** {trip.get('theme', 'spring_training').replace('_', ' ').title()}")
    with col2:
        arrival_date = date.fromisoformat(trip.get("arrival", date.today().isoformat()))
        departure_date = date.fromisoformat(trip.get("departure", (date.today() + timedelta(days=4)).isoformat()))
        st.markdown(f"**Dates:** {arrival_date.strftime('%b %d')} - {departure_date.strftime('%b %d')}")
    with col3:
        st.markdown(f"**Group Size:** {trip.get('group_size', 6)} people")
    
    st.markdown("---")
    
    # Voting form
    st.markdown('<div class="section-label">Your Preferences</div>', unsafe_allow_html=True)
    
    # Use a unique key that won't conflict with session state modifications
    voter_name = st.text_input("Your name", placeholder="Enter your name", key=f"voter_name_{trip_id}")
    
    vibe_options = [
        "party", "relax", "balanced", "foodie", "active",
        "sports", "luxury", "spa", "shopping", "casino",
    ]
    
    st.markdown('<div class="section-label">Pick up to 3 vibes</div>', unsafe_allow_html=True)
    st.caption("Select the vibes that best describe what you want from this trip. Casino venues appear in nightlife slots.")
    
    selected_vibes = st.session_state.get("vote_vibes", [])
    num_cols = 5
    vibe_cols = st.columns(num_cols)
    for idx, vibe in enumerate(vibe_options):
        col_idx = idx % num_cols
        with vibe_cols[col_idx]:
            is_selected = vibe in selected_vibes
            label = f"✓ {vibe.title()}" if is_selected else vibe.title()
            if st.button(label, key=f"vote_vibe_{vibe}", use_container_width=True, type="primary" if is_selected else "secondary"):
                if vibe in selected_vibes:
                    selected_vibes.remove(vibe)
                else:
                    if len(selected_vibes) < 3:
                        selected_vibes.append(vibe)
                    else:
                        st.warning("Max 3 vibes — deselect one to add another.")
                st.session_state.vote_vibes = selected_vibes
                # Prevent page jump - don't scroll to top on vibe selection
                st.session_state.scroll_vote_to_top = False
                # Use rerun but preserve scroll position
                st.rerun()
    
    if selected_vibes:
        st.caption(f"Selected: {', '.join([v.title() for v in selected_vibes])} ({len(selected_vibes)}/3)")
    
    free_text = st.text_area(
        "Additional preferences (optional)",
        placeholder="E.g., 'Must have pool day', 'Avoid late nights', 'Love Italian food'",
        height=100,
        key="vote_free_text",
    )
    
    st.markdown("---")
    
    if st.button("Submit Vote", key="btn_submit_vote", use_container_width=True, type="primary"):
        if not voter_name or not voter_name.strip():
            st.error("Please enter your name.")
        elif not selected_vibes:
            st.error("Please select at least one vibe.")
        else:
            success = submit_vote(trip_id, voter_name.strip(), selected_vibes, free_text)
            if success:
                st.success(f"Thanks {voter_name}! Your preferences have been recorded.")
                # Clear vote state (don't modify widget state variables that are bound to widgets)
                st.session_state.vote_vibes = []
                # Don't try to clear widget-bound state variables - they'll reset on next render
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Failed to submit vote. Please try again.")
    
    # Show current vote status and results
    votes = trip.get("votes", [])
    if votes:
        st.markdown("---")
        st.markdown(f"**{len(votes)} vote(s) received so far**")
        
        # Show vote results breakdown
        with st.expander("View Vote Results", expanded=False):
            st.markdown("### Individual Votes")
            for vote in votes:
                vibes_str = ', '.join([v.title() for v in vote.get('vibes', [])])
                free_text = vote.get('free_text', '')
                if free_text:
                    st.markdown(f"- **{vote.get('voter_name', 'Anonymous')}**: {vibes_str} | *{free_text}*")
                else:
                    st.markdown(f"- **{vote.get('voter_name', 'Anonymous')}**: {vibes_str}")
            
            # Show reconciled preferences if available
            if trip.get("reconciled_preferences"):
                st.markdown("### Reconciled Preferences (AI Summary)")
                reconciled = trip["reconciled_preferences"]
                sorted_prefs = sorted(reconciled.items(), key=lambda x: x[1], reverse=True)
                for vibe, weight in sorted_prefs:
                    pct = int(weight * 100)
                    st.markdown(f"- **{vibe.title()}**: {pct}% weight")
        
        # Show link to view results as organizer
        if st.button("View Full Results Dashboard", key="btn_view_results", use_container_width=True):
            st.session_state.page = "vote_results"
            st.rerun()


# ----------------------------
# Page: Vote Results Dashboard
# ----------------------------
elif current_page == "vote_results":
    trip_id = st.session_state.get("trip_id")
    if not trip_id:
        st.error("No trip found.")
        st.session_state.page = "welcome"
        st.rerun()
    
    trip = load_trip(trip_id)
    if not trip:
        st.error("Trip not found.")
        st.session_state.page = "welcome"
        st.rerun()
    
    render_page_banner(_banner_for_page(trip.get("theme", "spring_training"), "welcome"), "Vote Results")
    
    back_col1, back_col2 = st.columns([0.9, 0.1])
    with back_col1:
        st.markdown('<div class="h1">Vote Results Dashboard</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="subhead">{trip.get("trip_name", "Group Trip")} — See how your group voted and what the AI reconciled.</div>',
            unsafe_allow_html=True,
        )
    with back_col2:
        if st.button("← Back", key="btn_back_results", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()
    
    st.markdown("---")
    
    votes = trip.get("votes", [])
    vote_count = len(votes)
    group_size = trip.get("group_size", 6)
    
    # Vote status (high contrast for dark background)
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.1); padding:16px; border-radius:8px; border:1px solid rgba(255,255,255,0.2);">'
            f'<div style="color:rgba(255,255,255,0.9); font-size:14px; font-weight:600; margin-bottom:8px;">Votes Received</div>'
            f'<div style="color:#ffffff; font-size:32px; font-weight:800;">{vote_count}/{group_size}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with status_col2:
        if vote_count > 0:
            pct = int((vote_count / group_size) * 100)
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.1); padding:16px; border-radius:8px; border:1px solid rgba(255,255,255,0.2);">'
                f'<div style="color:rgba(255,255,255,0.9); font-size:14px; font-weight:600; margin-bottom:8px;">Response Rate</div>'
                f'<div style="color:#ffffff; font-size:32px; font-weight:800;">{pct}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.1); padding:16px; border-radius:8px; border:1px solid rgba(255,255,255,0.2);">'
                f'<div style="color:rgba(255,255,255,0.9); font-size:14px; font-weight:600; margin-bottom:8px;">Response Rate</div>'
                f'<div style="color:#ffffff; font-size:32px; font-weight:800;">0%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    
    if vote_count == 0:
        st.info("No votes received yet. Share the voting link with your group members.")
    else:
        # Individual votes
        st.markdown("### Individual Votes")
        for idx, vote in enumerate(votes, 1):
            with st.expander(f"Vote #{idx}: {vote.get('voter_name', 'Anonymous')}", expanded=False):
                st.markdown(f"**Vibes:** {', '.join([v.title() for v in vote.get('vibes', [])])}")
                if vote.get('free_text'):
                    st.markdown(f"**Additional Notes:** {vote.get('free_text')}")
                st.caption(f"Submitted: {vote.get('submitted_at', 'Unknown')}")
        
        # Reconciled preferences
        st.markdown("### AI-Reconciled Preferences")
        if trip.get("reconciled_preferences"):
            reconciled = trip["reconciled_preferences"]
            sorted_prefs = sorted(reconciled.items(), key=lambda x: x[1], reverse=True)
            
            st.markdown("The AI analyzed all votes and created this preference profile:")
            for vibe, weight in sorted_prefs:
                pct = int(weight * 100)
                bar_width = pct
                st.markdown(
                    f'<div style="margin:8px 0;">'
                    f'<strong>{vibe.title()}</strong>: {pct}% '
                    f'<div style="background:rgba(255,255,255,0.2); height:8px; border-radius:4px; margin-top:4px;">'
                    f'<div style="background:#0b2b5a; height:100%; width:{bar_width}%; border-radius:4px;"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
            
            active_vibes = preferences_to_vibes(reconciled, max_vibes=3)
            st.info(f"**Active vibes for itinerary:** {', '.join([v.title() for v in active_vibes])}")
        else:
            st.info("Generate Plan A/B to see reconciled preferences.")
        
        # Vibe breakdown chart
        st.markdown("### Vibe Popularity")
        vibe_counts: Dict[str, int] = {}
        for vote in votes:
            for vibe in vote.get("vibes", []):
                vibe_counts[vibe] = vibe_counts.get(vibe, 0) + 1
        
        if vibe_counts:
            sorted_vibes = sorted(vibe_counts.items(), key=lambda x: x[1], reverse=True)
            for vibe, count in sorted_vibes:
                pct = int((count / vote_count) * 100)
                st.markdown(f"- **{vibe.title()}**: {count} vote(s) ({pct}%)")
    
    st.markdown("---")
    
    # Actions
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Generate Plan A & B", key="btn_gen_from_results", use_container_width=True, type="primary"):
            if vote_count == 0:
                st.warning("No votes received yet. Share the voting link with your group members first.")
            else:
                try:
                    # Run generation here and go directly to itinerary page
                    st.session_state.last_error = ""
                    st.session_state.swap_choices = {}
                    st.session_state.slot_status = {}
                    st.session_state.skipped_slots = set()
                    st.session_state.enthusiastic_summary = ""
                    st.session_state.day_descriptions = {}
                    st.session_state.scroll_itinerary_to_top = True

                    votes = trip.get("votes", [])
                    group_size = trip.get("group_size", 6)
                    reconciled = reconcile_preferences(votes, group_size)
                    trip["reconciled_preferences"] = reconciled
                    save_trip(trip_id, trip)
                    st.session_state.reconciled_preferences = reconciled

                    active_vibes = preferences_to_vibes(reconciled, max_vibes=3)
                    must_haves = get_must_haves_for_trip()
                    plan_a = build_itinerary(
                        venues=venues,
                        theme=trip.get("theme", st.session_state.theme),
                        vibes=active_vibes,
                        arrival=date.fromisoformat(trip.get("arrival", st.session_state.arrival.isoformat())),
                        departure=date.fromisoformat(trip.get("departure", st.session_state.departure.isoformat())),
                        team=trip.get("team", st.session_state.team),
                        variant="premium",
                        must_haves=must_haves,
                    )
                    plan_b = build_itinerary(
                        venues=venues,
                        theme=trip.get("theme", st.session_state.theme),
                        vibes=active_vibes,
                        arrival=date.fromisoformat(trip.get("arrival", st.session_state.arrival.isoformat())),
                        departure=date.fromisoformat(trip.get("departure", st.session_state.departure.isoformat())),
                        team=trip.get("team", st.session_state.team),
                        variant="balanced",
                        must_haves=must_haves,
                    )

                    st.session_state.itinerary_plan_a = plan_a
                    st.session_state.itinerary_plan_b = plan_b
                    st.session_state.plan_comparison = compare_plans(plan_a, plan_b, venues)
                    st.session_state.selected_plan = "A"
                    st.session_state.itinerary = plan_a
                    # Sync trip dates/theme/team to session in case we came from vote results only
                    st.session_state.arrival = date.fromisoformat(trip.get("arrival", st.session_state.arrival.isoformat()))
                    st.session_state.departure = date.fromisoformat(trip.get("departure", st.session_state.departure.isoformat()))
                    st.session_state.theme = trip.get("theme", st.session_state.theme)
                    st.session_state.team = trip.get("team", st.session_state.team)

                    st.session_state.page = "itinerary"
                    st.rerun()
                except Exception as e:
                    st.session_state.last_error = str(e)
                    st.error(f"Could not generate plans: {e}")
    with action_col2:
        share_link = f"http://localhost:8502/?trip={trip_id}"
        _share_link_with_copy(share_link, "action", label="Share link")


# ----------------------------
# Page 2: Itinerary
# ----------------------------
elif current_page == "itinerary":
    scroll_main_to_top_once("scroll_itinerary_to_top")
    render_page_banner(_banner_for_page(st.session_state.theme, "itinerary"), "Your itinerary")

    top_row, edit_col = st.columns([0.84, 0.16], vertical_alignment="center")
    with top_row:
        st.markdown('<div class="h1" style="margin:0;">VibeCheck</div>', unsafe_allow_html=True)
        st.markdown('<div class="subhead" style="margin:0;">Confirm or swap slots. Export. Invite. Pay to lock it in.</div>', unsafe_allow_html=True)

    with edit_col:
        if st.button("← Edit Trip", key="btn_edit_trip", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown("---")
    
    # Plan A/B comparison if both plans exist
    plan_a = st.session_state.get("itinerary_plan_a", [])
    plan_b = st.session_state.get("itinerary_plan_b", [])
    selected_plan = st.session_state.get("selected_plan")
    
    if plan_a and plan_b:
        # Step-by-step instructions for Plan A/B selection
        st.markdown(
            '<div style="background:rgba(11,43,90,0.95); color:#ffffff; padding:20px 24px; border-radius:10px; font-size:16px; margin-bottom:20px; border:2px solid rgba(255,255,255,0.3);">'
            '<h4 style="margin:0 0 12px 0; color:#ffffff; font-weight:800; font-size:18px;">Choose Your Plan:</h4>'
            '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 1:</strong> Review Plan A (Premium) and Plan B (Balanced) below</p>'
            '<p style="margin:0 0 10px 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 2:</strong> Click "Select Plan A" for premium venues or "Select Plan B" for balanced value</p>'
            '<p style="margin:0 0 0 0; color:#ffffff; font-weight:700; font-size:16px; line-height:1.6;"><strong>Step 3:</strong> Review your selected itinerary and confirm or swap any venues as needed</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        
        st.markdown("## Compare Plans")
        comparison = st.session_state.get("plan_comparison", {})
        
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.markdown(
                f'<div class="card" style="text-align:center; padding:20px;">'
                f'<h3 style="margin:0 0 10px 0;">Plan A: {comparison.get("plan_a_label", "Premium Experience")}</h3>'
                f'<p style="margin:0; opacity:0.9;">Higher-end venues<br/>Avg tier: {comparison.get("plan_a_avg_price_tier", "N/A")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with comp_col2:
            st.markdown(
                f'<div class="card" style="text-align:center; padding:20px;">'
                f'<h3 style="margin:0 0 10px 0;">Plan B: {comparison.get("plan_b_label", "Balanced & Value")}</h3>'
                f'<p style="margin:0; opacity:0.9;">Balanced quality & value<br/>Avg tier: {comparison.get("plan_b_avg_price_tier", "N/A")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        
        if comparison.get("key_differences"):
            st.markdown("**Key Differences:**")
            for diff in comparison.get("key_differences", []):
                st.markdown(f"- {diff}")
        
        st.markdown("---")
        
        # Plan selection buttons
        sel_col1, sel_col2 = st.columns(2)
        with sel_col1:
            if st.button("Select Plan A", key="select_plan_a", use_container_width=True, type="primary" if selected_plan == "A" else "secondary"):
                st.session_state.selected_plan = "A"
                st.session_state.itinerary = plan_a
                st.rerun()
        with sel_col2:
            if st.button("Select Plan B", key="select_plan_b", use_container_width=True, type="primary" if selected_plan == "B" else "secondary"):
                st.session_state.selected_plan = "B"
                st.session_state.itinerary = plan_b
                st.rerun()
        
        # Set active itinerary based on selected plan
        if selected_plan == "B":
            st.session_state.itinerary = plan_b
        else:
            st.session_state.itinerary = plan_a
        
        st.markdown("---")
    
    # Show instructions if a plan is selected
    if selected_plan and (plan_a or plan_b):
        st.markdown(
            '<div style="background:rgba(11,43,90,0.85); color:#ffffff; padding:16px 20px; border-radius:10px; font-size:15px; margin-bottom:16px; border:2px solid rgba(255,255,255,0.25);">'
            '<p style="margin:0 0 8px 0; color:#ffffff; font-weight:700; font-size:15px;"><strong>✓ Plan {plan} Selected:</strong> Review your itinerary below. You can swap venues or confirm selections to finalize your trip.</p>'
            '</div>'.format(plan=selected_plan),
            unsafe_allow_html=True,
        )
    
    st.markdown("## Your Itinerary")

    team_lbl = team_label_from_key(st.session_state.team)
    active_vibes = get_active_vibes()
    base_summary = theme_summary(
        st.session_state.theme, active_vibes,
        st.session_state.arrival, st.session_state.departure, team_lbl,
    )

    if st.session_state.itinerary and not st.session_state.get("enthusiastic_summary"):
        by_day: Dict[str, List[Dict]] = {}
        for s in st.session_state.itinerary:
            by_day.setdefault(s.get("day", ""), []).append(s)
        lines = []
        for day_iso in sorted(by_day.keys()):
            slots = by_day[day_iso]
            day_label = slots[0].get("day_label", day_iso) if slots else day_iso
            parts = [f"{s.get('time', '')} {s.get('type', '')}: {(s.get('venue') or {}).get('name', 'TBD')}" for s in slots]
            lines.append(f"{day_label}: " + " | ".join(parts))
        itinerary_by_day = "\n".join(lines)
        st.session_state.enthusiastic_summary = generate_enthusiastic_summary(
            base_summary, itinerary_by_day, theme=st.session_state.get("theme", "")
        )

    display_summary = st.session_state.get("enthusiastic_summary") or base_summary
    st.markdown(f"<div class='card'>{display_summary}</div>", unsafe_allow_html=True)
    st.markdown("")

    @st.fragment
    def itinerary_slots_fragment():
        render_itinerary(venues)

    itinerary_slots_fragment()

    st.markdown("---")
    ex_col, inv_col = st.columns([0.52, 0.48], gap="large")

    @st.fragment
    def confirm_and_export_fragment():
        st.markdown("## Confirm Plan")
        plan_paid = st.session_state.get("plan_paid", False)
        stripe_link = get_stripe_payment_link()
        all_confirmed = bool(st.session_state.itinerary) and all(
            st.session_state.slot_status.get(s["id"], "PENDING") in ("CONFIRMED", "SKIPPED")
            for s in st.session_state.itinerary
        )
        if all_confirmed:
            st.success("All slots confirmed. Proceed to payment to lock the plan and unlock exports.")
        else:
            st.info("Confirm each slot (or swap), then proceed to payment to lock the plan.")

        if stripe_link:
            st.link_button("Confirm Plan — Pay to lock ($99)", stripe_link, use_container_width=False)
            st.caption("After paying, you'll be taken to your confirmed trip page to export. Test: use Stripe demo card 4242 4242 4242 4242.")
            if st.button("I have Paid (Unlock Exports)", key="demo_paid_btn"):
                st.session_state.plan_paid = True
                st.session_state.page = "confirmed"
                st.session_state.scroll_confirmed_to_top = True
                st.rerun()
        else:
            st.warning("Stripe payment link not configured. Add it in .streamlit/secrets.toml or set env var VIBECHECK_STRIPE_PAYMENT_LINK.")
            st.code(
                """# vibecheck/.streamlit/secrets.toml
[stripe]
payment_link = "https://buy.stripe.com/test_..." """,
                language="toml",
            )

        if plan_paid:
            if st.button("View confirmed trip →", key="btn_view_confirmed", use_container_width=True, type="primary"):
                st.session_state.page = "confirmed"
                st.session_state.scroll_confirmed_to_top = True
                st.rerun()
            st.caption("Export and full summary are on the confirmed trip page.")
            st.markdown("### Reservation details (mock)")
            st.caption("Replace with real APIs in production (OpenTable, Resy, Riot House VIP, GolfNow, etc.).")
            h = abs(hash(str(st.session_state.itinerary)[:50]))
            st.code("OpenTable: OT-MOCK-" + str(h)[:8])
            st.code("Resy: RS-MOCK-" + str(h)[-8:])
            st.code("Riot House VIP: RH-VIP-" + str(h % 100000))
            st.code("GolfNow Tee Time: GN-" + str(h % 10000))
            st.code("Spa: SPA-" + str(h)[:6])
            st.code("Pool / Daybed: POOL-" + str(h)[-6:])

    with ex_col:
        confirm_and_export_fragment()

    @st.fragment
    def invite_fragment():
        st.markdown("## Invite Attendees")
        st.markdown(
            "<p style=\"color:#fff; font-size:15px; font-weight:700; line-height:1.5;\">Add up to 10 emails (comma or newline separated). We'll send a draft invite link once you're ready.</p>",
            unsafe_allow_html=True,
        )
        st.session_state.emails_text = st.text_area(
            "Emails",
            value=st.session_state.emails_text,
            height=120,
            placeholder="alex@email.com, sam@email.com",
            label_visibility="collapsed",
        )
        emails = parse_emails(st.session_state.emails_text)[:10]
        st.caption(f"Valid emails: {len(emails)} / 10")
        if emails:
            if st.button("Send draft invite (demo)", key="invite_demo_btn", use_container_width=True):
                st.session_state.invite_demo_sent = True
            if st.session_state.get("invite_demo_sent"):
                st.success(f"Draft invite link sent to {len(emails)} attendee(s). (Demo — no email actually sent.)")
                st.caption("In production, we'd email a link to view and confirm the plan.")
        else:
            st.caption("Enter at least one valid email to demo the invite.")

    with inv_col:
        invite_fragment()

elif current_page == "confirmed":
    scroll_main_to_top_once("scroll_confirmed_to_top")
    render_page_banner(_banner_for_page(st.session_state.theme, "itinerary"), "Your confirmed trip")

    top_row, back_col = st.columns([0.84, 0.16], vertical_alignment="center")
    with top_row:
        st.markdown('<div class="h1" style="margin:0;">Trip locked</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subhead" style="margin:0;">Your confirmed itinerary, theme, vibes, and write-up. Export or share below.</div>',
            unsafe_allow_html=True,
        )
    with back_col:
        if st.button("← Back to itinerary", key="btn_back_from_confirmed", use_container_width=True):
            st.session_state.page = "itinerary"
            st.rerun()

    st.markdown("---")

    theme = st.session_state.get("theme", "spring_training")
    theme_labels = {"spring_training": "Spring Training", "bachelorette": "Bachelorette", "wmpo": "WM Phoenix Open"}
    theme_label = theme_labels.get(theme, theme.replace("_", " ").title())
    active_vibes = get_active_vibes()
    vibe_text = ", ".join(v.title() for v in active_vibes) if active_vibes else "—"
    trip_id = st.session_state.get("trip_id")
    group_note = " (based on group preferences)" if trip_id else ""

    st.markdown(
        f'<div style="background:rgba(255,255,255,0.12); color:#fff; padding:16px 20px; border-radius:10px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.25);">'
        f'<div style="font-size:14px; font-weight:700; margin-bottom:6px;">Theme & vibes</div>'
        f'<div style="font-size:18px; font-weight:800;">{theme_label} • {vibe_text}{group_note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    write_up = st.session_state.get("enthusiastic_summary", "")
    if write_up:
        st.markdown("## Trip summary")
        st.markdown(f"<div class='card'>{write_up}</div>", unsafe_allow_html=True)
        st.markdown("")

    itin = st.session_state.get("itinerary", [])
    if itin:
        by_day_iso: Dict[str, List[Dict[str, Any]]] = {}
        for s in itin:
            by_day_iso.setdefault(s.get("day", ""), []).append(s)
        for slist in by_day_iso.values():
            slist.sort(key=lambda x: (_time_to_minutes(x.get("time") or ""), x.get("type") or ""))
        day_order = sorted(by_day_iso.keys())
        day_descriptions = st.session_state.get("day_descriptions", {})

        st.markdown("## Your itinerary")
        for day_index, day_iso in enumerate(day_order):
            slots = by_day_iso[day_iso]
            day_label = slots[0].get("day_label", day_iso) if slots else day_iso
            day_key = f"{theme}_{day_index}"
            day_desc = day_descriptions.get(day_key)
            st.markdown(f"### {day_label}")
            if day_desc:
                day_desc_html = (day_desc or "").replace("\n", "<br/>")
                st.markdown(f"<p style='opacity:0.95; margin-top:-6px; margin-bottom:12px; font-size:15px;'>{day_desc_html}</p>", unsafe_allow_html=True)
            for s in slots:
                v = s.get("venue") or {}
                name = v.get("name", "TBD")
                time_str = s.get("time", "")
                slot_type = s.get("type", "")
                travel = (s.get("travel_note") or "").strip()
                line = f"**{time_str}** {slot_type}: {name}"
                if travel:
                    line += f"  \n_{travel}_"
                st.markdown(line)

    st.markdown("---")
    st.markdown("## Export")
    st.markdown("Download your plan to add to your calendar or print.")
    ical_data = generate_ical(itin)
    html_data = generate_html(
        itin,
        theme=st.session_state.get("theme", ""),
        day_descriptions=st.session_state.get("day_descriptions", {}),
    )
    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button("Download iCal (.ics)", data=ical_data, mime="text/calendar", file_name="vibecheck_plan.ics", key="dl_ical_confirmed", use_container_width=True)
    with dl2:
        st.download_button("Download HTML (Print to PDF)", data=html_data, mime="text/html", file_name="vibecheck_plan.html", key="dl_html_confirmed", use_container_width=True)
    with dl3:
        st.download_button("Save as PDF (open HTML, then Print → Save as PDF)", data=html_data, mime="text/html", file_name="vibecheck_plan_print.html", key="dl_pdf_confirmed", use_container_width=True)
    st.caption("Open the HTML file in a browser, then File → Print → Save as PDF.")
