import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import dataiku

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
        font-family: 'Manrope', sans-serif;
        font-size: 20px;
        font-weight: 800;
        color: var(--navy-600);
        border-right: 1px solid var(--hairline);
        padding-right: 18px;
        letter-spacing: -0.02em;
    }
    .pfizer-header h1 {
        color: var(--navy-900);
        font-family: 'Manrope', sans-serif;
        font-size: 16px;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.01em;
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
    [data-testid="stDataFrame"] {
        border: 1px solid var(--hairline);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] th {
        background: var(--navy-900) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Info box */
    .stAlert {
        background: rgba(28,79,192,0.04) !important;
        border: 1px solid rgba(28,79,192,0.12) !important;
        border-radius: 12px !important;
        color: var(--navy-900) !important;
        font-family: 'Inter', sans-serif !important;
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
st.markdown("""
<div class="pfizer-header">
    <span class="pfizer-logo">Pfizer</span>
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
    st.dataframe(step_df, use_container_width=True, hide_index=True)
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
    st.dataframe(analog_df, use_container_width=True, hide_index=True)
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
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SCENARIO INPUTS</div>', unsafe_allow_html=True)

        selected_mco = st.selectbox(
            "Select MCO (type to search)",
            MCO_LIST,
            index=0,
            placeholder="Type MCO name to search..."
        )

        current_status, payer_type, ocgrp_contrib = get_mco_metadata(selected_mco)
        st.text_input("Current Status", value=current_status, disabled=True)

        if current_status in STATUS_OPTIONS:
            future_options = [s for s in STATUS_OPTIONS if s != current_status]
        else:
            future_options = STATUS_OPTIONS

        future_status = st.selectbox("Future Status", future_options)
        selected_change_month = st.selectbox("Change Month", CHANGE_MONTH_OPTIONS, index=6)
        change_idx = CHANGE_MONTH_IDX_MAP[selected_change_month]

        step_key = (current_status, future_status)
        if step_key in STEP_TABLE:
            info = STEP_TABLE[step_key]
            st.markdown(f"""
            <div class="scenario-box">
                <h4>Scenario Details</h4>
                <p><b>Analog:</b> {info['analog']}</p>
                <p><b>Step:</b> {info['step']} | <b>Reverse:</b> {info['reverse']}</p>
                <p><b>Transition:</b> {current_status} &rarr; {future_status}</p>
                <p><b>Payer Type:</b> {payer_type}</p>
                <p><b>OCGRP Contribution:</b> {ocgrp_contrib}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="scenario-box">
                <h4>Scenario Details</h4>
                <p><b>Transition:</b> {current_status} &rarr; {future_status}</p>
                <p><b>Payer Type:</b> {payer_type}</p>
                <p><b>OCGRP Contribution:</b> {ocgrp_contrib}</p>
                <p style="color:#E03C31;"><b>No analog defined for this transition</b></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.button("Back to Home", on_click=go_to_landing, use_container_width=True)

    # =========================================================================
    # COMPUTE
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
    # CHART — NATIONAL MARKET SHARE
    # =========================================================================
    if step_key in STEP_TABLE:
        with st.spinner("Computing national roll-up..."):
            baseline_natl_ms, projected_natl_ms = compute_national_ms(selected_mco, projected, change_idx)

        st.markdown('<p class="chart-title">National Market Share Trend</p>', unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(N_ACTUAL)), y=baseline_natl_ms[:N_ACTUAL],
            mode='lines+markers', name='Actual National MS',
            line=dict(color=PFZ_DARK_BLUE, width=2.5), marker=dict(size=4),
            hovertemplate='%{text}<br>MS: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(N_ACTUAL)],
        ))
        fig.add_trace(go.Scatter(
            x=list(range(N_ACTUAL - 1, N_TOTAL)), y=baseline_natl_ms[N_ACTUAL - 1:],
            mode='lines', name='Baseline (no change)',
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate='%{text}<br>Baseline: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(N_ACTUAL - 1, N_TOTAL)],
        ))
        fig.add_trace(go.Scatter(
            x=list(range(change_idx, N_TOTAL)), y=projected_natl_ms[change_idx:],
            mode='lines+markers', name='Projected (post change)',
            line=dict(color=PFZ_RED, width=2.5), marker=dict(size=5),
            fill='tonexty', fillcolor='rgba(239, 68, 68, 0.06)',
            hovertemplate='%{text}<br>Projected: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(change_idx, N_TOTAL)],
        ))

        fig.add_shape(type="line", x0=change_idx, x1=change_idx,
                      y0=0, y1=1, yref="paper",
                      line=dict(color=PFZ_ORANGE, width=2, dash="dash"))
        fig.add_annotation(x=change_idx, y=1.05, yref="paper",
                           text="Status Change", showarrow=False,
                           font=dict(color=PFZ_ORANGE, size=9))

        all_v = baseline_natl_ms + projected_natl_ms[change_idx:]
        valid_v = [v for v in all_v if v > 0]
        y_lo = min(valid_v) - 0.5 if valid_v else 0
        y_hi = max(valid_v) + 0.5 if valid_v else 100

        tick_idx = list(range(0, N_TOTAL, 6))
        tick_lbl = [MONTH_LABELS[i] for i in tick_idx]

        fig.update_layout(
            xaxis=dict(tickmode='array', tickvals=tick_idx, ticktext=tick_lbl,
                       tickfont=dict(size=10, color=PFZ_GRAY, family='Inter'), showgrid=False),
            yaxis=dict(title='National Market Share (%)', ticksuffix='%',
                       range=[y_lo, y_hi], gridcolor='rgba(15,23,42,0.05)',
                       tickfont=dict(size=10, color=PFZ_GRAY, family='Inter'),
                       title_font=dict(size=11, color=PFZ_DARK_BLUE, family='Manrope')),
            legend=dict(orientation='h', x=0, y=1.12, font=dict(size=10, color=PFZ_GRAY, family='Inter')),
            plot_bgcolor=PFZ_WHITE, paper_bgcolor='rgba(0,0,0,0)',
            height=380, margin=dict(l=50, r=20, t=50, b=30),
            hovermode='x unified',
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # =========================================================================
        # NATIONAL IMPACT METRICS
        # =========================================================================
        st.markdown('<div class="impact-header">NATIONAL MARKET SHARE IMPACT</div>', unsafe_allow_html=True)

        natl_baseline_current = baseline_natl_ms[N_ACTUAL - 1]
        natl_projected_12m = projected_natl_ms[min(change_idx + 12, N_TOTAL - 1)]
        natl_delta = natl_projected_12m - natl_baseline_current

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card border-positive"><div class="label">Baseline National MS</div>'
                        f'<div class="value positive">{natl_baseline_current:.2f}%</div></div>',
                        unsafe_allow_html=True)
        with c2:
            cls = "negative" if natl_projected_12m < natl_baseline_current else "positive"
            st.markdown(f'<div class="metric-card border-{cls}"><div class="label">Projected National MS (12m)</div>'
                        f'<div class="value {cls}">{natl_projected_12m:.2f}%</div></div>',
                        unsafe_allow_html=True)
        with c3:
            cls = "negative" if natl_delta < 0 else "positive"
            arrow = "&#9660;" if natl_delta < 0 else "&#9650;"
            st.markdown(f'<div class="metric-card border-{cls}"><div class="label">National Delta</div>'
                        f'<div class="value {cls}">{arrow} {natl_delta:+.2f} pp</div></div>',
                        unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card border-accent"><div class="label">Analog Used</div>'
                        f'<div class="value accent">{analog_name}</div></div>',
                        unsafe_allow_html=True)

        # =========================================================================
        # MCO-LEVEL CHART
        # =========================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="chart-title">{selected_mco} — Market Share Trend</p>', unsafe_allow_html=True)

        fig_mco = go.Figure()
        fig_mco.add_trace(go.Scatter(
            x=list(range(N_ACTUAL)), y=baseline_ms[:N_ACTUAL],
            mode='lines+markers', name='Actual MCO MS',
            line=dict(color=PFZ_DARK_BLUE, width=2.5), marker=dict(size=4),
            hovertemplate='%{text}<br>MS: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(N_ACTUAL)],
        ))
        fig_mco.add_trace(go.Scatter(
            x=list(range(N_ACTUAL - 1, N_TOTAL)), y=baseline_ms[N_ACTUAL - 1:],
            mode='lines', name='Baseline (no change)',
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate='%{text}<br>Baseline: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(N_ACTUAL - 1, N_TOTAL)],
        ))
        fig_mco.add_trace(go.Scatter(
            x=list(range(change_idx, N_TOTAL)), y=projected[change_idx:],
            mode='lines+markers', name='Projected (post change)',
            line=dict(color=PFZ_RED, width=2.5), marker=dict(size=5),
            fill='tonexty', fillcolor='rgba(239, 68, 68, 0.06)',
            hovertemplate='%{text}<br>Projected: %{y:.2f}%<extra></extra>',
            text=[MONTH_LABELS[i] for i in range(change_idx, N_TOTAL)],
        ))

        fig_mco.add_shape(type="line", x0=change_idx, x1=change_idx,
                          y0=0, y1=1, yref="paper",
                          line=dict(color=PFZ_ORANGE, width=2, dash="dash"))
        fig_mco.add_annotation(x=change_idx, y=1.05, yref="paper",
                               text="Status Change", showarrow=False,
                               font=dict(color=PFZ_ORANGE, size=9))

        mco_all_v = baseline_ms + projected[change_idx:]
        mco_valid_v = [v for v in mco_all_v if v > 0]
        mco_y_lo = min(mco_valid_v) - 2 if mco_valid_v else 0
        mco_y_hi = max(mco_valid_v) + 2 if mco_valid_v else 100

        fig_mco.update_layout(
            xaxis=dict(tickmode='array', tickvals=tick_idx, ticktext=tick_lbl,
                       tickfont=dict(size=10, color=PFZ_GRAY, family='Inter'), showgrid=False),
            yaxis=dict(title=f'{selected_mco} Market Share (%)', ticksuffix='%',
                       range=[mco_y_lo, mco_y_hi], gridcolor='rgba(15,23,42,0.05)',
                       tickfont=dict(size=10, color=PFZ_GRAY, family='Inter'),
                       title_font=dict(size=11, color=PFZ_DARK_BLUE, family='Manrope')),
            legend=dict(orientation='h', x=0, y=1.12, font=dict(size=10, color=PFZ_GRAY, family='Inter')),
            plot_bgcolor=PFZ_WHITE, paper_bgcolor='rgba(0,0,0,0)',
            height=380, margin=dict(l=50, r=20, t=50, b=30),
            hovermode='x unified',
        )

        st.plotly_chart(fig_mco, use_container_width=True, config={'displayModeBar': False})

        # =========================================================================
        # MCO-LEVEL IMPACT METRICS
        # =========================================================================
        st.markdown('<div class="impact-header">MCO-LEVEL IMPACT</div>', unsafe_allow_html=True)

        mco_baseline_current = baseline_ms[N_ACTUAL - 1]
        mco_projected_12m = projected[min(change_idx + 12, N_TOTAL - 1)]
        mco_delta = mco_projected_12m - mco_baseline_current

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card border-positive"><div class="label">Current MCO MS</div>'
                        f'<div class="value positive">{mco_baseline_current:.2f}%</div></div>',
                        unsafe_allow_html=True)
        with c2:
            cls = "negative" if mco_projected_12m < mco_baseline_current else "positive"
            st.markdown(f'<div class="metric-card border-{cls}"><div class="label">Projected MCO MS (12m)</div>'
                        f'<div class="value {cls}">{mco_projected_12m:.2f}%</div></div>',
                        unsafe_allow_html=True)
        with c3:
            cls = "negative" if mco_delta < 0 else "positive"
            arrow = "&#9660;" if mco_delta < 0 else "&#9650;"
            st.markdown(f'<div class="metric-card border-{cls}"><div class="label">MCO Delta</div>'
                        f'<div class="value {cls}">{arrow} {mco_delta:+.2f} pp</div></div>',
                        unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card border-accent"><div class="label">Analog Used</div>'
                        f'<div class="value accent">{analog_name}</div></div>',
                        unsafe_allow_html=True)
    else:
        st.info("Select a valid status transition to see national impact.")

    # Footer
    st.markdown(f'<p style="text-align:center;color:{PFZ_GRAY};font-family:Inter,sans-serif;font-size:10px;margin-top:18px;'
                f'padding-top:10px;border-top:1px solid rgba(15,23,42,0.08);">'
                f'Data Source: Xponent (Plantrak) via Dataiku &bull; '
                f'Analog: {analog_name} &bull; '
                f'Forecast: Apr 2026 &ndash; Dec 2027 &bull; '
                f'Pfizer Confidential</p>', unsafe_allow_html=True)
