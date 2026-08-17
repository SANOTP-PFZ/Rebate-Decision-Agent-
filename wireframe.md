# Nurtec Payer Model — Streamlit Webapp Wireframe

## Rebate Decision Agent — Refreshed Layout (v2)

```
+=====================================================================+
|  [Pfizer]  REBATE DECISION AGENT                                     |   <- global brand header
+=====================================================================+
|                                                     [ Back to Home ] |   <- action row (top-right)
+---------------------------------------------------------------------+
|  Scenario   MCO · CVS HEALTH  ·  [Preferred] -> [Not Covered]  ·     |
|             Change · Jul 2026                                        |   <- context chip row
+-------------+-------------------------------------------------------+
| SIDEBAR     |                                                       |
|             |  NATIONAL & MCO IMPACT                                |
| SCENARIO    |  +----------+ +----------+ +----------+ +----------+ |
| INPUTS      |  | Baseline | | Proj 12m | | MCO ΔPP  | | Analog   | |
|  MCO        |  |  44.12%  | |  38.90%  | | ▼ 5.2 pp | | Blended  | |   <- KPI hero (single row)
|  Future     |  | as of..  | | ▼ -5.22p | | 62→57%   | | Step -2  | |
|  Change     |  +----------+ +----------+ +----------+ +----------+ |
|  Month      |                                                       |
|             |  MARKET SHARE TREND        [ National ]  [ MCO ]      |   <- segmented toggle
| CURRENT     |  +-------------------------------------------------+  |
| STATE       |  |  Actual --Baseline --Projected                  |  |
|  Status tag |  |                    :                            |  |
|  Payer      |  |    solid navy line : shaded forecast region     |  |
|  OCGRP %    |  |                    ▼ Status change · Jul'26     |  |   <- single chart
|             |  |   ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈dashed gray + red overlay┈ |  |
| SCENARIO    |  +-------------------------------------------------+  |
| DETAILS     |         Jan'25 ... Mar'26 | Apr'26 ...... Dec'27      |
|  Analog     |                                                       |
|  Step       |     Data as of Mar 2026 · Source: Xponent · Analog:.. |
|  Reverse    |                                            (footer)   |
|  Transition |                                                       |
+-------------+-------------------------------------------------------+
```

## App Layout (v1 — historical reference)

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
- **Rule 3**: Each subsequent month uses its corresponding analog month rate: `Projected[M] = Baseline[M] x (1 + analog_rate[months_since_change] x Reverse)`

---

## UI/UX Enhancement Guide

### Visual Polish

#### Color System
- **Primary palette**: Dark Navy (#002F6C) for headers/emphasis, Pfizer Blue (#0093D0) for interactive elements/accents, White (#FFFFFF) for content backgrounds
- **Semantic colors**: Red (#E03C31) for negative deltas/declines, Green (#28A745) for positive gains, Orange (#F5A623) for warnings/change markers
- **Neutral tones**: Light gray (#F7FAFC) for app background, Medium gray (#63666A) for secondary text, Border gray (#D0DEE8) for card edges
- **Gradient accents**: Use subtle linear gradients on headers (`background: linear-gradient(135deg, #002F6C, #004B8D)`) for depth

#### Typography
- **Hierarchy**: Use 3 distinct size levels — section headers (14-16px, 700 weight), metric values (22-28px, 800 weight), body/labels (10-12px, 400-600 weight)
- **Letter-spacing**: Add 0.5-1px letter-spacing on uppercase labels for readability
- **Font stacking**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` for cross-platform consistency

#### Spacing & Layout
- **Card padding**: 16-20px internal padding, 12-16px gap between cards
- **Section spacing**: 24-32px between major sections, use dividers (`border-top: 2px solid #D0DEE8`) sparingly
- **Border radius**: 8px for cards, 6px for buttons, 4px for small elements (badges, tags)
- **Shadows**: `box-shadow: 0 2px 8px rgba(0,47,108,0.06)` for cards, `0 4px 12px rgba(0,47,108,0.1)` on hover

#### KPI Cards
- **Layout**: Equal-width columns with consistent internal structure (label on top, value centered, optional sub-label)
- **Emphasis**: Use colored left border (4px) on cards to indicate sentiment (blue=neutral, red=negative, green=positive)
- **Value formatting**: Large bold numbers with unit suffix, 2 decimal places for percentages, explicit +/- sign on deltas

### Chart Improvements

#### Plotly Styling
- **Line weights**: Actual data = 2.5px solid, Baseline = 2px dashed, Projected = 2.5px solid with markers
- **Marker size**: 5-6px on projected line for emphasis, 4px on actual
- **Fill area**: Add semi-transparent fill between baseline and projected lines to highlight the delta visually:
  ```python
  fig.add_trace(go.Scatter(
      ..., fill='tonexty', fillcolor='rgba(224, 60, 49, 0.08)'
  ))
  ```
- **Hover template**: Show month name, value with % suffix, and delta from baseline in hover tooltip:
  ```python
  hovertemplate='%{x}<br>MS: %{y:.2f}%<extra></extra>'
  ```
- **Annotations**: Add text annotations at key points (change month value, 12m projected value) directly on the chart
- **Grid**: Light horizontal gridlines only (`gridcolor='#F0F2F5'`), no vertical grid
- **Y-axis range**: Pad by 1-2pp above/below data range for breathing room, use `ticksuffix='%'`

#### Chart Containers
- **Title**: Place a styled header above each chart indicating scope ("National Market Share Trend", "MCO-Level Market Share Trend")
- **Legend**: Horizontal legend above the chart, compact font (10px), subtle gray color
- **Responsive height**: 380-420px for desktop, consider reducing on smaller viewports

### Micro-interactions

#### Loading States
- Use `st.spinner("Computing national roll-up...")` around heavy computations
- Add a brief loading message while datasets load on first visit

#### Visual Feedback
- **Sidebar scenario box**: Animate border color change when inputs change (CSS transition on border-color)
- **KPI delta arrows**: Add unicode arrows (up arrow for positive, down arrow for negative) next to delta values
- **Change month marker**: Pulse animation on the vertical line annotation:
  ```css
  @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
  }
  ```

#### Transitions
- **Page navigation**: Use `st.session_state` transitions with brief content fade (CSS `animation: fadeIn 0.3s ease`)
- **Expander sections**: Use `st.expander` for detailed data tables that don't need to be visible by default

### Dashboard Layout

#### Information Hierarchy (top to bottom)
1. **Header bar** — Brand identity, app title (fixed, always visible)
2. **Primary chart** — National MS trend (largest visual element, commands attention)
3. **Primary KPIs** — National impact metrics (scannable at a glance)
4. **Secondary chart** — MCO-level trend (supplementary detail)
5. **Secondary KPIs** — MCO-level metrics
6. **Footer** — Data source attribution, confidentiality notice

#### Density & Scanning
- **KPI cards**: 4 cards in a row maximum, use `st.columns(4)` with equal weights
- **Progressive disclosure**: Show summary first, let users drill into detail (e.g., expandable analog table below charts)
- **Visual anchors**: Use the impact header bars (`background: #002F6C`) as section separators — they create natural scan points
- **White space**: Generous margins between sections prevent cognitive overload; don't pack elements too tightly

#### Sidebar Design
- **Sticky inputs**: All scenario inputs in sidebar so they're always accessible while scrolling the main area
- **Scenario summary box**: Compact info card at bottom of sidebar showing active parameters at a glance
- **Input grouping**: Group related inputs (MCO + Status together, Change Month separate) with subtle spacing
- **Back navigation**: Always accessible, positioned at bottom of sidebar with full width
