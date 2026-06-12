# Nurtec Payer Model — Streamlit Webapp Wireframe

## App Layout

```
+=====================================================================+
|  NURTEC PAYER MODEL -- Market Share Scenario Tool                    |
+=====================================================================+
|                                                                     |
|  +-- SIDEBAR ---------------------------+                           |
|  |                                       |                          |
|  |  Select MCO                           |                          |
|  |  +-------------------------------+    |                          |
|  |  | [Dropdown: CVS HEALTH-AD.. v] |    |                          |
|  |  +-------------------------------+    |                          |
|  |                                       |                          |
|  |  Current Status (auto-populated)      |                          |
|  |  +-------------------------------+    |                          |
|  |  | Preferred          (read-only)|    |                          |
|  |  +-------------------------------+    |                          |
|  |                                       |                          |
|  |  Future Status                        |                          |
|  |  +-------------------------------+    |                          |
|  |  | [Dropdown: Not Covered     v] |    |                          |
|  |  +-------------------------------+    |                          |
|  |                                       |                          |
|  |  Change Month                         |                          |
|  |  +-------------------------------+    |                          |
|  |  | [Month picker: Jul 2026    v] |    |                          |
|  |  +-------------------------------+    |                          |
|  |                                       |                          |
|  |  Multiplier (default = 1.0)           |                          |
|  |  +-------------------------------+    |                          |
|  |  | [Slider: 0.5 --- 1.0 --- 2.0]|    |                          |
|  |  +-------------------------------+    |                          |
|  |                                       |                          |
|  |  +-------------------------------+    |                          |
|  |  |      [ Run Scenario ]         |    |                          |
|  |  +-------------------------------+    |                          |
|  |                                       |                          |
|  |  --- Scenario Details (auto) ---      |                          |
|  |  Analog Used  : Blended               |                          |
|  |  Step         : -2                    |                          |
|  |  Reverse      : 1                     |                          |
|  |  OCGRP Contrib: 3.6%                  |                          |
|  |                                       |                          |
|  +---------------------------------------+                          |
|                                                                     |
|  +-- MAIN AREA ----------------------------------------------------+|
|  |                                                                  ||
|  |  +-- Market Share Trend Chart ------------------------------+    ||
|  |  |                                                          |    ||
|  |  |   50% |                                                  |    ||
|  |  |       |    *--*--*--*--*--*--*--*                         |    ||
|  |  |   45% |   /                      \                       |    ||
|  |  |       |  *                        \                      |    ||
|  |  |   40% |                            \--*--*--*--*         |    ||
|  |  |       |                                                  |    ||
|  |  |   35% |                                      *--*--*     |    ||
|  |  |       |                                                  |    ||
|  |  |   30% +-------------------------------------------->     |    ||
|  |  |       Jan'25  Apr   Jul   Oct  Jan'26  Apr  Jul  Oct    |    ||
|  |  |                                                          |    ||
|  |  |   --- Actual MS                                          |    ||
|  |  |   - - Baseline Forecast (no change)                      |    ||
|  |  |   === Projected (post status change)                     |    ||
|  |  |                 ^ Change Month                           |    ||
|  |  +----------------------------------------------------------+    ||
|  |                                                                  ||
|  |  +-- Summary Metrics ------------------------------------------+||
|  |  |                                                              |||
|  |  |  Current MS     | Projected MS (12m) | Delta Impact          |||
|  |  |  43.2%          | 36.8%              | -6.4 pp               |||
|  |  |                                                              |||
|  |  |  Analog: Blended (Preferred -> Not Covered)                  |||
|  |  +--------------------------------------------------------------+||
|  |                                                                  ||
|  +------------------------------------------------------------------+|
|                                                                     |
+=====================================================================+
```

## Interaction Flow

1. **Select MCO** - Dropdown with all MCO names (searchable). On selection, the app auto-populates "Current Status" from the latest MMIT data.

2. **Choose Future Status** - Dropdown filtered to valid transitions: Not Covered, Covered, Preferred, Specialty (excludes current status).

3. **Set Change Month** - Month picker starting from next month through Dec 2027.

4. **Adjust Multiplier** (optional) - Slider from 0.5x to 2.0x (default 1.0). Allows business leads to dampen or amplify the analog effect.

5. **Run Scenario** - Triggers the projection calculation. The sidebar auto-displays which analog will be used and the Step/Reverse parameters.

6. **View Output** - Main area shows:
   - A line chart with 3 series (actual, baseline, post-change projection)
   - A vertical marker at the Change Month
   - Summary KPI cards showing current vs projected market share and percentage-point delta

## Status Hierarchy (used by Step table)

```
Not Covered  <-->  Covered  <-->  Preferred
                      |
                  Specialty (treated same tier as Covered)
```

## Step Table (embedded in app logic)

| Current      | Future       | Analog     | Step | Reverse | Multiplier |
|-------------|-------------|------------|------|---------|------------|
| Not Covered | Covered     | Providence | 1    | -1      | 1          |
| Not Covered | Preferred   | Blended    | 2    | -1      | 1          |
| Preferred   | Covered     | BCBS       | -1   | -1      | 1          |
| Not Covered | Specialty   | Providence | 1    | -1      | 1          |
| Preferred   | Specialty   | BCBS       | -1   | -1      | 1          |
| Specialty   | Preferred   | BCBS       | 1    | 1       | 1          |
| Specialty   | Not Covered | Providence | -1   | 1       | 1          |
| Covered     | Preferred   | BCBS       | 1    | 1       | 1          |
| Preferred   | Not Covered | Blended    | -2   | 1       | 1          |
| Covered     | Not Covered | Providence | -1   | 1       | 1          |

## Projection Rules (from Xpo TRx Model sheet)

- **Rule 1**: Pre-change months use actual historical market share
- **Rule 2**: The Change Month is "Month 1" of the analog — apply the analog's first-month rate-of-change
- **Rule 3**: Each subsequent month: `Projected[M] = Projected[M-1] x (1 + analog_relative_rate x Reverse x Multiplier)`
