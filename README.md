# Nurtec Payer Model — Webapp Implementation Plan

## Overview

A Streamlit webapp hosted as a **Dataiku webapp** that allows business leads to simulate the impact of formulary status changes on Nurtec's market share at the MCO level. The user selects an MCO, defines a status transition, picks a change month, and sees the projected market share trend powered by historical analog curves.

---

## Architecture

```
+------------------+       +------------------+       +------------------+
|   Snowflake      | ----> |   Dataiku        | ----> |   Streamlit App  |
|   (source data)  |       |   (managed       |       |   (Dataiku       |
|                  |       |    datasets)     |       |    webapp)       |
+------------------+       +------------------+       +------------------+
```

- **Snowflake** stores the raw XPONENT claims data and MMIT formulary status data.
- **Dataiku** manages dataset refresh (scheduled recipes) so the app always reads latest data.
- **Streamlit** is the user-facing interface, reading from Dataiku datasets via `dataiku.Dataset()`.

---

## Required Datasets (in Dataiku)

| Dataset Name | Description | Source |
|---|---|---|
| `mco_current_status` | MCO name + current Nurtec formulary status (latest period from MMIT) | Snowflake MMIT table |
| `nurtec_xpo_share_pct` | Nurtec market share % by MCO by month (actuals Jan'25 - Mar'26, forecast Apr'26 - Dec'27) | Snowflake XPONENT + forecast logic |
| `ocgrp_xpo_claims` | OCGRP total claims by MCO by month (for contribution weighting) | Snowflake XPONENT |
| `analog_curves` | Month-over-month relative rate-of-change for BCBS, Providence, and Blended analogs | Pre-computed from analog analysis |

---

## App Components

### 1. Sidebar — User Inputs

| Component | Type | Behavior |
|---|---|---|
| MCO Selector | `st.selectbox` (searchable) | Lists all MCO names from `mco_current_status` |
| Current Status | `st.text_input` (disabled) | Auto-filled from dataset on MCO selection |
| Future Status | `st.selectbox` | Options: Not Covered, Covered, Preferred, Specialty (minus current) |
| Change Month | `st.selectbox` | Monthly options from next month through Dec 2027 |
| Multiplier | `st.slider` | Range 0.5–2.0, step 0.1, default 1.0 |
| Run Button | `st.button` | Triggers projection calculation |
| Scenario Info | `st.info` / `st.caption` | Shows which analog, step, reverse values will be used |

### 2. Main Area — Output

| Component | Type | Description |
|---|---|---|
| Market Share Chart | `plotly.line` | 3 lines: Actual (solid blue), Baseline forecast (dashed gray), Post-change projection (solid red/orange). Vertical line at change month. |
| Summary Metrics | `st.metric` x 3 | Current MS %, Projected MS % at 12m, Delta (pp) |
| Analog Label | `st.caption` | "Analog: Blended (Preferred -> Not Covered)" |

---

## Projection Logic (Python)

```python
def project_market_share(actual_share, baseline_forecast, analog_curve, 
                         change_month_idx, reverse, multiplier):
    """
    actual_share: dict of {month: share%} — historical data
    baseline_forecast: dict of {month: share%} — forecast without status change
    analog_curve: list of floats — MoM relative rate for months 1..N
    change_month_idx: int — index in the timeline where status changes
    reverse: int — 1 or -1
    multiplier: float — user-adjustable scaling
    """
    projected = {}
    
    for i, month in enumerate(all_months):
        if i < change_month_idx:
            # Rule 1: Use actual/baseline
            projected[month] = actual_share.get(month) or baseline_forecast[month]
        elif i == change_month_idx:
            # Rule 2: Change month = Month 1 of analog
            base = actual_share.get(month) or baseline_forecast[month]
            rate = analog_curve[0]
            projected[month] = base * (1 + rate * reverse * multiplier)
        else:
            # Rule 3: Subsequent months
            analog_month = i - change_month_idx
            if analog_month < len(analog_curve):
                rate = analog_curve[analog_month]
            else:
                rate = 0  # No more analog data, flat
            projected[month] = projected[prev_month] * (1 + rate * reverse * multiplier)
    
    return projected
```

---

## Step Table Lookup

```python
STEP_TABLE = {
    ("Not Covered", "Covered"):     {"analog": "Providence", "step": 1,  "reverse": -1},
    ("Not Covered", "Preferred"):   {"analog": "Blended",    "step": 2,  "reverse": -1},
    ("Preferred",   "Covered"):     {"analog": "BCBS",       "step": -1, "reverse": -1},
    ("Not Covered", "Specialty"):   {"analog": "Providence", "step": 1,  "reverse": -1},
    ("Preferred",   "Specialty"):   {"analog": "BCBS",       "step": -1, "reverse": -1},
    ("Specialty",   "Preferred"):   {"analog": "BCBS",       "step": 1,  "reverse": 1},
    ("Specialty",   "Not Covered"): {"analog": "Providence", "step": -1, "reverse": 1},
    ("Covered",     "Preferred"):   {"analog": "BCBS",       "step": 1,  "reverse": 1},
    ("Preferred",   "Not Covered"): {"analog": "Blended",    "step": -2, "reverse": 1},
    ("Covered",     "Not Covered"): {"analog": "Providence", "step": -1, "reverse": 1},
}
```

---

## Implementation Steps

### Phase 1: Data Preparation (Dataiku)
1. Create managed datasets in Dataiku that pull from Snowflake:
   - MCO current status (latest MMIT snapshot)
   - Nurtec market share by MCO by month
   - OCGRP claims by MCO by month
2. Create a dataset for analog curves (BCBS, Providence, Blended MoM rates) — can be a static upload or computed recipe

### Phase 2: App Development
1. Create Dataiku Streamlit webapp project
2. Build `app.py` with:
   - Dataset loading via `dataiku.Dataset().get_dataframe()`
   - Sidebar input widgets
   - Step table lookup logic
   - Projection engine (Rules 1/2/3)
   - Plotly chart rendering
   - Summary metric cards
3. Style with clean layout (wide mode, branded header)

### Phase 3: Testing & Validation
1. Compare app projections against Excel model for 3-5 known MCO scenarios
2. Validate edge cases: same-status selection (should show no change), all 10 transition types
3. Verify data refresh: ensure Dataiku dataset sync brings latest Snowflake data

### Phase 4: Deployment
1. Publish webapp in Dataiku project
2. Set dataset refresh schedule (e.g., weekly or monthly)
3. Share webapp URL with business leads

---

## File Structure (in Dataiku webapp)

```
webapp/
  app.py              # Main Streamlit application
  requirements.txt    # streamlit, plotly, pandas
```

---

## Validation Checklist

- [ ] MCO dropdown loads all MCOs correctly
- [ ] Current status auto-populates on MCO selection
- [ ] Step table lookup returns correct analog/reverse for all 10 transitions
- [ ] Chart shows actual data up to latest available month
- [ ] Projection starts correctly at Change Month
- [ ] Multiplier slider amplifies/dampens the curve as expected
- [ ] Results match Excel model within 0.1% tolerance
- [ ] Data refreshes when Dataiku recipe reruns
