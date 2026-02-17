import os
import json
import re
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

/* Cards – brighter */
.card {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
}

/* -------------------------------------------------------
   BUTTON UX: easier clicks + hover darken + selected stays dark
   ------------------------------------------------------- */

/* Base: make buttons easier to click everywhere */
.stButton > button,
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] a {
  min-height: 44px !important;
  padding: 0.70rem 1.10rem !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  touch-action: manipulation !important;
  transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease !important;
}

/* Default "secondary" look: light background, dark text */
.stButton > button {
  color: #0b2b5a !important;
  background-color: rgba(255,255,255,0.92) !important;
  border: 2px solid rgba(255,255,255,0.35) !important;
}

/* Hover: always darken blue (what you asked for) */
.stButton > button:hover {
  background-color: #1e3a5f !important;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.55) !important;
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

/* Hover on selected: slightly lighter dark blue */
[data-testid="stBaseButton-primary"] button:hover,
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
  background-color: #1e3a5f !important;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.70) !important;
}

/* Prevent text wrapping on vibe buttons */
.stButton > button {
  white-space: nowrap !important;
}

/* Team logo clickable */
.teamLogo {
  cursor: pointer;
  transition: opacity 0.2s;
  border-radius: 8px;
  padding: 4px;
}
.teamLogo:hover {
  opacity: 0.8;
  background: rgba(255,255,255,0.05);
}
.teamLogo.selected {
  background: rgba(255,255,255,0.12);
  border: 2px solid rgba(255,255,255,0.3);
}

/* Team picker: keep your existing layout rules (left as-is) */
[data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(5)) {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 6px !important;
  overflow-x: auto !important;
  padding-bottom: 4px !important;
  align-items: stretch !important;
}
[data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(5)) [data-testid="column"] {
  flex: 1 1 0% !important;
  min-width: 80
