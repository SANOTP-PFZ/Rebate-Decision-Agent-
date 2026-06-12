import streamlit as st
import plotly.graph_objects as go
import numpy as np

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="NURTEC PAYER MODEL",
    layout="wide",
    initial_sidebar_state="expanded"
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

    /* Header */
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

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F4F8FC !important;
        width: 320px !important;
    }
    section[data-testid="stSidebar"] label {
        color: #002F6C !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
    }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {
        color: #222 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox svg {
        fill: #0093D0 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #EDF1F5 !important;
        color: #222222 !important;
        border: 1px solid #C8D6E0 !important;
        -webkit-text-fill-color: #222222 !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input:disabled {
        background-color: #E8EDF2 !important;
        color: #002F6C !important;
        -webkit-text-fill-color: #002F6C !important;
        opacity: 1 !important;
        font-weight: 600 !important;
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
        background: #FFFDF5;
        border: 1px solid #E8D48C;
        border-radius: 5px;
        padding: 12px;
        margin-top: 14px;
    }
    .scenario-box h4 {
        color: #8B6F00; margin: 0 0 6px 0;
        font-size: 11px; font-weight: 700;
        text-transform: uppercase;
    }
    .scenario-box p {
        color: #555; font-size: 11px; margin: 2px 0;
    }

    /* Metrics */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 16px 10px;
        text-align: center;
        border: 1px solid #E4ECF2;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
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

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA
# =============================================================================
MCO_DATA = {
    'CVS HEALTH-ADMINISTERED PLANS - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 43.2, 'contribution': 4.85,
    },
    'UHG / OPTUM RX - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 41.5, 'contribution': 3.99,
    },
    'EXPRESS SCRIPTS - ADMINISTERED PLANS - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 44.3, 'contribution': 3.75,
    },
    'CIGNA HEALTH PLAN - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 42.8, 'contribution': 3.02,
    },
    'AETNA HEALTH PLAN - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 40.2, 'contribution': 2.72,
    },
    'HUMANA PLANS - MEDICARE': {
        'status': 'Not Covered', 'payer_type': 'MEDICARE',
        'base_ms': 19.8, 'contribution': 2.00,
    },
    'ANTHEM ALL OTHER PLANS - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 43.8, 'contribution': 2.15,
    },
    'UHG / AARP MEDICARERX PLANS - MEDICARE': {
        'status': 'Specialty', 'payer_type': 'MEDICARE',
        'base_ms': 41.8, 'contribution': 3.99,
    },
    'FEDERAL EMPLOYEE PROGRAM PLANS - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 65.0, 'contribution': 2.04,
    },
    'WELLCARE - MEDICARE': {
        'status': 'Specialty', 'payer_type': 'MEDICARE',
        'base_ms': 57.2, 'contribution': 1.67,
    },
    'MEDICAID CA - FFS_MEDICAID': {
        'status': 'Covered', 'payer_type': 'MEDICAID',
        'base_ms': 55.2, 'contribution': 1.99,
    },
    'MEDICAID NY - FFS_MEDICAID': {
        'status': 'Covered', 'payer_type': 'MEDICAID',
        'base_ms': 45.5, 'contribution': 1.65,
    },
    'BCBS HCSC / BCBS TEXAS - COMMERCIAL': {
        'status': 'Preferred', 'payer_type': 'COMMERCIAL',
        'base_ms': 38.1, 'contribution': 1.57,
    },
    'BLUE CROSS BLUE SHIELD OF NORTH CAROLINA - COMMERCIAL': {
        'status': 'Covered', 'payer_type': 'COMMERCIAL',
        'base_ms': 36.5, 'contribution': 0.89,
    },
}

STATUS_OPTIONS = ['Not Covered', 'Covered', 'Preferred', 'Specialty']

STEP_TABLE = {
    ('Not Covered', 'Covered'):     {'analog': 'Providence', 'step': 1, 'reverse': -1},
    ('Not Covered', 'Preferred'):   {'analog': 'Blended', 'step': 2, 'reverse': -1},
    ('Preferred', 'Covered'):       {'analog': 'BCBS', 'step': -1, 'reverse': -1},
    ('Not Covered', 'Specialty'):   {'analog': 'Providence', 'step': 1, 'reverse': -1},
    ('Preferred', 'Specialty'):     {'analog': 'BCBS', 'step': -1, 'reverse': -1},
    ('Specialty', 'Preferred'):     {'analog': 'BCBS', 'step': 1, 'reverse': 1},
    ('Specialty', 'Not Covered'):   {'analog': 'Providence', 'step': -1, 'reverse': 1},
    ('Covered', 'Preferred'):       {'analog': 'BCBS', 'step': 1, 'reverse': 1},
    ('Preferred', 'Not Covered'):   {'analog': 'Blended', 'step': -2, 'reverse': 1},
    ('Covered', 'Not Covered'):     {'analog': 'Providence', 'step': -1, 'reverse': 1},
}

ANALOG_CURVES = {
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
}

MONTH_TICKS = [
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
# Map change month labels to index in 0..35
CHANGE_MONTH_IDX_MAP = {label: i + 15 for i, label in enumerate(CHANGE_MONTH_OPTIONS)}

N_ACTUAL = 15
N_TOTAL = 36


def generate_actual_ms(base_ms):
    np.random.seed(int(base_ms * 10))
    actual = []
    val = base_ms
    for _ in range(N_ACTUAL):
        val += np.random.uniform(-0.4, 0.5)
        actual.append(round(val, 2))
    return actual


def generate_baseline(actual_ms):
    last = actual_ms[-1]
    return actual_ms + [round(last + i * 0.04, 2) for i in range(N_TOTAL - N_ACTUAL)]


def apply_analog(baseline, change_idx, analog_curve, reverse):
    projected = baseline[:change_idx]
    for i in range(change_idx, N_TOTAL):
        m = i - change_idx
        rate = analog_curve[m] if m < len(analog_curve) else analog_curve[-1]
        projected.append(round(max(baseline[i] * (1 + rate * reverse), 2.0), 2))
    return projected


# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div class="pfizer-header">
    <span class="pfizer-logo">Pfizer</span>
    <h1>NURTEC PAYER MODEL</h1>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">SCENARIO INPUTS</div>', unsafe_allow_html=True)

    selected_mco = st.selectbox("Select MCO", list(MCO_DATA.keys()), index=0)
    mco_info = MCO_DATA[selected_mco]
    current_status = mco_info['status']

    st.text_input("Current Status", value=current_status, disabled=True)

    future_options = [s for s in STATUS_OPTIONS if s != current_status]
    future_status = st.selectbox("Future Status", future_options)

    selected_change_month = st.selectbox("Change Month", CHANGE_MONTH_OPTIONS, index=6)
    change_idx = CHANGE_MONTH_IDX_MAP[selected_change_month]

    st.markdown("")
    st.button("Run Scenario", use_container_width=True)

    step_key = (current_status, future_status)
    if step_key in STEP_TABLE:
        info = STEP_TABLE[step_key]
        st.markdown(f"""
        <div class="scenario-box">
            <h4>Scenario Details</h4>
            <p><b>Analog:</b> {info['analog']}</p>
            <p><b>Step:</b> {info['step']} | <b>Reverse:</b> {info['reverse']}</p>
            <p><b>Transition:</b> {current_status} &rarr; {future_status}</p>
            <p><b>Payer Type:</b> {mco_info['payer_type']}</p>
            <p><b>OCGRP Contribution:</b> {mco_info['contribution']:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No analog defined for this transition.")

# =============================================================================
# COMPUTE
# =============================================================================
step_key = (current_status, future_status)
actual_ms = generate_actual_ms(mco_info['base_ms'])
baseline = generate_baseline(actual_ms)

if step_key in STEP_TABLE:
    analog_name = STEP_TABLE[step_key]['analog']
    reverse = STEP_TABLE[step_key]['reverse']
    analog_curve = ANALOG_CURVES[analog_name]
else:
    analog_name = 'BCBS'
    reverse = 1
    analog_curve = ANALOG_CURVES['BCBS']

projected = apply_analog(baseline, change_idx, analog_curve, reverse)

# =============================================================================
# CHART
# =============================================================================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=list(range(N_ACTUAL)),
    y=actual_ms,
    mode='lines+markers',
    name='Actual',
    line=dict(color=PFZ_DARK_BLUE, width=2.5),
    marker=dict(size=4),
))

fig.add_trace(go.Scatter(
    x=list(range(N_ACTUAL - 1, N_TOTAL)),
    y=baseline[N_ACTUAL - 1:],
    mode='lines',
    name='Baseline (no change)',
    line=dict(color='#B0BEC5', width=2, dash='dash'),
))

fig.add_trace(go.Scatter(
    x=list(range(change_idx, N_TOTAL)),
    y=projected[change_idx:],
    mode='lines+markers',
    name='Projected (post change)',
    line=dict(color=PFZ_RED, width=2.5),
    marker=dict(size=4),
))

# Vertical marker
fig.add_shape(type="line", x0=change_idx, x1=change_idx,
              y0=0, y1=1, yref="paper",
              line=dict(color=PFZ_ORANGE, width=2, dash="dash"))
fig.add_annotation(x=change_idx, y=1.05, yref="paper",
                   text="Status Change", showarrow=False,
                   font=dict(color=PFZ_ORANGE, size=9))

# Axis range
all_v = actual_ms + baseline[N_ACTUAL-1:] + projected[change_idx:]
y_lo, y_hi = min(all_v) - 2, max(all_v) + 2

# Show every 6th month tick
tick_idx = list(range(0, N_TOTAL, 6))
tick_lbl = [MONTH_TICKS[i] for i in tick_idx]

fig.update_layout(
    xaxis=dict(tickmode='array', tickvals=tick_idx, ticktext=tick_lbl,
               tickfont=dict(size=10, color=PFZ_GRAY), showgrid=False),
    yaxis=dict(title='Market Share (%)', ticksuffix='%',
               range=[y_lo, y_hi], gridcolor='#F0F2F5',
               tickfont=dict(size=10, color=PFZ_GRAY),
               title_font=dict(size=11, color=PFZ_DARK_BLUE)),
    legend=dict(orientation='h', x=0, y=1.12, font=dict(size=10, color=PFZ_GRAY)),
    plot_bgcolor=PFZ_WHITE, paper_bgcolor=PFZ_WHITE,
    height=400,
    margin=dict(l=50, r=20, t=50, b=30),
    hovermode='x unified',
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# =============================================================================
# IMPACT SUMMARY
# =============================================================================
st.markdown('<div class="impact-header">IMPACT SUMMARY</div>', unsafe_allow_html=True)

current_ms_val = actual_ms[-1]
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

# Footer
st.markdown(f'<p style="text-align:center;color:{PFZ_GRAY};font-size:10px;margin-top:14px;'
            f'padding-top:8px;border-top:1px solid #E4ECF2;">'
            f'Data Source: Xponent (Plantrak) via Dataiku &bull; '
            f'Analog: {analog_name} &bull; '
            f'Forecast: Apr 2026 &ndash; Dec 2027 &bull; '
            f'Pfizer Confidential</p>', unsafe_allow_html=True)
