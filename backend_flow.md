# Rebate Decision Agent — Backend Data Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│               DATA SOURCE: Rebate_backend_implementation.xlsx             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Sheet 1: "Market Share"         Sheet 2: "Analogs"                     │
│  ┌─────────────────────────┐     ┌─────────────────────────┐           │
│  │ 2723 MCOs x 36 months   │     │ 23 months x 3 analogs   │           │
│  │                         │     │                         │           │
│  │ Cols: MCO_NM,           │     │ Cols: Month,            │           │
│  │   Current Status*,      │     │   BCBS (Cov->Pref),     │           │
│  │   Payer Type*,          │     │   Providence (Cov->NC),  │           │
│  │   OCGRP Contribution*,  │     │   Blended (Pref->NC)    │           │
│  │   Jan'25 .. Dec'27      │     │                         │           │
│  │                         │     │ Values = MoM relative    │           │
│  │ Row 8: Section markers  │     │ difference rates         │           │
│  │   Actual (Jan'25-Mar'26)│     └─────────────────────────┘           │
│  │   Projected (Apr'26+)   │                                           │
│  │                         │     Sheet 3: "Analog Implementation"       │
│  │ * Not yet populated     │     ┌─────────────────────────┐           │
│  │   (from Dataiku later)  │     │ 10 status transitions   │           │
│  └─────────────────────────┘     │                         │           │
│                                  │ Cols: Current, Future,   │           │
│  Sheet 4: "OCGRP claims"        │   Analog Used, Step,     │           │
│  ┌─────────────────────────┐     │   Reverse                │           │
│  │ 2730 MCOs x 36 months   │     └─────────────────────────┘           │
│  │                         │                                           │
│  │ Cols: MCO_NM,           │                                           │
│  │   Jan'25 .. Dec'27      │                                           │
│  │                         │                                           │
│  │ Values = OCGRP claim    │                                           │
│  │ volumes per MCO/month   │                                           │
│  │                         │                                           │
│  │ Purpose: Multiply new   │                                           │
│  │ MCO-level MS by OCGRP   │                                           │
│  │ claims to get Nurtec    │                                           │
│  │ claims, then roll up    │                                           │
│  │ nationally              │                                           │
│  └─────────────────────────┘                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         APP STARTUP (data loading)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Read "Market Share" sheet → pandas DataFrame                        │
│     - Header row: 7 (0-indexed: 6)                                      │
│     - Data starts: row 9 (skip section marker row 8)                    │
│     - Result: df_market_share[MCO_NM, Status*, Payer*, Contrib*,        │
│               Jan 2025 ... Dec 2027]                                    │
│                                                                         │
│  2. Read "Analogs" sheet → dict of 3 curves                            │
│     - Data rows: 18-40 (Month 1 to Month 23)                           │
│     - Result: {"BCBS": [...], "Providence": [...], "Blended": [...]}    │
│                                                                         │
│  3. Read "Analog Implementation" sheet → dict lookup                    │
│     - Data rows: 5-14                                                   │
│     - Result: {(Current, Future): {analog, step, reverse}}              │
│                                                                         │
│  4. Read "OCGRP claims" sheet → pandas DataFrame                       │
│     - Header row: 6 (0-indexed: 5)                                      │
│     - Data starts: row 8 (skip section marker row 7)                    │
│     - Result: df_ocgrp[MCO_NM, Jan 2025 ... Dec 2027]                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION FLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──── SIDEBAR ────────────────────────────────────────────────┐        │
│  │                                                              │        │
│  │  1. SEARCH MCO (text input for type-ahead filtering)         │        │
│  │     └─► Filters 2723 MCOs by typing                          │        │
│  │                                                              │        │
│  │  2. SELECT MCO (dropdown, filtered list)                     │        │
│  │     └─► Picks the MCO to analyze                             │        │
│  │                                                              │        │
│  │  3. CURRENT STATUS (auto-filled, read-only)                  │        │
│  │     └─► From Market Share col B                              │        │
│  │         (shows "Data not available yet" if empty)            │        │
│  │                                                              │        │
│  │  4. FUTURE STATUS (user selects)                             │        │
│  │     └─► Options: Not Covered/Covered/Preferred/Specialty     │        │
│  │         (excludes current status)                            │        │
│  │                                                              │        │
│  │  5. CHANGE MONTH (user selects)                              │        │
│  │     └─► Apr 2026 through Dec 2027 (projected months)        │        │
│  │                                                              │        │
│  │  6. RUN SCENARIO (button)                                    │        │
│  │                                                              │        │
│  └──────────────────────────────────────────────────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         PROJECTION ENGINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  === MCO-LEVEL PROJECTION ===                                           │
│                                                                         │
│  INPUT:                                                                 │
│    - MCO baseline MS: 36 values from Market Share row                   │
│    - Analog curve: 23 MoM rates from Analogs sheet                      │
│    - Reverse: from Step Table lookup                                    │
│    - Change Month Index: position in 0..35 timeline                     │
│                                                                         │
│  FORMULA (from Excel documentation):                                    │
│    For each month M >= Change Month:                                    │
│                                                                         │
│      Projected[M] = Baseline[M] x (1 + analog_rate[M-change] x Reverse)│
│                                                                         │
│  WHERE:                                                                 │
│    - Baseline[M] = original projected MS from Market Share table        │
│    - analog_rate[M-change] = relative difference for that analog month  │
│    - Reverse = +1 or -1 (from Step Table)                               │
│    - If M-change > 23, use the last available analog rate               │
│                                                                         │
│  === NATIONAL ROLL-UP ===                                               │
│                                                                         │
│  For each month M:                                                      │
│    1. New Nurtec Claims[M] = Projected MS[M] x OCGRP Claims[M]         │
│    2. Baseline Nurtec Claims[M] = Baseline MS[M] x OCGRP Claims[M]     │
│                                                                         │
│  National Impact:                                                       │
│    - Sum all MCO Nurtec Claims (new) → National Nurtec Claims           │
│    - Sum all MCO OCGRP Claims → National OCGRP Claims                   │
│    - National MS = National Nurtec Claims / National OCGRP Claims       │
│                                                                         │
│  NOTE: For a single MCO scenario, only that MCO's MS changes;           │
│        all other MCOs retain baseline MS for the national roll-up.       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CHART (Plotly interactive):                                            │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                                                             │        │
│  │  ── Actual MS (dark blue, Jan'25 - Mar'26, 15 months)       │        │
│  │  -- Baseline Forecast (gray dashed, Apr'26 - Dec'27)        │        │
│  │  ── Projected post-change (red, from change month onward)   │        │
│  │  |  Vertical marker at change month (orange dashed)         │        │
│  │                                                             │        │
│  │  Y-axis: Market Share (%) — values * 100                    │        │
│  │  X-axis: Month labels (every 6th shown)                     │        │
│  │                                                             │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                         │
│  IMPACT SUMMARY (MCO-level, 4 metric cards):                            │
│  ┌────────────┐ ┌────────────────┐ ┌────────────┐ ┌────────────┐      │
│  │ Current MS │ │ Projected (12m)│ │   Delta    │ │   Analog   │      │
│  │   44.2%    │ │    41.5%       │ │  -2.7 pp   │ │  Blended   │      │
│  └────────────┘ └────────────────┘ └────────────┘ └────────────┘      │
│                                                                         │
│  NATIONAL IMPACT (roll-up section):                                     │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐             │
│  │ Baseline Natl  │ │ Projected Natl │ │ National Delta │             │
│  │ MS: 43.8%      │ │ MS: 43.5%      │ │  -0.3 pp       │             │
│  └────────────────┘ └────────────────┘ └────────────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Schema Details

### Market Share Table (Sheet: "Market Share")
| Column | Description | Available? |
|--------|-------------|-----------|
| A (col 0) | MCO_NM — Plan name | Yes (2723 MCOs) |
| B (col 1) | Current Status from MMIT | Not yet (Dataiku) |
| C (col 2) | Payer Type | Not yet (Dataiku) |
| D (col 3) | OCGRP FY2025 Contribution | Not yet (Dataiku) |
| E-S (cols 4-18) | Jan 2025 - Mar 2026 (ACTUAL) | Yes |
| T-AN (cols 19-39) | Apr 2026 - Dec 2027 (PROJECTED) | Yes |

### OCGRP Claims Table (Sheet: "OCGRP claims")
| Column | Description | Available? |
|--------|-------------|-----------|
| A (col 0) | MCO_NM — Plan name | Yes (2730 MCOs) |
| B-P (cols 1-15) | Jan 2025 - Mar 2026 (ACTUAL claims) | Yes |
| Q-AK (cols 16-36) | Apr 2026 - Dec 2027 (PROJECTED claims) | Yes |

### Analogs Table (Sheet: "Analogs")
| Column | Description |
|--------|-------------|
| A (col 0) | Month label (Month 1 - Month 23) |
| B (col 1) | BCBS rate (Covered -> Preferred analog) |
| C (col 2) | Providence rate (Covered -> Not Covered analog) |
| D (col 3) | Blended rate (Preferred -> Not Covered analog) |

### Step Table (Sheet: "Analog Implementation")
| Current | Future | Analog | Step | Reverse |
|---------|--------|--------|------|---------|
| Not Covered | Covered | Providence | 1 | -1 |
| Not Covered | Preferred | Blended | 2 | -1 |
| Preferred | Covered | BCBS | -1 | -1 |
| Not Covered | Specialty | Providence | 1 | -1 |
| Preferred | Specialty | BCBS | -1 | -1 |
| Specialty | Preferred | BCBS | 1 | 1 |
| Specialty | Not Covered | Providence | -1 | 1 |
| Covered | Preferred | BCBS | 1 | 1 |
| Preferred | Not Covered | Blended | -2 | 1 |
| Covered | Not Covered | Providence | -1 | 1 |

## National Roll-Up Logic

The national roll-up answers: "If this MCO's formulary status changes, what is the impact on overall national Nurtec market share?"

```
For each month M:
  For each MCO:
    If MCO == selected MCO:
      nurtec_claims[M] = projected_ms[M] * ocgrp_claims[M]
    Else:
      nurtec_claims[M] = baseline_ms[M] * ocgrp_claims[M]
  
  national_nurtec[M] = SUM(nurtec_claims across all MCOs)
  national_ocgrp[M] = SUM(ocgrp_claims across all MCOs)
  national_ms[M] = national_nurtec[M] / national_ocgrp[M]
```

This shows how one MCO's status change ripples into the national aggregate.
