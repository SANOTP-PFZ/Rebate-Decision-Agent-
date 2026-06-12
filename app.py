import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Rebate Decision Agent",
    layout="wide",
    initial_sidebar_state="auto"
)

# =============================================================================
# PFIZER BRAND COLORS
# =============================================================================
PFZ_BLUE = '#0093D0'
PFZ_DARK_BLUE = '#002F6C'
PFZ_RED = '#E03C31'
PFZ_ORANGE = '#F5A623'
PFZ_GRAY = '#63666A'
PFZ_WHITE = '#FFFFFF'

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .stApp { background-color: #F7FAFC; }

    .pfizer-header {
        background: #002F6C;
        padding: 12px 28px;
        display: flex;
        align-items: center;
        gap: 20px;
        border-radius: 6px;
        margin-bottom: 1.2rem;
    }
    .pfizer-logo {
        font-size: 22px;
        font-weight: 900;
        color: #0093D0;
        font-style: italic;
        border-right: 2px solid rgba(0,147,208,0.4);
        padding-right: 20px;
    }
    .pfizer-header h1 {
        color: white;
        font-size: 18px;
        margin: 0;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* Landing page */
    .greeting {
        font-size: 36px;
        font-weight: 700;
        color: #002F6C;
        text-align: center;
        margin: 40px 0 8px 0;
    }
    .disclaimer-box {
        background: white;
        border-radius: 10px;
        padding: 24px 32px;
        border: 1px solid #D0DEE8;
        box-shadow: 0 2px 8px rgba(0,47,108,0.05);
        max-width: 700px;
        margin: 20px auto 30px auto;
    }
    .disclaimer-box h3 {
        color: #002F6C;
        font-size: 14px;
        font-weight: 700;
        margin: 0 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #0093D0;
    }
    .disclaimer-box p, .disclaimer-box li {
        color: #555;
        font-size: 12px;
        line-height: 1.7;
    }
    .disclaimer-box ul {
        padding-left: 18px;
        margin: 6px 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F0F6FC !important;
        width: 320px !important;
        border-right: 2px solid #0093D0 !important;
    }
    section[data-testid="stSidebar"] label {
        color: #002F6C !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        border-color: #0093D0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {
        color: #002F6C !important;
    }
    section[data-testid="stSidebar"] .stSelectbox svg {
        fill: #0093D0 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #EDF1F5 !important;
        color: #002F6C !important;
        border: 1px solid #0093D0 !important;
        -webkit-text-fill-color: #002F6C !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input:disabled {
        background-color: #E8F4FD !important;
        color: #002F6C !important;
        -webkit-text-fill-color: #002F6C !important;
        opacity: 1 !important;
        font-weight: 600 !important;
        border: 1px solid #B0D4E8 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: #0093D0 !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #002F6C !important;
    }

    .sidebar-header {
        color: #002F6C;
        font-size: 14px;
        font-weight: 700;
        padding-bottom: 6px;
        border-bottom: 2px solid #0093D0;
        margin-bottom: 10px;
    }
    .scenario-box {
        background: #E8F4FD;
        border: 1px solid #0093D0;
        border-radius: 5px;
        padding: 12px;
        margin-top: 14px;
    }
    .scenario-box h4 {
        color: #002F6C; margin: 0 0 6px 0;
        font-size: 11px; font-weight: 700;
        text-transform: uppercase;
    }
    .scenario-box p {
        color: #333; font-size: 11px; margin: 2px 0;
    }

    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 16px 10px;
        text-align: center;
        border: 1px solid #D0DEE8;
        box-shadow: 0 1px 4px rgba(0,47,108,0.06);
    }
    .metric-card .label {
        font-size: 10px; color: #63666A;
        text-transform: uppercase; letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 22px; font-weight: 800;
    }
    .metric-card .value.negative { color: #E03C31; }
    .metric-card .value.positive { color: #002F6C; }
    .metric-card .value.accent { color: #0093D0; }

    .impact-header {
        background: #002F6C;
        color: white;
        padding: 8px;
        border-radius: 4px;
        text-align: center;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 6px 0 10px 0;
    }

    .section-divider {
        border-top: 2px solid #D0DEE8;
        margin: 16px 0 12px 0;
    }

    /* Primary buttons (landing page) */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: #002F6C !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: #0093D0 !important;
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background: white !important;
        color: #002F6C !important;
        font-weight: 600 !important;
        border: 2px solid #0093D0 !important;
        border-radius: 6px !important;
        padding: 12px !important;
    }
    .stButton > button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background: #E8F4FD !important;
        border-color: #002F6C !important;
    }

    /* Dataframe / table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #D0DEE8;
        border-radius: 6px;
    }
    [data-testid="stDataFrame"] th {
        background: #002F6C !important;
        color: white !important;
    }

    /* Info box */
    .stAlert {
        background: #E8F4FD !important;
        border: 1px solid #0093D0 !important;
        color: #002F6C !important;
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

    first_name = get_first_name()
    st.markdown(f'<div class="greeting">Hi, {first_name}</div>', unsafe_allow_html=True)

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
    st.markdown('<h2 style="color:#002F6C; margin-bottom:4px;">Business Rules & Methodology</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#63666A; font-size:13px; margin-bottom:20px;">How the Rebate Decision Agent computes market share projections</p>', unsafe_allow_html=True)

    # --- Section 1: Data Sources ---
    st.markdown('<h4 style="color:#002F6C; border-bottom:2px solid #0093D0; padding-bottom:4px;">Data Sources</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:white; border:1px solid #E4ECF2; border-radius:8px; padding:16px; margin-bottom:12px;">
            <p style="font-weight:700; color:#002F6C; margin:0 0 6px 0;">Market Share Table</p>
            <p style="font-size:12px; color:#555; margin:2px 0;">~2,723 MCOs with 36 months of baseline market share data (Jan 2025 - Dec 2027). Months Jan'25 - Mar'26 are actuals; Apr'26 onward are projected.</p>
        </div>
        <div style="background:white; border:1px solid #E4ECF2; border-radius:8px; padding:16px;">
            <p style="font-weight:700; color:#002F6C; margin:0 0 6px 0;">OCGRP Claims Table</p>
            <p style="font-size:12px; color:#555; margin:2px 0;">~2,730 MCOs with monthly OCGRP claim volumes. Used to convert MCO-level market share into claim counts for national roll-up calculations.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white; border:1px solid #E4ECF2; border-radius:8px; padding:16px; margin-bottom:12px;">
            <p style="font-weight:700; color:#002F6C; margin:0 0 6px 0;">Analog Curves</p>
            <p style="font-size:12px; color:#555; margin:2px 0;">23-month rate-of-change curves derived from historical formulary changes. Three analogs: BCBS (Covered to Preferred), Providence (Covered to Not Covered), Blended (Preferred to Not Covered).</p>
        </div>
        <div style="background:white; border:1px solid #E4ECF2; border-radius:8px; padding:16px;">
            <p style="font-weight:700; color:#002F6C; margin:0 0 6px 0;">Step Table</p>
            <p style="font-size:12px; color:#555; margin:2px 0;">Maps every possible status transition (Current to Future) to the appropriate analog curve with direction (Reverse) and magnitude (Step) parameters.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 2: Projection Formula ---
    st.markdown('<h4 style="color:#002F6C; border-bottom:2px solid #0093D0; padding-bottom:4px;">Projection Formula</h4>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#F0F6FC; border-left:4px solid #0093D0; padding:16px 20px; border-radius:4px; margin:12px 0;">
        <p style="font-size:14px; color:#002F6C; font-weight:700; margin:0 0 8px 0;">For each month M from Change Month onward:</p>
        <p style="font-size:16px; color:#002F6C; font-family:monospace; margin:0; background:white; padding:10px 14px; border-radius:4px; display:inline-block;">
            Projected[M] = Baseline[M] &times; (1 + analog_rate &times; Reverse)
        </p>
        <ul style="font-size:12px; color:#555; margin-top:12px;">
            <li><b>Baseline[M]</b> &mdash; Original forecasted market share from the Market Share table</li>
            <li><b>analog_rate</b> &mdash; Month-over-month relative difference value for the selected analog</li>
            <li><b>Reverse</b> &mdash; +1 for downward status changes, -1 for upward status changes</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 3: Transition Mapping ---
    st.markdown('<h4 style="color:#002F6C; border-bottom:2px solid #0093D0; padding-bottom:4px;">Status Transition Mapping</h4>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px; color:#555;">Each formulary status change maps to a specific analog and direction:</p>', unsafe_allow_html=True)

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

    # --- Section 4: National Roll-Up ---
    st.markdown('<h4 style="color:#002F6C; border-bottom:2px solid #0093D0; padding-bottom:4px;">National Roll-Up Logic</h4>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white; border:1px solid #E4ECF2; border-radius:8px; padding:18px 22px; margin:10px 0;">
        <p style="font-size:12px; color:#555; margin:0 0 10px 0;">To compute the national-level impact of a single MCO's status change:</p>
        <ol style="font-size:12px; color:#333; line-height:1.8; padding-left:18px;">
            <li>For the <b>selected MCO</b>: apply projected (post-change) market share</li>
            <li>For <b>all other MCOs</b>: retain their baseline market share</li>
            <li>Compute per MCO: <code>Nurtec Claims = Market Share &times; OCGRP Claims</code></li>
            <li>Sum across all MCOs to get national totals</li>
            <li>National MS = Total Nurtec Claims &divide; Total OCGRP Claims</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 5: Timeline ---
    st.markdown('<h4 style="color:#002F6C; border-bottom:2px solid #0093D0; padding-bottom:4px;">Data Timeline</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:#E8F4FD; border-radius:8px; padding:14px 18px; text-align:center;">
            <p style="font-size:11px; color:#63666A; margin:0; text-transform:uppercase;">Actual Period</p>
            <p style="font-size:18px; font-weight:700; color:#002F6C; margin:4px 0;">Jan 2025 - Mar 2026</p>
            <p style="font-size:11px; color:#555; margin:0;">15 months of historical data</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#FFF8E1; border-radius:8px; padding:14px 18px; text-align:center;">
            <p style="font-size:11px; color:#63666A; margin:0; text-transform:uppercase;">Forecast Period</p>
            <p style="font-size:18px; font-weight:700; color:#002F6C; margin:4px 0;">Apr 2026 - Dec 2027</p>
            <p style="font-size:11px; color:#555; margin:0;">21 months of projected data</p>
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
    # DATA LOADING
    # =========================================================================
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Rebate_backend_implementation.xlsx')
    _file_mtime = os.path.getmtime(DATA_FILE)

    @st.cache_data(ttl=60)
    def load_data(_mtime):
        """Load all 4 sheets. _mtime param busts cache when file changes."""
        df_ms_raw = pd.read_excel(DATA_FILE, sheet_name='Market Share', header=None)
        headers_ms = df_ms_raw.iloc[6].tolist()
        df_ms = df_ms_raw.iloc[8:].copy()
        df_ms.columns = headers_ms
        df_ms = df_ms.reset_index(drop=True)
        df_ms = df_ms.dropna(subset=['MCO_NM'])

        df_oc_raw = pd.read_excel(DATA_FILE, sheet_name='OCGRP claims', header=None)
        headers_oc = df_oc_raw.iloc[5].tolist()
        df_oc = df_oc_raw.iloc[7:].copy()
        df_oc.columns = headers_oc
        df_oc = df_oc.reset_index(drop=True)
        df_oc = df_oc.dropna(subset=['MCO_NM'])

        df_analog_raw = pd.read_excel(DATA_FILE, sheet_name='Analogs', header=None)
        analog_data = df_analog_raw.iloc[17:40, 0:4].copy()
        analog_data.columns = ['Month', 'BCBS', 'Providence', 'Blended']
        analog_data = analog_data.reset_index(drop=True)
        analog_curves = {
            'BCBS': [float(x) for x in analog_data['BCBS'].tolist()],
            'Providence': [float(x) for x in analog_data['Providence'].tolist()],
            'Blended': [float(x) for x in analog_data['Blended'].tolist()],
        }

        df_step_raw = pd.read_excel(DATA_FILE, sheet_name='Analog Implementation', header=None)
        step_data = df_step_raw.iloc[4:14, 0:5].copy()
        step_data.columns = ['Current', 'Future', 'Analog', 'Step', 'Reverse']
        step_data = step_data.reset_index(drop=True)
        step_table = {}
        for _, row in step_data.iterrows():
            key = (str(row['Current']).strip(), str(row['Future']).strip())
            step_table[key] = {
                'analog': str(row['Analog']).strip(),
                'step': int(row['Step']),
                'reverse': int(row['Reverse']),
            }
        return df_ms, df_oc, analog_curves, step_table

    df_market_share, df_ocgrp, ANALOG_CURVES, STEP_TABLE = load_data(_file_mtime)

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
    def get_mco_ms(mco_name):
        row = df_market_share[df_market_share['MCO_NM'] == mco_name]
        if row.empty:
            return [0.0] * N_TOTAL
        values = row.iloc[0, 4:40].tolist()
        ms = []
        for v in values:
            try:
                val = float(v) * 100
                ms.append(val)
            except (TypeError, ValueError):
                ms.append(0.0)
        return ms

    def get_mco_ocgrp(mco_name):
        row = df_ocgrp[df_ocgrp['MCO_NM'] == mco_name]
        if row.empty:
            return [0.0] * N_TOTAL
        values = row.iloc[0, 1:37].tolist()
        claims = []
        for v in values:
            try:
                claims.append(float(v))
            except (TypeError, ValueError):
                claims.append(0.0)
        return claims

    def get_mco_metadata(mco_name):
        row = df_market_share[df_market_share['MCO_NM'] == mco_name]
        if row.empty:
            return "Data not available yet", "Data not available yet", "N/A"
        status = row.iloc[0, 1]
        payer = row.iloc[0, 2]
        contrib = row.iloc[0, 3]
        status = str(status).strip() if pd.notna(status) and str(status).strip() not in ['', 'nan', 'None'] else "Data not available yet"
        payer = str(payer).strip() if pd.notna(payer) and str(payer).strip() not in ['', 'nan', 'None'] else "Data not available yet"
        try:
            contrib = f"{float(contrib) * 100:.2f}%" if pd.notna(contrib) else "N/A"
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
    # CHART
    # =========================================================================
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(N_ACTUAL)), y=baseline_ms[:N_ACTUAL],
        mode='lines+markers', name='Actual',
        line=dict(color=PFZ_DARK_BLUE, width=2.5), marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=list(range(N_ACTUAL - 1, N_TOTAL)), y=baseline_ms[N_ACTUAL - 1:],
        mode='lines', name='Baseline (no change)',
        line=dict(color='#B0BEC5', width=2, dash='dash'),
    ))
    if step_key in STEP_TABLE:
        fig.add_trace(go.Scatter(
            x=list(range(change_idx, N_TOTAL)), y=projected[change_idx:],
            mode='lines+markers', name='Projected (post change)',
            line=dict(color=PFZ_RED, width=2.5), marker=dict(size=4),
        ))

    fig.add_shape(type="line", x0=change_idx, x1=change_idx,
                  y0=0, y1=1, yref="paper",
                  line=dict(color=PFZ_ORANGE, width=2, dash="dash"))
    fig.add_annotation(x=change_idx, y=1.05, yref="paper",
                       text="Status Change", showarrow=False,
                       font=dict(color=PFZ_ORANGE, size=9))

    all_v = baseline_ms + (projected[change_idx:] if step_key in STEP_TABLE else [])
    valid_v = [v for v in all_v if v > 0]
    y_lo = min(valid_v) - 2 if valid_v else 0
    y_hi = max(valid_v) + 2 if valid_v else 100

    tick_idx = list(range(0, N_TOTAL, 6))
    tick_lbl = [MONTH_LABELS[i] for i in tick_idx]

    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=tick_idx, ticktext=tick_lbl,
                   tickfont=dict(size=10, color=PFZ_GRAY), showgrid=False),
        yaxis=dict(title='Market Share (%)', ticksuffix='%',
                   range=[y_lo, y_hi], gridcolor='#F0F2F5',
                   tickfont=dict(size=10, color=PFZ_GRAY),
                   title_font=dict(size=11, color=PFZ_DARK_BLUE)),
        legend=dict(orientation='h', x=0, y=1.12, font=dict(size=10, color=PFZ_GRAY)),
        plot_bgcolor=PFZ_WHITE, paper_bgcolor=PFZ_WHITE,
        height=380, margin=dict(l=50, r=20, t=50, b=30),
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # =========================================================================
    # MCO-LEVEL IMPACT
    # =========================================================================
    st.markdown('<div class="impact-header">MCO-LEVEL IMPACT</div>', unsafe_allow_html=True)

    current_ms_val = baseline_ms[N_ACTUAL - 1]
    projected_12m_val = projected[min(change_idx + 12, N_TOTAL - 1)]
    delta = projected_12m_val - current_ms_val

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="label">Current MS</div>'
                    f'<div class="value positive">{current_ms_val:.1f}%</div></div>',
                    unsafe_allow_html=True)
    with c2:
        cls = "negative" if projected_12m_val < current_ms_val else "positive"
        st.markdown(f'<div class="metric-card"><div class="label">Projected MS (12m)</div>'
                    f'<div class="value {cls}">{projected_12m_val:.1f}%</div></div>',
                    unsafe_allow_html=True)
    with c3:
        cls = "negative" if delta < 0 else "positive"
        st.markdown(f'<div class="metric-card"><div class="label">Delta Impact</div>'
                    f'<div class="value {cls}">{delta:+.1f} pp</div></div>',
                    unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="label">Analog Used</div>'
                    f'<div class="value accent">{analog_name}</div></div>',
                    unsafe_allow_html=True)

    # =========================================================================
    # NATIONAL ROLL-UP
    # =========================================================================
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="impact-header">NATIONAL MARKET SHARE IMPACT</div>', unsafe_allow_html=True)

    if step_key in STEP_TABLE:
        baseline_natl_ms, projected_natl_ms = compute_national_ms(selected_mco, projected, change_idx)

        natl_baseline_current = baseline_natl_ms[N_ACTUAL - 1]
        natl_projected_12m = projected_natl_ms[min(change_idx + 12, N_TOTAL - 1)]
        natl_delta = natl_projected_12m - natl_baseline_current

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="label">Baseline National MS</div>'
                        f'<div class="value positive">{natl_baseline_current:.2f}%</div></div>',
                        unsafe_allow_html=True)
        with c2:
            cls = "negative" if natl_projected_12m < natl_baseline_current else "positive"
            st.markdown(f'<div class="metric-card"><div class="label">Projected National MS (12m)</div>'
                        f'<div class="value {cls}">{natl_projected_12m:.2f}%</div></div>',
                        unsafe_allow_html=True)
        with c3:
            cls = "negative" if natl_delta < 0 else "positive"
            st.markdown(f'<div class="metric-card"><div class="label">National Delta</div>'
                        f'<div class="value {cls}">{natl_delta:+.2f} pp</div></div>',
                        unsafe_allow_html=True)
    else:
        st.info("Select a valid status transition to see national impact.")

    # Footer
    st.markdown(f'<p style="text-align:center;color:{PFZ_GRAY};font-size:10px;margin-top:14px;'
                f'padding-top:8px;border-top:1px solid #E4ECF2;">'
                f'Data Source: Xponent (Plantrak) via Dataiku &bull; '
                f'Analog: {analog_name} &bull; '
                f'Forecast: Apr 2026 &ndash; Dec 2027 &bull; '
                f'Pfizer Confidential</p>', unsafe_allow_html=True)
