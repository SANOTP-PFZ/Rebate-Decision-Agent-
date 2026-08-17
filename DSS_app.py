import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import dataiku
import base64

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Rebate Decision Agent",
    layout="wide",
    initial_sidebar_state="auto"
)

# =============================================================================
# PFIZER BRAND COLORS (aligned with Migraine Intelligence Hub palette)
# =============================================================================
PFZ_BLUE = '#3B6FD9'
PFZ_DARK_BLUE = '#0A1A3D'
PFZ_NAVY_700 = '#163990'
PFZ_NAVY_600 = '#1C4FC0'
PFZ_ACCENT = '#41B6E6'
PFZ_RED = '#EF4444'
PFZ_ORANGE = '#F59E0B'
PFZ_GREEN = '#10B981'
PFZ_GRAY = '#64748B'
PFZ_WHITE = '#FFFFFF'
PFZ_BG = '#EEF3FB'
PFZ_SURFACE = '#FFFFFF'

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --navy-900: #0A1A3D;
        --navy-800: #102A5C;
        --navy-700: #163990;
        --navy-600: #1C4FC0;
        --navy-500: #3B6FD9;
        --accent: #41B6E6;
        --bg: #EEF3FB;
        --surface: #FFFFFF;
        --surface-2: #F8FAFD;
        --text: #0F172A;
        --text-muted: #64748B;
        --text-soft: #475569;
        --hairline: rgba(15,23,42,0.08);
        --up: #10B981;
        --down: #EF4444;
        --shadow-sm: 0 2px 8px rgba(15,23,42,0.05), 0 1px 2px rgba(15,23,42,0.04);
        --shadow-md: 0 6px 16px rgba(15,23,42,0.07), 0 2px 4px rgba(15,23,42,0.04);
        --shadow-lg: 0 18px 40px rgba(15,23,42,0.10), 0 6px 12px rgba(15,23,42,0.06);
        --panel-radius: 18px;
        --ease: cubic-bezier(0.4, 0, 0.2, 1);
        --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
            var(--bg) !important;
    }

    /* Fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main .block-container {
        animation: fadeIn 0.35s var(--ease-out);
    }

    /* Header */
    .pfizer-header {
        background: rgba(255,255,255,0.62);
        backdrop-filter: saturate(180%) blur(22px);
        -webkit-backdrop-filter: saturate(180%) blur(22px);
        padding: 14px 24px;
        display: flex;
        align-items: center;
        gap: 18px;
        border-radius: 14px;
        margin-bottom: 1.4rem;
        border: 1px solid var(--hairline);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    .pfizer-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--navy-600), var(--accent), var(--navy-500));
        opacity: 0.7;
    }
    .pfizer-logo {
        display: flex;
        align-items: center;
        border-right: 1px solid var(--hairline);
        padding-right: 18px;
    }
    .pfizer-logo img {
        height: 30px;
        object-fit: contain;
    }
    .pfizer-header h1 {
        color: var(--navy-900);
        font-family: 'Manrope', sans-serif;
        font-size: 20px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    /* Landing page */
    .greeting {
        font-family: 'Manrope', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--navy-900);
        text-align: center;
        margin: 48px 0 8px 0;
        letter-spacing: -0.025em;
    }
    .disclaimer-box {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 28px 36px;
        border: 1px solid var(--hairline);
        box-shadow: var(--shadow-md);
        max-width: 700px;
        margin: 24px auto 36px auto;
    }
    .disclaimer-box h3 {
        font-family: 'Manrope', sans-serif;
        color: var(--navy-900);
        font-size: 14px;
        font-weight: 700;
        margin: 0 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--accent);
    }
    .disclaimer-box p, .disclaimer-box li {
        color: var(--text-soft);
        font-size: 12.5px;
        line-height: 1.7;
        font-family: 'Inter', sans-serif;
    }
    .disclaimer-box ul {
        padding-left: 18px;
        margin: 8px 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.62) !important;
        backdrop-filter: saturate(180%) blur(22px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(22px) !important;
        width: 320px !important;
        border-right: 1px solid var(--hairline) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    section[data-testid="stSidebar"] label {
        color: var(--navy-900) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: rgba(255,255,255,0.8) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {
        color: var(--navy-900) !important;
        font-family: 'Inter', sans-serif !important;
    }
    section[data-testid="stSidebar"] .stSelectbox svg {
        fill: var(--navy-600) !important;
    }

    /* Selectbox dropdown menu (listbox) */
    [data-baseweb="popover"] {
        background-color: white !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow-lg) !important;
    }
    [data-baseweb="popover"] ul {
        background-color: white !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] [role="option"] {
        background-color: white !important;
        color: var(--navy-900) !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] [role="option"]:hover,
    [data-baseweb="menu"] [role="option"][aria-selected="true"] {
        background-color: rgba(28,79,192,0.06) !important;
        color: var(--navy-700) !important;
    }
    [data-baseweb="select"] [data-baseweb="tag"] {
        background-color: rgba(28,79,192,0.08) !important;
        color: var(--navy-900) !important;
    }
    /* Selectbox placeholder text */
    [data-baseweb="select"] [data-baseweb="select"] span[aria-live="polite"] {
        color: var(--text-muted) !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white !important;
        color: var(--navy-900) !important;
    }
    .stSelectbox [data-baseweb="select"] input {
        color: var(--navy-900) !important;
        -webkit-text-fill-color: var(--navy-900) !important;
    }
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: var(--surface-2) !important;
        color: var(--navy-900) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 10px !important;
        -webkit-text-fill-color: var(--navy-900) !important;
        opacity: 1 !important;
        font-family: 'Inter', sans-serif !important;
    }
    section[data-testid="stSidebar"] .stTextInput input:disabled {
        background-color: rgba(28,79,192,0.05) !important;
        color: var(--navy-900) !important;
        -webkit-text-fill-color: var(--navy-900) !important;
        opacity: 1 !important;
        font-weight: 600 !important;
        border: 1px solid rgba(28,79,192,0.15) !important;
    }
    /* Global disabled text input override */
    .stTextInput input,
    .stTextInput input:disabled,
    .stTextInput [data-baseweb="input"] input,
    .stTextInput [data-baseweb="base-input"] input {
        background-color: white !important;
        color: var(--navy-900) !important;
        -webkit-text-fill-color: var(--navy-900) !important;
        opacity: 1 !important;
    }
    .stTextInput [data-baseweb="input"],
    .stTextInput [data-baseweb="base-input"] {
        background-color: white !important;
    }
    .stTextInput input:disabled,
    .stTextInput [data-baseweb="input"]:has(input:disabled),
    .stTextInput [data-baseweb="base-input"]:has(input:disabled) {
        background-color: rgba(28,79,192,0.05) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, var(--navy-600), var(--navy-500)) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.25s var(--ease) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, var(--navy-700), var(--navy-600)) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .sidebar-header {
        font-family: 'Manrope', sans-serif;
        color: var(--navy-900);
        font-size: 13px;
        font-weight: 700;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--accent);
        margin-bottom: 12px;
        letter-spacing: -0.01em;
        text-transform: uppercase;
    }
    .scenario-box {
        background: rgba(28,79,192,0.04);
        border: 1px solid rgba(28,79,192,0.12);
        border-left: 3px solid var(--navy-600);
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 16px;
        transition: all 0.25s var(--ease);
    }
    .scenario-box:hover {
        background: rgba(28,79,192,0.06);
        border-color: rgba(28,79,192,0.2);
    }
    .scenario-box h4 {
        font-family: 'Manrope', sans-serif;
        color: var(--navy-900); margin: 0 0 8px 0;
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.06em;
    }
    .scenario-box p {
        color: var(--text-soft); font-size: 11.5px; margin: 3px 0;
        font-family: 'Inter', sans-serif;
    }

    /* Metric cards */
    .metric-card {
        background: var(--surface);
        border-radius: 14px;
        padding: 20px 14px;
        text-align: center;
        border: 1px solid var(--hairline);
        border-left: none;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: var(--accent);
        border-radius: 0 4px 4px 0;
    }
    .metric-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-3px);
    }
    .metric-card .label {
        font-family: 'Inter', sans-serif;
        font-size: 10.5px; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.06em;
        margin-bottom: 10px; font-weight: 500;
    }
    .metric-card .value {
        font-family: 'Manrope', sans-serif;
        font-size: 1.5rem; font-weight: 700;
        letter-spacing: -0.02em;
        font-variant-numeric: tabular-nums;
    }
    .metric-card .value.negative { color: var(--down); }
    .metric-card .value.positive { color: var(--navy-900); }
    .metric-card .value.accent { color: var(--navy-600); }
    .metric-card.border-negative::before { background: var(--down); }
    .metric-card.border-positive::before { background: linear-gradient(180deg, var(--navy-600), var(--accent)); }
    .metric-card.border-accent::before { background: var(--accent); }

    .impact-header {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        color: var(--navy-900);
        padding: 12px 16px;
        border-radius: 12px;
        text-align: center;
        font-family: 'Manrope', sans-serif;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin: 12px 0 16px 0;
        border: 1px solid var(--hairline);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    .impact-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--navy-600), var(--accent));
    }

    .section-divider {
        border: none;
        border-top: 1px solid var(--hairline);
        margin: 28px 0 20px 0;
    }

    /* Chart title */
    .chart-title {
        font-family: 'Manrope', sans-serif;
        font-size: 14px;
        font-weight: 700;
        color: var(--navy-900);
        margin: 0 0 6px 0;
        padding-left: 4px;
        letter-spacing: -0.01em;
    }

    /* Primary buttons (landing page) */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, var(--navy-600), var(--navy-500)) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.25s var(--ease) !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, var(--navy-700), var(--navy-600)) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background: rgba(255,255,255,0.8) !important;
        color: var(--navy-900) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.25s var(--ease) !important;
    }
    .stButton > button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background: rgba(255,255,255,1) !important;
        border-color: rgba(28,79,192,0.25) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    /* Dataframe / table styling */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--hairline);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stTable"] table {
        background: white !important;
        width: 100%;
        border-collapse: collapse;
    }
    [data-testid="stTable"] th {
        background: var(--navy-900) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        text-align: left !important;
    }
    [data-testid="stTable"] td {
        background: white !important;
        color: #0F172A !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        padding: 8px 14px !important;
        border-bottom: 1px solid rgba(15,23,42,0.06) !important;
    }
    [data-testid="stTable"] tr:hover td {
        background: rgba(28,79,192,0.03) !important;
    }
    /* Also handle stDataFrame canvas-based fallback */
    [data-testid="stDataFrame"] th {
        background: var(--navy-900) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stDataFrame"] td {
        background: white !important;
        color: #0F172A !important;
    }
    [data-testid="stDataFrame"] table {
        background: white !important;
    }

    /* Info box */
    .stAlert {
        background: rgba(28,79,192,0.04) !important;
        border: 1px solid rgba(28,79,192,0.12) !important;
        border-radius: 12px !important;
        color: var(--navy-900) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* =====================================================================
       AGENT PAGE — design token cheatsheet
       ---------------------------------------------------------------------
       Space scale : 8  / 12 / 16 / 24 / 32 / 48 px
       Radii       : 10 (chip) / 14 (card) / 18 (panel)
       Shadow      : var(--shadow-sm | --shadow-md | --shadow-lg)
       Type        : 10 micro | 11 label | 12 body | 13 body+ | 14 kpi-label
                     18 chart-title | 26 kpi-value | 34 page-title
       Fonts       : Manrope (headings, KPI values), Inter (body/UI)
       All new agent-page classes are namespaced under .agent-* so landing
       and business-rules pages are untouched.
       ===================================================================== */

    /* Agent — action row above content (holds Back-to-Home) */
    .agent-actionrow {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 12px;
        margin: -8px 0 12px 0;
    }

    /* Agent — context chip row */
    .agent-context {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        padding: 10px 14px;
        margin: 0 0 18px 0;
        background: rgba(255,255,255,0.68);
        backdrop-filter: saturate(180%) blur(18px);
        -webkit-backdrop-filter: saturate(180%) blur(18px);
        border: 1px solid var(--hairline);
        border-radius: 14px;
        box-shadow: var(--shadow-sm);
    }
    .agent-context .ctx-label {
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.10em;
        color: var(--text-muted);
        font-weight: 600;
        margin-right: 6px;
    }
    .agent-context .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 999px;
        background: var(--surface-2);
        border: 1px solid var(--hairline);
        color: var(--navy-900);
        font-family: 'Inter', sans-serif;
        font-size: 11.5px;
        font-weight: 600;
        letter-spacing: -0.005em;
        font-variant-numeric: tabular-nums;
    }
    .agent-context .chip.chip-transition {
        background: rgba(28,79,192,0.06);
        border-color: rgba(28,79,192,0.18);
        color: var(--navy-700);
    }
    .agent-context .chip .arrow {
        color: var(--navy-600);
        font-weight: 700;
        margin: 0 2px;
    }
    .agent-context .sep {
        width: 4px; height: 4px; border-radius: 50%;
        background: rgba(15,23,42,0.18);
        margin: 0 4px;
    }

    /* Agent — sidebar grouped panels */
    .agent-sec-hdr {
        font-family: 'Manrope', sans-serif;
        font-size: 10.5px;
        font-weight: 700;
        color: var(--navy-900);
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin: 18px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--hairline);
    }
    .agent-sec-hdr:first-of-type { margin-top: 4px; }

    .agent-state-panel {
        background: rgba(255,255,255,0.7);
        border: 1px solid var(--hairline);
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: var(--shadow-sm);
    }
    .agent-state-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px dashed rgba(15,23,42,0.06);
        font-family: 'Inter', sans-serif;
    }
    .agent-state-row:last-child { border-bottom: none; }
    .agent-state-row .k {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    .agent-state-row .v {
        font-family: 'Manrope', sans-serif;
        font-size: 12px;
        color: var(--navy-900);
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }

    /* Status tag chips (sidebar) */
    .agent-status-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-family: 'Inter', sans-serif;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .agent-status-tag.tag-nc   { background: rgba(100,116,139,0.14); color: #475569; }
    .agent-status-tag.tag-cov  { background: rgba(59,111,217,0.14); color: var(--navy-700); }
    .agent-status-tag.tag-pref { background: var(--navy-700); color: #ffffff; }
    .agent-status-tag.tag-spec { background: rgba(65,182,230,0.18); color: #0E6E93; }
    .agent-status-tag.tag-na   { background: rgba(15,23,42,0.05); color: var(--text-muted); }

    /* Details panel (analog / step / reverse) */
    .agent-details-panel {
        background: rgba(28,79,192,0.04);
        border: 1px solid rgba(28,79,192,0.12);
        border-left: 3px solid var(--navy-600);
        border-radius: 12px;
        padding: 12px 14px;
    }
    .agent-details-panel.warn {
        background: rgba(239,68,68,0.05);
        border: 1px solid rgba(239,68,68,0.18);
        border-left: 3px solid var(--down);
    }
    .agent-details-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        font-family: 'Inter', sans-serif;
    }
    .agent-details-row .k {
        font-size: 11px;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .agent-details-row .v {
        font-family: 'JetBrains Mono', 'Consolas', monospace;
        font-size: 12px;
        color: var(--navy-900);
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .agent-details-warn {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: var(--down);
        font-weight: 600;
        margin-top: 6px;
    }

    /* Agent — KPI hero row */
    .agent-kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin: 4px 0 20px 0;
    }
    @media (max-width: 1180px) {
        .agent-kpi-row { grid-template-columns: repeat(2, 1fr); }
    }
    .agent-kpi {
        background: var(--surface);
        border: 1px solid var(--hairline);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: var(--shadow-sm);
        transition: transform 0.18s var(--ease-out), box-shadow 0.18s var(--ease-out);
        position: relative;
        overflow: hidden;
        min-height: 108px;
    }
    .agent-kpi::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, var(--navy-600), var(--accent));
    }
    .agent-kpi.kpi-neg::before { background: var(--down); }
    .agent-kpi.kpi-pos::before { background: linear-gradient(180deg, var(--up), #6EE7B7); }
    .agent-kpi.kpi-accent::before { background: var(--accent); }
    .agent-kpi:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    .agent-kpi .label {
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.10em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .agent-kpi .value {
        font-family: 'Manrope', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: var(--navy-900);
        letter-spacing: -0.025em;
        line-height: 1.05;
        font-variant-numeric: tabular-nums;
    }
    .agent-kpi .value.small { font-size: 20px; }
    .agent-kpi .value.pos { color: var(--up); }
    .agent-kpi .value.neg { color: var(--down); }
    .agent-kpi .delta {
        margin-top: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 11.5px;
        color: var(--text-muted);
        font-weight: 500;
        font-variant-numeric: tabular-nums;
    }
    .agent-kpi .delta.pos { color: var(--up); font-weight: 600; }
    .agent-kpi .delta.neg { color: var(--down); font-weight: 600; }

    /* Sidebar — pull content to the very top (zero out Streamlit's default top padding) */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
    }
    /* Kill any residual margin on the first child inside the sidebar */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Hide the invisible agent-page-marker container so it doesn't add vertical space above Back-to-Home */
    [data-testid="stElementContainer"]:has(.agent-page-marker),
    div:has(> .agent-page-marker) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Agent — sidebar brand block (stacked: logo on top, title below,
       spacing matched to Migraine Intelligence Hub reference) */
    .agent-sidebar-brand {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        padding: 1.6rem 1.1rem 1rem 1.1rem;
        margin: 0 -1rem 0 -1rem;
        border-bottom: 1px solid var(--hairline);
    }
    .agent-sidebar-brand .brand-logo {
        height: 28px;
        width: auto;
        object-fit: contain;
        align-self: flex-start;
        flex-shrink: 0;
    }
    .agent-sidebar-brand .brand-logo-fallback {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        color: var(--navy-700);
        font-size: 18px;
        line-height: 1;
        align-self: flex-start;
    }
    .agent-sidebar-brand .brand-copy { line-height: 1.18; }
    .agent-sidebar-brand .brand-title {
        font-family: 'Manrope', sans-serif;
        font-size: 1.22rem;
        font-weight: 800;
        color: var(--navy-900);
        letter-spacing: -0.025em;
        line-height: 1.18;
    }
    .agent-sidebar-brand .brand-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: var(--text-muted);
        font-weight: 500;
        margin-top: 0.35rem;
    }

    /* Section header labels — proper breathing room above each section */
    .agent-sec-hdr {
        font-family: 'Manrope', sans-serif;
        font-size: 0.62rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 1.15rem 0.15rem 0.5rem 0.15rem;
        margin: 0;
        border-bottom: none;
    }
    .agent-sec-hdr:first-of-type { padding-top: 1.1rem; }

    /* Sidebar element rhythm — tight but breathable */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    section[data-testid="stSidebar"] .element-container,
    section[data-testid="stSidebar"] [data-testid="stElementContainer"] { margin-bottom: 0 !important; }

    /* Label + input rhythm inside the sidebar */
    section[data-testid="stSidebar"] .stSelectbox { margin-bottom: 0.35rem !important; }
    section[data-testid="stSidebar"] label { margin-bottom: 0.15rem !important; }

    /* Extra breathing room around the state and details panels */
    .agent-state-panel { margin-top: 0.15rem; }
    .agent-details-panel { margin-top: 0.15rem; }

    /* Main-content top alignment — line the Back-to-Home button up with
       the sidebar brand block's logo. Streamlit's sidebar has hidden internal
       top offsets we can't reliably zero, so we push the button down with an
       explicit margin. Value derived from measured screenshot offset (~34 px). */
    body:has(.agent-page-marker) .block-container {
        padding-top: 0.5rem !important;
    }
    .st-key-agent_back_home,
    div[class*="st-key-agent_back_home"] {
        margin-top: 60px !important;
    }
    .st-key-agent_back_home .stButton,
    div[class*="st-key-agent_back_home"] .stButton {
        margin-top: 0 !important;
    }

    /* Agent — Back-to-Home compact button (overrides the global sidebar button style) */
    .st-key-agent_back_home .stButton > button,
    div[class*="st-key-agent_back_home"] .stButton > button {
        background: rgba(255,255,255,0.72) !important;
        color: var(--navy-700) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 8px !important;
        padding: 4px 10px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        box-shadow: none !important;
        min-height: 0 !important;
        line-height: 1.2 !important;
    }
    .st-key-agent_back_home .stButton > button:hover,
    div[class*="st-key-agent_back_home"] .stButton > button:hover {
        background: #ffffff !important;
        color: var(--navy-900) !important;
        border-color: rgba(28,79,192,0.22) !important;
        transform: none !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* Agent — segmented toggle: darker label color + kill Streamlit's default
       block spacing around the radio so no white strip appears below */
    .st-key-agent_chart_view .stRadio > div[role="radiogroup"],
    div[class*="st-key-agent_chart_view"] .stRadio > div[role="radiogroup"] {
        display: inline-flex !important;
        gap: 0 !important;
        background: var(--surface-2) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 999px !important;
        padding: 3px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .st-key-agent_chart_view .stRadio label,
    div[class*="st-key-agent_chart_view"] .stRadio label {
        margin: 0 !important;
        padding: 6px 18px !important;
        border-radius: 999px !important;
        cursor: pointer !important;
        transition: all 0.18s var(--ease-out) !important;
        background: transparent !important;
    }
    /* Force text color on ALL descendants (Streamlit wraps label text in <p>/<div>) */
    .st-key-agent_chart_view .stRadio label,
    .st-key-agent_chart_view .stRadio label *,
    div[class*="st-key-agent_chart_view"] .stRadio label,
    div[class*="st-key-agent_chart_view"] .stRadio label * {
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        letter-spacing: -0.005em !important;
        -webkit-text-fill-color: var(--navy-900) !important;
    }
    .st-key-agent_chart_view .stRadio label:hover,
    .st-key-agent_chart_view .stRadio label:hover *,
    div[class*="st-key-agent_chart_view"] .stRadio label:hover,
    div[class*="st-key-agent_chart_view"] .stRadio label:hover * {
        color: var(--navy-700) !important;
        -webkit-text-fill-color: var(--navy-700) !important;
    }
    .st-key-agent_chart_view .stRadio label:has(input:checked),
    div[class*="st-key-agent_chart_view"] .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, var(--navy-600), var(--navy-500)) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .st-key-agent_chart_view .stRadio label:has(input:checked),
    .st-key-agent_chart_view .stRadio label:has(input:checked) *,
    div[class*="st-key-agent_chart_view"] .stRadio label:has(input:checked),
    div[class*="st-key-agent_chart_view"] .stRadio label:has(input:checked) * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .st-key-agent_chart_view .stRadio input[type="radio"],
    div[class*="st-key-agent_chart_view"] .stRadio input[type="radio"] {
        display: none !important;
    }
    .st-key-agent_chart_view .stRadio > label > div:first-child,
    .st-key-agent_chart_view .stRadio label [data-baseweb="radio"],
    div[class*="st-key-agent_chart_view"] .stRadio > label > div:first-child,
    div[class*="st-key-agent_chart_view"] .stRadio label [data-baseweb="radio"] {
        display: none !important;
    }
    /* Kill every source of white strip: element container margin, padding, background */
    .st-key-agent_chart_view,
    div[class*="st-key-agent_chart_view"],
    .st-key-agent_chart_view [data-testid="stRadio"],
    .st-key-agent_chart_view [data-testid="stElementContainer"],
    .st-key-agent_chart_view [data-testid="element-container"],
    .st-key-agent_chart_view [data-testid="stVerticalBlock"],
    div[class*="st-key-agent_chart_view"] [data-testid="stRadio"],
    div[class*="st-key-agent_chart_view"] [data-testid="stElementContainer"],
    div[class*="st-key-agent_chart_view"] [data-testid="element-container"],
    div[class*="st-key-agent_chart_view"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
        border: none !important;
        min-height: 0 !important;
    }
    /* Pull the chart wrap tight under the toggle to eliminate any residual gap */
    .agent-chart-wrap {
        margin-top: 4px !important;
    }
    .agent-trend-title {
        margin-bottom: 4px !important;
    }

    /* Agent — segmented toggle (radio styled as pills) */
    .agent-toggle-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 4px 0 10px 0;
    }
    .agent-toggle-wrap .toggle-title {
        font-family: 'Manrope', sans-serif;
        font-size: 14px;
        font-weight: 700;
        color: var(--navy-900);
        letter-spacing: -0.01em;
    }
    .agent-toggle .stRadio > div[role="radiogroup"] {
        display: inline-flex !important;
        gap: 0 !important;
        background: var(--surface-2) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 999px !important;
        padding: 3px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .agent-toggle .stRadio label {
        margin: 0 !important;
        padding: 6px 18px !important;
        border-radius: 999px !important;
        cursor: pointer !important;
        transition: all 0.18s var(--ease-out) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
    }
    .agent-toggle .stRadio label:hover { color: var(--navy-700) !important; }
    .agent-toggle .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, var(--navy-600), var(--navy-500)) !important;
        color: #ffffff !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .agent-toggle .stRadio input[type="radio"] {
        display: none !important;
    }
    .agent-toggle .stRadio > label > div:first-child { display: none !important; }

    /* Agent — chart container */
    .agent-chart-wrap {
        background: var(--surface);
        border: 1px solid var(--hairline);
        border-radius: 18px;
        padding: 18px 18px 8px 18px;
        box-shadow: var(--shadow-sm);
        animation: fadeIn 220ms var(--ease-out);
    }

    /* Agent — skeleton loader */
    @keyframes agentShimmer {
        0%   { background-position: -400px 0; }
        100% { background-position: 400px 0; }
    }
    .agent-skeleton {
        border-radius: 14px;
        background: linear-gradient(90deg,
            rgba(15,23,42,0.05) 0%,
            rgba(15,23,42,0.10) 50%,
            rgba(15,23,42,0.05) 100%);
        background-size: 800px 100%;
        animation: agentShimmer 1.4s infinite linear;
    }
    .agent-skeleton.k { height: 108px; }
    .agent-skeleton.c { height: 380px; margin-top: 12px; }

    /* Agent — empty state (invalid transition) */
    .agent-empty {
        background: var(--surface);
        border: 1px solid var(--hairline);
        border-radius: 18px;
        padding: 32px 28px;
        box-shadow: var(--shadow-sm);
        display: flex;
        gap: 20px;
        align-items: flex-start;
    }
    .agent-empty .icon {
        width: 48px; height: 48px;
        border-radius: 12px;
        background: rgba(245,158,11,0.14);
        color: #B45309;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px;
        font-weight: 700;
        font-family: 'Manrope', sans-serif;
        flex-shrink: 0;
    }
    .agent-empty h3 {
        font-family: 'Manrope', sans-serif;
        font-size: 16px;
        color: var(--navy-900);
        margin: 0 0 6px 0;
        letter-spacing: -0.015em;
    }
    .agent-empty p {
        font-family: 'Inter', sans-serif;
        font-size: 12.5px;
        color: var(--text-soft);
        margin: 0;
        line-height: 1.55;
    }
    .agent-empty .suggest {
        margin-top: 10px;
        display: flex; flex-wrap: wrap; gap: 6px;
    }
    .agent-empty .suggest span {
        padding: 3px 10px;
        border-radius: 999px;
        background: rgba(28,79,192,0.06);
        color: var(--navy-700);
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 600;
    }

    /* Agent — section heading (KPI, Chart) */
    .agent-sec-title {
        font-family: 'Manrope', sans-serif;
        font-size: 11px;
        font-weight: 700;
        color: var(--navy-900);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 8px 0 10px 2px;
    }

    /* Agent — footer meta */
    .agent-footer {
        text-align: center;
        color: var(--text-muted);
        font-family: 'Inter', sans-serif;
        font-size: 10.5px;
        margin-top: 24px;
        padding-top: 12px;
        border-top: 1px solid var(--hairline);
        font-variant-numeric: tabular-nums;
    }
    .agent-footer .dot { margin: 0 8px; opacity: 0.6; }

    /* Accessibility — focus visible */
    .agent-toggle .stRadio label:focus-within,
    .agent-kpi:focus-within {
        outline: 2px solid var(--accent);
        outline-offset: 2px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
if 'page' not in st.session_state:
    st.session_state.page = 'landing'


def go_to_agent():
    st.session_state.page = 'agent'


def go_to_rules():
    st.session_state.page = 'rules'


def go_to_landing():
    st.session_state.page = 'landing'


# =============================================================================
# GET USER NAME
# =============================================================================
def get_first_name():
    # Try Dataiku API — prioritize email (format: firstname.lastname@pfizer.com)
    try:
        import dataiku
        client = dataiku.api_client()
        auth_info = client.get_auth_info()
        # Fields: authIdentifier, groups, email, displayName
        email = auth_info.get("email", "")
        if email:
            local_part = email.split("@")[0]        # "pranav.sanotra"
            first_name = local_part.split(".")[0]    # "pranav"
            return first_name.capitalize()           # "Pranav"
        display_name = auth_info.get("displayName", "")
        if display_name:
            return display_name.split(" ")[0].capitalize()
    except Exception:
        pass
    # Fallback: OS username
    try:
        username = os.getlogin()
        if "." in username:
            return username.split(".")[0].capitalize()
        return username.capitalize()
    except Exception:
        return "User"


# =============================================================================
# HEADER (all pages)
# =============================================================================
# Load and resize logo for embedding
def _get_logo_b64():
    """Locate logo.png in common Streamlit / Dataiku webapp paths and return
    a base64-encoded PNG. Uses PIL to resize for the header when available;
    falls back to the raw file bytes so the logo still renders even without PIL."""
    import io

    candidates = []
    # 1) CWD
    candidates.append(os.path.join(os.getcwd(), "logo.png"))
    # 2) Same directory as this script (works in most Streamlit runners)
    try:
        if '__file__' in globals():
            candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))
    except Exception:
        pass
    # 3) Parent of CWD (Dataiku sometimes runs from a nested working dir)
    candidates.append(os.path.join(os.path.dirname(os.getcwd()), "logo.png"))
    # 4) Dataiku webapp resource conventions
    candidates.append("/home/dataiku/dss/lib/logo.png")
    candidates.append(os.path.join(os.getcwd(), "resource", "logo.png"))
    candidates.append(os.path.join(os.getcwd(), "static", "logo.png"))

    logo_path = None
    for p in candidates:
        try:
            if p and os.path.isfile(p):
                logo_path = p
                break
        except Exception:
            continue
    if not logo_path:
        return None

    # Prefer PIL-resized output; fall back to raw bytes so the image still shows.
    try:
        from PIL import Image
        img = Image.open(logo_path)
        ratio = 40 / img.height
        img = img.resize((int(img.width * ratio), 40), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None

_b64 = _get_logo_b64()
# On the agent page, the brand block lives in the sidebar (see agent-sidebar-brand).
# Render the wide global header only on the landing and business-rules pages.
# Primary logo source is the Pfizer corporate CDN — matches the Migraine
# Intelligence Hub reference and bypasses file-path issues in Dataiku.
_pfizer_cdn_url = "https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png"
if st.session_state.page != 'agent':
    if _b64:
        _hdr_img = (
            f'<img src="{_pfizer_cdn_url}" '
            f'onerror="this.onerror=null;this.src=\'data:image/png;base64,{_b64}\';" '
            f'alt="Pfizer" style="height:30px;object-fit:contain;">'
        )
    else:
        _hdr_img = (
            f'<img src="{_pfizer_cdn_url}" '
            f'onerror="this.onerror=null;this.src=\'logo.png\';" '
            f'alt="Pfizer" style="height:30px;object-fit:contain;">'
        )
    st.markdown(f"""
    <div class="pfizer-header">
        <span class="pfizer-logo">{_hdr_img}</span>
        <h1>REBATE DECISION AGENT</h1>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE: LANDING
# =============================================================================
if st.session_state.page == 'landing':

    # Hide sidebar on landing page
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        <h3>Disclaimer</h3>
        <p>This tool provides projected market share estimates based on historical analog data and formulary status change assumptions. Results are indicative and intended to support scenario planning only.</p>
        <ul>
            <li>Projections are based on analog-derived rate-of-change curves (BCBS, Providence, Blended)</li>
            <li>Actual market dynamics may differ due to competitive actions, market access changes, or other external factors</li>
            <li>National roll-up assumes all other MCOs maintain baseline trajectory</li>
            <li>This tool does not constitute a financial commitment or guarantee</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.button("Rebate Decision Agent", on_click=go_to_agent, use_container_width=True, type="primary")
        st.markdown("")
        st.button("Business Rules", on_click=go_to_rules, use_container_width=True)


# =============================================================================
# PAGE: BUSINESS RULES
# =============================================================================
elif st.session_state.page == 'rules':

    # Hide sidebar on rules page
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.button("Back to Home", on_click=go_to_landing)

    st.markdown("---")
    st.markdown('<h2 style="font-family:Manrope,sans-serif; color:#0A1A3D; margin-bottom:4px; letter-spacing:-0.02em;">Business Rules & Methodology</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Inter,sans-serif; color:#64748B; font-size:13px; margin-bottom:20px;">How the Rebate Decision Agent computes market share projections</p>', unsafe_allow_html=True)

    # --- Section 1: Data Sources ---
    st.markdown('<h4 style="font-family:Manrope,sans-serif; color:#0A1A3D; border-bottom:2px solid #41B6E6; padding-bottom:6px;">Data Sources</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.75); border:1px solid rgba(15,23,42,0.08); border-radius:14px; padding:18px; margin-bottom:12px; box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <p style="font-family:Manrope,sans-serif; font-weight:700; color:#0A1A3D; margin:0 0 6px 0;">Market Share Table</p>
            <p style="font-family:Inter,sans-serif; font-size:12px; color:#475569; margin:2px 0;">~2,723 MCOs with 36 months of baseline market share data (Jan 2025 - Dec 2027). Months Jan'25 - Mar'26 are actuals; Apr'26 onward are projected.</p>
        </div>
        <div style="background:rgba(255,255,255,0.75); border:1px solid rgba(15,23,42,0.08); border-radius:14px; padding:18px; box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <p style="font-family:Manrope,sans-serif; font-weight:700; color:#0A1A3D; margin:0 0 6px 0;">OCGRP Claims Table</p>
            <p style="font-family:Inter,sans-serif; font-size:12px; color:#475569; margin:2px 0;">~2,730 MCOs with monthly OCGRP claim volumes. Used to convert MCO-level market share into claim counts for national roll-up calculations.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.75); border:1px solid rgba(15,23,42,0.08); border-radius:14px; padding:18px; margin-bottom:12px; box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <p style="font-family:Manrope,sans-serif; font-weight:700; color:#0A1A3D; margin:0 0 6px 0;">Analog Curves</p>
            <p style="font-family:Inter,sans-serif; font-size:12px; color:#475569; margin:2px 0;">23-month rate-of-change curves derived from historical formulary changes. Three analogs: BCBS (Covered to Preferred), Providence (Covered to Not Covered), Blended (Preferred to Not Covered).</p>
        </div>
        <div style="background:rgba(255,255,255,0.75); border:1px solid rgba(15,23,42,0.08); border-radius:14px; padding:18px; box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <p style="font-family:Manrope,sans-serif; font-weight:700; color:#0A1A3D; margin:0 0 6px 0;">Step Table</p>
            <p style="font-family:Inter,sans-serif; font-size:12px; color:#475569; margin:2px 0;">Maps every possible status transition (Current to Future) to the appropriate analog curve with direction (Reverse) and magnitude (Step) parameters.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 2: Projection Formula ---
    st.markdown('<h4 style="font-family:Manrope,sans-serif; color:#0A1A3D; border-bottom:2px solid #41B6E6; padding-bottom:6px;">Projection Formula</h4>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(28,79,192,0.04); border-left:4px solid #1C4FC0; padding:18px 22px; border-radius:12px; margin:12px 0;">
        <p style="font-family:Manrope,sans-serif; font-size:14px; color:#0A1A3D; font-weight:700; margin:0 0 10px 0;">For each month M from Change Month onward:</p>
        <p style="font-size:15px; color:#0A1A3D; font-family:monospace; margin:0; background:rgba(255,255,255,0.8); padding:12px 16px; border-radius:8px; display:inline-block; border:1px solid rgba(15,23,42,0.08);">
            Projected[M] = Baseline[M] &times; (1 + analog_rate &times; Reverse)
        </p>
        <ul style="font-family:Inter,sans-serif; font-size:12px; color:#475569; margin-top:14px;">
            <li><b>Baseline[M]</b> &mdash; Original forecasted market share from the Market Share table</li>
            <li><b>analog_rate</b> &mdash; Month-over-month relative difference value for the selected analog</li>
            <li><b>Reverse</b> &mdash; +1 for downward status changes, -1 for upward status changes</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 3: Transition Mapping ---
    st.markdown('<h4 style="font-family:Manrope,sans-serif; color:#0A1A3D; border-bottom:2px solid #41B6E6; padding-bottom:6px;">Status Transition Mapping</h4>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Inter,sans-serif; font-size:12px; color:#475569;">Each formulary status change maps to a specific analog and direction:</p>', unsafe_allow_html=True)

    step_df = pd.DataFrame([
        {"Current": "Not Covered", "Future": "Covered", "Analog": "Providence", "Step": 1, "Reverse": -1},
        {"Current": "Not Covered", "Future": "Preferred", "Analog": "Blended", "Step": 2, "Reverse": -1},
        {"Current": "Preferred", "Future": "Covered", "Analog": "BCBS", "Step": -1, "Reverse": -1},
        {"Current": "Not Covered", "Future": "Specialty", "Analog": "Providence", "Step": 1, "Reverse": -1},
        {"Current": "Preferred", "Future": "Specialty", "Analog": "BCBS", "Step": -1, "Reverse": -1},
        {"Current": "Specialty", "Future": "Preferred", "Analog": "BCBS", "Step": 1, "Reverse": 1},
        {"Current": "Specialty", "Future": "Not Covered", "Analog": "Providence", "Step": -1, "Reverse": 1},
        {"Current": "Covered", "Future": "Preferred", "Analog": "BCBS", "Step": 1, "Reverse": 1},
        {"Current": "Preferred", "Future": "Not Covered", "Analog": "Blended", "Step": -2, "Reverse": 1},
        {"Current": "Covered", "Future": "Not Covered", "Analog": "Providence", "Step": -1, "Reverse": 1},
    ])
    st.table(step_df)
    st.caption("Note: Specialty status is treated as equivalent to Covered for transition mapping purposes.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 4: Analog Curves ---
    st.markdown('<h4 style="font-family:Manrope,sans-serif; color:#0A1A3D; border-bottom:2px solid #41B6E6; padding-bottom:6px;">Analog Curves (Month-Level Dynamics)</h4>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Inter,sans-serif; font-size:12px; color:#475569;">Monthly relative rate-of-change values for each analog. The Month 1 value is used as the impact rate for all projected months post status change.</p>', unsafe_allow_html=True)

    analog_df = pd.DataFrame({
        'Month': [f"Month {i+1}" for i in range(23)],
        'BCBS': [0.0614, 0.0668, 0.1452, 0.1246, 0.1582, 0.1501, 0.0961, 0.1315,
                 0.1024, 0.1168, 0.1870, 0.1495, 0.1634, 0.1469, 0.1861, 0.1517,
                 0.1199, 0.1131, 0.1209, 0.1245, 0.1448, 0.1379, 0.2415],
        'Providence': [-0.1755, -0.1993, -0.0906, -0.0744, -0.3362, -0.2854,
                       -0.4238, -0.3848, -0.3862, -0.4169, -0.4470, -0.5508,
                       -0.4832, -0.4727, -0.5195, -0.4965, -0.4912, -0.4835,
                       -0.5108, -0.5250, -0.4921, -0.5226, -0.4983],
        'Blended': [-0.2369, -0.2662, -0.2358, -0.1991, -0.4944, -0.4354,
                    -0.5198, -0.5163, -0.4886, -0.5337, -0.6340, -0.7003,
                    -0.6465, -0.6195, -0.7056, -0.6482, -0.6110, -0.5966,
                    -0.6317, -0.6495, -0.6369, -0.6605, -0.7398],
    })
    st.table(analog_df)
    st.caption("Note: Month 1 rate is applied at the change month, Month 2 rate at the next month, and so on. Each rate represents the total impact on market share at that point in time.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 5: National Roll-Up ---
    st.markdown('<h4 style="font-family:Manrope,sans-serif; color:#0A1A3D; border-bottom:2px solid #41B6E6; padding-bottom:6px;">National Roll-Up Logic</h4>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(255,255,255,0.75); border:1px solid rgba(15,23,42,0.08); border-radius:14px; padding:20px 24px; margin:12px 0; box-shadow:0 2px 8px rgba(15,23,42,0.05);">
        <p style="font-family:Inter,sans-serif; font-size:12px; color:#475569; margin:0 0 12px 0;">To compute the national-level impact of a single MCO's status change:</p>
        <ol style="font-family:Inter,sans-serif; font-size:12px; color:#0F172A; line-height:1.9; padding-left:18px;">
            <li>For the <b>selected MCO</b>: apply projected (post-change) market share</li>
            <li>For <b>all other MCOs</b>: retain their baseline market share</li>
            <li>Compute per MCO: <code style="background:rgba(28,79,192,0.06); padding:2px 6px; border-radius:4px;">Nurtec Claims = Market Share &times; OCGRP Claims</code></li>
            <li>Sum across all MCOs to get national totals</li>
            <li>National MS = Total Nurtec Claims &divide; Total OCGRP Claims</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 5: Timeline ---
    st.markdown('<h4 style="font-family:Manrope,sans-serif; color:#0A1A3D; border-bottom:2px solid #41B6E6; padding-bottom:6px;">Data Timeline</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:rgba(28,79,192,0.04); border:1px solid rgba(28,79,192,0.1); border-radius:14px; padding:16px 20px; text-align:center;">
            <p style="font-family:Inter,sans-serif; font-size:11px; color:#64748B; margin:0; text-transform:uppercase; font-weight:600; letter-spacing:0.06em;">Actual Period</p>
            <p style="font-family:Manrope,sans-serif; font-size:1.2rem; font-weight:700; color:#0A1A3D; margin:6px 0; letter-spacing:-0.02em;">Jan 2025 - Mar 2026</p>
            <p style="font-family:Inter,sans-serif; font-size:11px; color:#475569; margin:0;">15 months of historical data</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:rgba(245,158,11,0.06); border:1px solid rgba(245,158,11,0.15); border-radius:14px; padding:16px 20px; text-align:center;">
            <p style="font-family:Inter,sans-serif; font-size:11px; color:#64748B; margin:0; text-transform:uppercase; font-weight:600; letter-spacing:0.06em;">Forecast Period</p>
            <p style="font-family:Manrope,sans-serif; font-size:1.2rem; font-weight:700; color:#0A1A3D; margin:6px 0; letter-spacing:-0.02em;">Apr 2026 - Dec 2027</p>
            <p style="font-family:Inter,sans-serif; font-size:11px; color:#475569; margin:0;">21 months of projected data</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE: AGENT (main tool)
# =============================================================================
elif st.session_state.page == 'agent':

    # Marker used by CSS to tighten main-content top padding on this page
    st.markdown('<span class="agent-page-marker" style="display:none"></span>', unsafe_allow_html=True)

    # Force sidebar open via set_page_config workaround
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: block !important;
            width: 320px !important;
            min-width: 320px !important;
            transform: none !important;
        }
        section[data-testid="stSidebar"] > div {
            width: 320px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================================
    # DATA LOADING (from Dataiku datasets)
    # =========================================================================
    @st.cache_data(ttl=300)
    def load_data():
        """Load all 4 datasets from Dataiku."""
        # Market Share
        df_ms = dataiku.Dataset("SQL_NURTEC_XPO_NPA_SCALED_MS_by_MONTH_SF").get_dataframe()
        df_ms = df_ms.dropna(subset=['MCO_NM'])

        # OCGRP Claims
        df_oc = dataiku.Dataset("SQL_XPO_NPA_SCALED_OCGRP_TRX_MONTH_SF").get_dataframe()
        df_oc = df_oc.dropna(subset=['MCO_NM'])

        # Analog Curves
        df_analog = dataiku.Dataset("PAYER_MODEL_ANALOG_MCO_SF").get_dataframe()
        df_analog['month_num'] = df_analog['MONTH'].str.extract(r'(\d+)').astype(int)
        df_analog = df_analog.sort_values('month_num').reset_index(drop=True)
        analog_curves = {
            'BCBS': [float(x) for x in df_analog['BCBS'].tolist()],
            'Providence': [float(x) for x in df_analog['Providence'].tolist()],
            'Blended': [float(x) for x in df_analog['Blended'].tolist()],
        }

        # Step Table
        df_step = dataiku.Dataset("PAYER_MODEL_STEP_SF").get_dataframe()
        step_table = {}
        for _, row in df_step.iterrows():
            key = (str(row['Current']).strip(), str(row['Future']).strip())
            step_table[key] = {
                'analog': str(row['Analog used']).strip(),
                'step': int(row['Step']),
                'reverse': int(row['Reverse']),
            }

        return df_ms, df_oc, analog_curves, step_table

    df_market_share, df_ocgrp, ANALOG_CURVES, STEP_TABLE = load_data()

    MCO_LIST = sorted(df_market_share['MCO_NM'].unique().tolist())
    MONTH_LABELS = [
        "Jan'25", "Feb'25", "Mar'25", "Apr'25", "May'25", "Jun'25",
        "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25",
        "Jan'26", "Feb'26", "Mar'26", "Apr'26", "May'26", "Jun'26",
        "Jul'26", "Aug'26", "Sep'26", "Oct'26", "Nov'26", "Dec'26",
        "Jan'27", "Feb'27", "Mar'27", "Apr'27", "May'27", "Jun'27",
        "Jul'27", "Aug'27", "Sep'27", "Oct'27", "Nov'27", "Dec'27",
    ]
    CHANGE_MONTH_OPTIONS = [
        "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026",
        "Oct 2026", "Nov 2026", "Dec 2026", "Jan 2027", "Feb 2027", "Mar 2027",
        "Apr 2027", "May 2027", "Jun 2027", "Jul 2027", "Aug 2027", "Sep 2027",
        "Oct 2027", "Nov 2027", "Dec 2027",
    ]
    CHANGE_MONTH_IDX_MAP = {label: i + 15 for i, label in enumerate(CHANGE_MONTH_OPTIONS)}
    STATUS_OPTIONS = ['Not Covered', 'Covered', 'Preferred', 'Specialty']
    N_ACTUAL = 15
    N_TOTAL = 36

    # =========================================================================
    # HELPERS
    # =========================================================================
    MS_COLS = [f"{y}{m:02d}_NURTEC_MS_sum" for y in range(2025, 2028) for m in range(1, 13)][:36]
    OCGRP_COLS = [f"{y}{m:02d}_OCGRP_NPA_TRX_sum" for y in range(2025, 2028) for m in range(1, 13)][:36]

    def get_mco_ms(mco_name):
        row = df_market_share[df_market_share['MCO_NM'] == mco_name]
        if row.empty:
            return [0.0] * N_TOTAL
        values = row.iloc[0][MS_COLS].tolist()
        return [float(v) * 100 if pd.notna(v) else 0.0 for v in values]

    def get_mco_ocgrp(mco_name):
        row = df_ocgrp[df_ocgrp['MCO_NM'] == mco_name]
        if row.empty:
            return [0.0] * N_TOTAL
        values = row.iloc[0][OCGRP_COLS].tolist()
        return [float(v) if pd.notna(v) else 0.0 for v in values]

    def get_mco_metadata(mco_name):
        row = df_market_share[df_market_share['MCO_NM'] == mco_name]
        if row.empty:
            return "Data not available yet", "Data not available yet", "N/A"
        status = row.iloc[0]['CURRENT_NURTEC_STATUS']
        payer = row.iloc[0]['PAYER_TYPE']
        contrib = row.iloc[0]['FY_2025_OCGRP_CONTRIBUTION']
        status = str(status).strip() if pd.notna(status) and str(status).strip() not in ['', 'nan', 'None'] else "Data not available yet"
        payer = str(payer).strip() if pd.notna(payer) and str(payer).strip() not in ['', 'nan', 'None'] else "Data not available yet"
        try:
            contrib = f"{float(contrib):.2f}%" if pd.notna(contrib) else "N/A"
        except (TypeError, ValueError):
            contrib = "N/A"
        return status, payer, contrib

    def apply_analog(baseline_ms, change_idx, analog_curve, reverse):
        projected = list(baseline_ms[:change_idx])
        for i in range(change_idx, N_TOTAL):
            m = i - change_idx
            rate = analog_curve[m] if m < len(analog_curve) else analog_curve[-1]
            val = baseline_ms[i] * (1 + rate * reverse)
            projected.append(round(max(val, 0.1), 4))
        return projected

    def compute_national_ms(selected_mco, projected_ms, change_idx):
        baseline_national_nurtec = [0.0] * N_TOTAL
        projected_national_nurtec = [0.0] * N_TOTAL
        national_ocgrp = [0.0] * N_TOTAL
        for mco in MCO_LIST:
            mco_ms = get_mco_ms(mco)
            mco_ocgrp = get_mco_ocgrp(mco)
            for m in range(N_TOTAL):
                ocgrp_val = mco_ocgrp[m]
                national_ocgrp[m] += ocgrp_val
                baseline_national_nurtec[m] += (mco_ms[m] / 100.0) * ocgrp_val
                if mco == selected_mco:
                    projected_national_nurtec[m] += (projected_ms[m] / 100.0) * ocgrp_val
                else:
                    projected_national_nurtec[m] += (mco_ms[m] / 100.0) * ocgrp_val
        baseline_natl_ms = []
        projected_natl_ms = []
        for m in range(N_TOTAL):
            if national_ocgrp[m] > 0:
                baseline_natl_ms.append((baseline_national_nurtec[m] / national_ocgrp[m]) * 100)
                projected_natl_ms.append((projected_national_nurtec[m] / national_ocgrp[m]) * 100)
            else:
                baseline_natl_ms.append(0.0)
                projected_natl_ms.append(0.0)
        return baseline_natl_ms, projected_natl_ms

    # =========================================================================
    # SIDEBAR — grouped panels (Inputs / Current State / Scenario Details)
    # =========================================================================
    def _status_tag(status):
        cls_map = {
            'Not Covered': 'tag-nc',
            'Covered':     'tag-cov',
            'Preferred':   'tag-pref',
            'Specialty':   'tag-spec',
        }
        cls = cls_map.get(status, 'tag-na')
        return f'<span class="agent-status-tag {cls}">{status}</span>'

    with st.sidebar:
        # ---- Brand block at the very top (stacked: logo -> title -> subtitle) ----
        # Primary: Pfizer CDN logo (works on the corporate network, same source
        # as the Migraine Intelligence Hub reference). Fallback: local base64.
        _pfizer_cdn = "https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png"
        if _b64:
            _brand_logo = (
                f'<img class="brand-logo" src="{_pfizer_cdn}" '
                f'onerror="this.onerror=null;this.src=\'data:image/png;base64,{_b64}\';" '
                f'alt="Pfizer">'
            )
        else:
            _brand_logo = (
                f'<img class="brand-logo" src="{_pfizer_cdn}" '
                f'onerror="this.onerror=null;this.src=\'logo.png\';" '
                f'alt="Pfizer">'
            )
        st.markdown(f"""
        <div class="agent-sidebar-brand">
            {_brand_logo}
            <div class="brand-copy">
                <div class="brand-title">Rebate Decision<br>Agent</div>
                <div class="brand-subtitle">Nurtec&reg; Payer Model</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- Section A: Scenario Inputs ----
        st.markdown('<div class="agent-sec-hdr">Scenario Inputs</div>', unsafe_allow_html=True)

        selected_mco = st.selectbox(
            "Select MCO (type to search)",
            MCO_LIST,
            index=0,
            placeholder="Type MCO name to search..."
        )

        current_status, payer_type, ocgrp_contrib = get_mco_metadata(selected_mco)

        if current_status in STATUS_OPTIONS:
            future_options = [s for s in STATUS_OPTIONS if s != current_status]
        else:
            future_options = STATUS_OPTIONS

        future_status = st.selectbox("Future Status", future_options)
        selected_change_month = st.selectbox("Change Month", CHANGE_MONTH_OPTIONS, index=6)
        change_idx = CHANGE_MONTH_IDX_MAP[selected_change_month]

        # ---- Section B: Current State (read-only info panel) ----
        st.markdown('<div class="agent-sec-hdr">Current State</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="agent-state-panel">
            <div class="agent-state-row">
                <span class="k">Status</span>
                <span class="v">{_status_tag(current_status)}</span>
            </div>
            <div class="agent-state-row">
                <span class="k">Payer Type</span>
                <span class="v">{payer_type}</span>
            </div>
            <div class="agent-state-row">
                <span class="k">OCGRP Contrib</span>
                <span class="v">{ocgrp_contrib}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- Section C: Scenario Details ----
        st.markdown('<div class="agent-sec-hdr">Scenario Details</div>', unsafe_allow_html=True)
        step_key = (current_status, future_status)
        if step_key in STEP_TABLE:
            info = STEP_TABLE[step_key]
            st.markdown(f"""
            <div class="agent-details-panel">
                <div class="agent-details-row">
                    <span class="k">Analog</span><span class="v">{info['analog']}</span>
                </div>
                <div class="agent-details-row">
                    <span class="k">Step</span><span class="v">{info['step']:+d}</span>
                </div>
                <div class="agent-details-row">
                    <span class="k">Reverse</span><span class="v">{info['reverse']:+d}</span>
                </div>
                <div class="agent-details-row">
                    <span class="k">Transition</span>
                    <span class="v">{current_status} &rarr; {future_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="agent-details-panel warn">
                <div class="agent-details-row">
                    <span class="k">Transition</span>
                    <span class="v">{current_status} &rarr; {future_status}</span>
                </div>
                <div class="agent-details-warn">No analog defined for this transition</div>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # ACTION ROW — Back to Home (top-left of main content)
    # =========================================================================
    _bh_l, _bh_r = st.columns([1, 6])
    with _bh_l:
        st.button("← Back to Home", on_click=go_to_landing, use_container_width=False, key="agent_back_home")

    # =========================================================================
    # COMPUTE (backend math unchanged)
    # =========================================================================
    baseline_ms = get_mco_ms(selected_mco)

    if step_key in STEP_TABLE:
        analog_name = STEP_TABLE[step_key]['analog']
        reverse = STEP_TABLE[step_key]['reverse']
        analog_curve = ANALOG_CURVES[analog_name]
        projected = apply_analog(baseline_ms, change_idx, analog_curve, reverse)
    else:
        analog_name = "N/A"
        reverse = 0
        projected = baseline_ms

    # =========================================================================
    # NATIONAL ROLL-UP (cached per scenario in session_state — pure memoization,
    # calls the untouched compute_national_ms)
    # =========================================================================
    if step_key in STEP_TABLE:
        if 'agent_rollup_cache' not in st.session_state:
            st.session_state.agent_rollup_cache = {}

        cache_key = (selected_mco, change_idx, analog_name, reverse)
        if cache_key in st.session_state.agent_rollup_cache:
            baseline_natl_ms, projected_natl_ms = st.session_state.agent_rollup_cache[cache_key]
        else:
            # Show skeleton placeholders while computing
            _sk_chart = st.empty()
            _sk_kpi = st.empty()
            _sk_chart.markdown('<div class="agent-skeleton c"></div>', unsafe_allow_html=True)
            _sk_kpi.markdown(
                '<div class="agent-kpi-row">'
                '<div class="agent-skeleton k"></div>'
                '<div class="agent-skeleton k"></div>'
                '<div class="agent-skeleton k"></div>'
                '<div class="agent-skeleton k"></div>'
                '</div>', unsafe_allow_html=True)
            baseline_natl_ms, projected_natl_ms = compute_national_ms(selected_mco, projected, change_idx)
            st.session_state.agent_rollup_cache[cache_key] = (baseline_natl_ms, projected_natl_ms)
            _sk_kpi.empty()
            _sk_chart.empty()

        # =====================================================================
        # 1) CHART with segmented toggle (National | MCO) — rendered FIRST
        # =====================================================================
        st.markdown('<div class="agent-sec-title agent-trend-title">Market Share Trend</div>', unsafe_allow_html=True)
        chart_view = st.radio(
            "chart-view",
            options=["National", "MCO"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key="agent_chart_view",
        )

        # Pick series + labels based on active view
        if chart_view == "National":
            _series_actual   = baseline_natl_ms[:N_ACTUAL]
            _series_baseline = baseline_natl_ms[N_ACTUAL - 1:]
            _series_proj     = projected_natl_ms[change_idx:]
            _yaxis_title     = 'National Market Share (%)'
            _actual_lbl      = 'Actual National MS'
        else:
            _series_actual   = baseline_ms[:N_ACTUAL]
            _series_baseline = baseline_ms[N_ACTUAL - 1:]
            _series_proj     = projected[change_idx:]
            _yaxis_title     = f'{selected_mco} Market Share (%)'
            _actual_lbl      = 'Actual MCO MS'

        fig = go.Figure()

        # Shaded forecast region (from last actual to end)
        fig.add_vrect(
            x0=N_ACTUAL - 1, x1=N_TOTAL - 1,
            fillcolor='rgba(15,23,42,0.03)',
            line_width=0, layer='below',
        )

        fig.add_trace(go.Scatter(
            x=list(range(N_ACTUAL)), y=_series_actual,
            mode='lines+markers', name=_actual_lbl,
            line=dict(color=PFZ_DARK_BLUE, width=2.75), marker=dict(size=4),
            hovertemplate='%{text}<br>MS: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(N_ACTUAL)],
        ))
        fig.add_trace(go.Scatter(
            x=list(range(N_ACTUAL - 1, N_TOTAL)), y=_series_baseline,
            mode='lines', name='Baseline (no change)',
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate='%{text}<br>Baseline: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(N_ACTUAL - 1, N_TOTAL)],
        ))
        fig.add_trace(go.Scatter(
            x=list(range(change_idx, N_TOTAL)), y=_series_proj,
            mode='lines+markers', name='Projected (post change)',
            line=dict(color=PFZ_RED, width=2.75), marker=dict(size=5),
            fill='tonexty', fillcolor='rgba(239, 68, 68, 0.06)',
            hovertemplate='%{text}<br>Projected: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(change_idx, N_TOTAL)],
        ))

        # Status change vertical line + badge
        fig.add_shape(type="line", x0=change_idx, x1=change_idx,
                      y0=0, y1=1, yref="paper",
                      line=dict(color=PFZ_ORANGE, width=2, dash="dash"))
        fig.add_annotation(
            x=change_idx, y=1.06, yref="paper",
            text=f"  Status change · {selected_change_month}  ",
            showarrow=False, align='center',
            font=dict(color='#B45309', size=10, family='Inter'),
            bgcolor='rgba(245,158,11,0.14)',
            bordercolor='rgba(245,158,11,0.35)', borderwidth=1, borderpad=4,
        )

        # Uniform y-axis padding
        _all_v = list(_series_actual) + list(_series_baseline) + list(_series_proj)
        _valid_v = [v for v in _all_v if v > 0]
        if _valid_v:
            _y_lo_raw, _y_hi_raw = min(_valid_v), max(_valid_v)
            _pad = max((_y_hi_raw - _y_lo_raw) * 0.08, 0.5)
            y_lo, y_hi = _y_lo_raw - _pad, _y_hi_raw + _pad
        else:
            y_lo, y_hi = 0, 100

        tick_idx = list(range(0, N_TOTAL, 6))
        tick_lbl = [MONTH_LABELS[i] for i in tick_idx]

        fig.update_layout(
            xaxis=dict(
                tickmode='array', tickvals=tick_idx, ticktext=tick_lbl,
                tickfont=dict(size=10, color=PFZ_GRAY, family='Inter'),
                showgrid=False, showspikes=True, spikemode='across',
                spikecolor='rgba(15,23,42,0.18)', spikethickness=1,
            ),
            yaxis=dict(
                title=_yaxis_title, ticksuffix='%',
                range=[y_lo, y_hi],
                gridcolor='rgba(15,23,42,0.04)',
                tickfont=dict(size=10, color=PFZ_GRAY, family='Inter'),
                title_font=dict(size=11, color=PFZ_DARK_BLUE, family='Manrope'),
            ),
            legend=dict(
                orientation='h', xanchor='right', x=1, y=1.14,
                font=dict(size=10.5, color=PFZ_GRAY, family='Inter'),
                bgcolor='rgba(0,0,0,0)',
            ),
            plot_bgcolor=PFZ_WHITE, paper_bgcolor='rgba(0,0,0,0)',
            height=400, margin=dict(l=60, r=20, t=60, b=30),
            hovermode='x unified',
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # =====================================================================
        # 2) KPI HERO ROW — National & MCO Impact
        # =====================================================================
        natl_baseline_current = baseline_natl_ms[N_ACTUAL - 1]
        natl_projected_12m    = projected_natl_ms[min(change_idx + 12, N_TOTAL - 1)]
        natl_delta            = natl_projected_12m - natl_baseline_current

        mco_baseline_current  = baseline_ms[N_ACTUAL - 1]
        mco_projected_12m     = projected[min(change_idx + 12, N_TOTAL - 1)]
        mco_delta             = mco_projected_12m - mco_baseline_current

        # Card 2 (Projected National MS 12m)
        c2_delta_cls = 'neg' if natl_delta < 0 else 'pos'
        c2_arrow = '&#9660;' if natl_delta < 0 else '&#9650;'
        c2_kpi_cls = 'kpi-neg' if natl_delta < 0 else 'kpi-pos'
        # Card 3 (MCO delta) — big value colored by sign
        c3_val_cls = 'neg' if mco_delta < 0 else 'pos'
        c3_arrow = '&#9660;' if mco_delta < 0 else '&#9650;'
        c3_kpi_cls = 'kpi-neg' if mco_delta < 0 else 'kpi-pos'

        st.markdown('<div class="agent-sec-title">National &amp; MCO Impact</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="agent-kpi-row">
            <div class="agent-kpi">
                <div class="label">Baseline National MS</div>
                <div class="value">{natl_baseline_current:.2f}%</div>
                <div class="delta">as of Mar 2026 (last actual)</div>
            </div>
            <div class="agent-kpi {c2_kpi_cls}">
                <div class="label">Projected · 12m post change</div>
                <div class="value">{natl_projected_12m:.2f}%</div>
                <div class="delta {c2_delta_cls}">{c2_arrow} {natl_delta:+.2f} pp vs baseline</div>
            </div>
            <div class="agent-kpi {c3_kpi_cls}">
                <div class="label">MCO-Level Delta</div>
                <div class="value {c3_val_cls}">{c3_arrow} {mco_delta:+.2f} pp</div>
                <div class="delta">{mco_baseline_current:.2f}% &rarr; {mco_projected_12m:.2f}%</div>
            </div>
            <div class="agent-kpi kpi-accent">
                <div class="label">Analog Applied</div>
                <div class="value small">{analog_name}</div>
                <div class="delta">{current_status} &rarr; {future_status} · Step {STEP_TABLE[step_key]['step']:+d}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # =====================================================================
        # EMPTY STATE — invalid transition
        # =====================================================================
        _valid_futures = [s for s in STATUS_OPTIONS
                          if s != current_status and (current_status, s) in STEP_TABLE]
        _chips_html = ''.join(f'<span>{s}</span>' for s in _valid_futures) \
            if _valid_futures else '<span>None available</span>'
        st.markdown(f"""
        <div class="agent-empty">
            <div class="icon">!</div>
            <div>
                <h3>No analog defined for this transition</h3>
                <p>The combination <b>{current_status} &rarr; {future_status}</b> is not
                mapped in the Step Table. Pick a different Future Status to project market
                share, or review the mapping in Business Rules.</p>
                <div class="suggest">
                    <span style="color:var(--text-muted); background:transparent; padding:3px 0;">Valid from {current_status}:</span>
                    {_chips_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # FOOTER META (bottom of page)
    # =========================================================================
    st.markdown(
        f'<div class="agent-footer">'
        f'Data as of Mar 2026<span class="dot">·</span>'
        f'Source: Xponent (Plantrak) via Dataiku<span class="dot">·</span>'
        f'Analog: {analog_name}<span class="dot">·</span>'
        f'Forecast: Apr 2026 – Dec 2027<span class="dot">·</span>'
        f'Pfizer Confidential'
        f'</div>',
        unsafe_allow_html=True,
    )
