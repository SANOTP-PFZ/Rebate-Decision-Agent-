# Plan: Rebate Decision Agent — UI/UX polish to shippable quality

## Context

The agent page lives in [DSS_app.py](DSS_app.py) at lines 781-1183. Current shape:

- Plain title + subtitle
- 320 px sidebar with header, four form fields, an HTML `.scenario-box` block, and a "Back to Home" button pinned at the bottom
- Main area: National chart (line 1004) -> 4 metrics -> divider -> MCO chart (line 1094) -> 4 metrics -> footer

Design tokens already in the CSS block (lines 37-515) that we reuse:

- Navy palette `--navy-900 #0A1A3D`, `--navy-700 #163990`, `--navy-600 #1C4FC0`, accent `#41B6E6`
- Surfaces `--bg #EEF3FB`, `--surface #FFFFFF`
- Radii and shadows via `--panel-radius 18px`, `--shadow-sm/md/lg`
- Fonts Manrope (headings), Inter (body)

Backend and data flow to preserve verbatim (must not change):

- `load_data()` (line 802) and the four `dataiku.Dataset(...)` reads
- `get_mco_ms`, `get_mco_ocgrp`, `get_mco_metadata`
- `apply_analog`, `compute_national_ms`
- `MS_COLS`, `OCGRP_COLS`, `MONTH_LABELS`, `CHANGE_MONTH_OPTIONS`, `CHANGE_MONTH_IDX_MAP`, `STATUS_OPTIONS`, `N_ACTUAL`, `N_TOTAL`, `STEP_TABLE`, `ANALOG_CURVES`
- All computed values (`baseline_ms`, `projected`, `analog_name`, `reverse`, `baseline_natl_ms`, `projected_natl_ms`, `natl_baseline_current`, `natl_projected_12m`, `natl_delta`, `mco_baseline_current`, `mco_projected_12m`, `mco_delta`) must retain identical formulas.

Locked user choices:

1. Chart layout = single canvas with a `National | MCO` segmented toggle
2. KPI cards = value + delta only (no sparklines)
3. Fully reactive (no Run button)
4. Ship all 8 tasks in one pass
5. Do NOT change any backend calculation or logic

## Target agent-page layout

```
+------------------------------------------------------------------+
|  Mark  Rebate Decision Agent           Back to Home | PS avatar  |  <- top bar
+------------------------------------------------------------------+
|  MCO: CVS HEALTH-ADV  .  Preferred -> Not Covered  .  Jul 2026   |  <- context chip row
+---------+--------------------------------------------------------+
|         |  +----------+ +----------+ +----------+ +----------+   |
| SIDEBAR |  | Baseline | | Proj 12m | | Delta pp | | Analog   |   |  <- KPI hero
|         |  |  44.12%  | |  38.90%  | | v 5.22pp | | Blended  |   |     (value + delta)
|         |  +----------+ +----------+ +----------+ +----------+   |
| Inputs  |                                                        |
|  MCO    |   [ National ]  [ MCO ]     <- segmented toggle        |
|  Future |  +-----------------------------------------------+    |
|  Month  |  |  Actual  ---Baseline  Projected               |    |
|         |  |                                               |    |
| Current |  |     solid navy   | shaded forecast band       |    |
|  Status |  |                  V                            |    |  <- single chart
|  Payer  |  |            (Status change badge)              |    |
|  OCGRP  |  +-----------------------------------------------+    |
|         |         Jan'25 . . . Mar'26 | Apr'26 . . . Dec'27    |
| Details |                                                        |
| Analog  |            Data as of . source . analog . confidential |
| Step    |                                                        |
+---------+--------------------------------------------------------+
```

## Implementation steps

### Step 1 - Design-token cheatsheet

Add a comment block inside the existing `<style>` (before `.block-container`) documenting spacing scale (8/12/16/24/32/48), radii (10/14/18), shadow tokens, and type scale (10/11/12/13/14/18/26/34). No new tokens introduced. Every new class added below snaps to these values.

### Step 2 - Rebuild page shell

Above the existing agent-page content, render:

**Top bar (56 px):** flexbox row inside a new `<div class="agent-topbar">`, with:
- Left: small square mark (12 px navy tile) + `Rebate Decision Agent` in Manrope 700 16 px
- Right: `<- Back to Home` styled as text link (calls `go_to_landing`) and a static `PS` avatar circle (initials of the signed-in user)

**Context chip row (44 px):** `<div class="agent-context">` under the top bar, rendering three chips (MCO, `Current -> Future`, Change Month) that update reactively from `selected_mco`, `current_status`, `future_status`, `selected_change_month`. Chips are 10 px uppercase Inter, `--surface-2` background with a 1 px hairline.

Move the existing `st.button("Back to Home", ...)` from the sidebar (line 978) into the top bar. Remove the sidebar entry to avoid duplication.

### Step 3 - Redesign sidebar into grouped panels

Replace the current sidebar block (lines 931-978) with three grouped sections, each preceded by an 11 px uppercase letter-spaced label header, separated by 1 px hairline dividers:

**Section A - Scenario Inputs**
- Keep the existing `st.selectbox` for MCO (line 934) verbatim
- Keep `st.selectbox` for Future Status (line 949) verbatim
- Keep `st.selectbox` for Change Month (line 950) verbatim

**Section B - Current State**
- Replace the disabled `st.text_input("Current Status", ...)` at line 942 with a small `st.markdown` info panel that renders Current Status, Payer Type, and OCGRP Contribution as label/value rows. Values in Manrope 600, `tabular-nums`. Status also renders as a small colored tag (Not Covered = gray, Covered = blue, Preferred = navy solid, Specialty = teal). Values still come from `get_mco_metadata(selected_mco)` unchanged.

**Section C - Scenario Details**
- Replaces the current `.scenario-box` HTML block (lines 956-975). Renders Analog / Step / Reverse as label/mono-value rows (drop the `<b>` markup). Invalid-transition variant uses a red-tinted card with a warning glyph. Values still come from `STEP_TABLE[step_key]` unchanged.

The sidebar loses the Back-to-Home button; it now lives in the top bar (Step 2).

### Step 4 - KPI hero row (value + delta only)

Replace both metric strips (lines 1067-1086 and 1154-1173) with a single row of four `.agent-kpi` cards, rendered once between the context chip row and the chart:

- Card 1 - `BASELINE NATIONAL MS` value `{natl_baseline_current:.2f}%`, delta line "as of Mar 2026"
- Card 2 - `PROJECTED . 12M POST CHANGE` value `{natl_projected_12m:.2f}%`, delta line colored triangle + `{natl_delta:+.2f} pp` (red down / green up)
- Card 3 - `MCO-LEVEL DELTA` value `{mco_delta:+.2f} pp` styled by sign, delta line "`Current {mco_baseline_current:.2f}% -> Proj {mco_projected_12m:.2f}%`"
- Card 4 - `ANALOG APPLIED` value `{analog_name}`, delta line "`{current_status} -> {future_status} . Step {step}`"

All values are the exact variables that already exist in the agent page - no recomputation, no new math. Cards drop to 2x2 below ~1100 px width. Layout uses `st.columns(4)` with a wrapping CSS class.

### Step 5 - Single chart with segmented toggle

Replace the two chart blocks (National at lines 998-1056 and MCO at lines 1091-1143) with:

1. A pill-styled segmented control above the chart, backed by `st.radio("View", ["National", "MCO"], horizontal=True, label_visibility="collapsed")` with CSS to render the radios as chip buttons.
2. A single `go.Figure()` block that switches its three traces between the National and MCO series based on the toggle value. Trace data (`baseline_natl_ms`, `projected_natl_ms`, `baseline_ms`, `projected`) is the same variables computed today.

Polish applied to whichever view is active:
- Legend converted to a chip row in the top-right of the plot area (Plotly `legend=dict(orientation='h', xanchor='right', x=1, y=1.06, ...)`)
- Shaded forecast band via `fig.add_vrect(x0=N_ACTUAL - 1, x1=N_TOTAL - 1, fillcolor='rgba(15,23,42,0.03)', line_width=0, layer='below')`
- Status-change marker becomes a small orange rounded badge at `y=1.05` yref=paper carrying `Status change . {selected_change_month}` (replaces the floating annotation on lines 1031-1033 and 1121-1123)
- Softer grid `rgba(15,23,42,0.04)`, horizontal-only
- `hovermode='x unified'` with `spikemode='across'`
- Line widths: Actual `2.75`, Baseline `2`, Projected `2.75` (harmonized)
- Y-axis padding replaces the ad-hoc `+/- 0.5` and `+/- 2` with `max((y_hi - y_lo) * 0.08, 0.5)` so both views scale cleanly. Y-axis range still driven by whichever view is active - no formula change to the underlying series.

### Step 6 - Loading, empty, and error states

- **Skeleton loader:** Wrap the KPI row and chart in a shimmering placeholder while `compute_national_ms` runs. Pure CSS keyframe animation. The `st.spinner("Computing national roll-up...")` block at line 999 is replaced by rendering the skeleton before the compute call and the real content after. Compute call itself unchanged.
- **Cache the roll-up:** Extract the existing inline `compute_national_ms(...)` call at line 1000 into an `@st.cache_data(ttl=600)` wrapper keyed on `(selected_mco, change_idx, analog_name, reverse)`. The wrapped function calls the untouched `compute_national_ms` unchanged - this is pure memoization, not a math change.
- **Empty state:** Replace the `st.info("Select a valid status transition to see national impact.")` at line 1175 with a proper full-width card carrying a warning glyph, a headline, a suggestion sentence listing the valid Future Status options for the current status, and a small `View business rules ->` link that calls the existing `go_to_rules()`. Fallback trigger (`step_key not in STEP_TABLE`) is unchanged.

### Step 7 - Micro-interactions and polish pass

- Hover on `.agent-kpi` cards: `translateY(-2px)` and `--shadow-md`, 180 ms `ease-out`
- All numeric strings use `font-variant-numeric: tabular-nums` (kills column jitter as values change)
- Focus-visible outlines: 2 px `--accent` for keyboard users
- Chart container gets `animation: fadeIn 220ms ease-out` keyed by a `st.session_state` scenario-hash so re-renders feel intentional
- Sidebar section headers standardized to 11 px uppercase letter-spaced Manrope 600
- Vertical rhythm normalized to 24 px between sections in the main area
- Footer (line 1178) reformatted right-aligned, dot-separated: `Data as of Mar 2026 . Source: Xponent (Plantrak) via Dataiku . Analog: {analog_name} . Pfizer Confidential`

### Step 8 - Responsive cross-check and doc sync

- Verify at 1280 / 1440 / 1920 widths - KPI row 4-up at >=1280, 2x2 below; chart legend chips wrap; sidebar stays 320 px
- Namespace all new CSS classes under `.agent-*` (`.agent-topbar`, `.agent-context`, `.agent-kpi`, `.agent-toggle`, `.agent-chart-wrap`) so landing and Business Rules pages are untouched
- Update [wireframe.md](wireframe.md) with the new layout diagram

## Verification

Because this is a Dataiku-hosted Streamlit app (imports `dataiku` at line 6), I cannot run it locally. Verification is a mix of static and manual checks:

1. **Static grep guardrails** - after edits, `grep` the file to confirm every backend anchor still exists character-for-character:
   - `df_ms = dataiku.Dataset("SQL_NURTEC_XPO_NPA_SCALED_MS_by_MONTH_SF").get_dataframe()`
   - `df_oc = dataiku.Dataset("SQL_XPO_NPA_SCALED_OCGRP_TRX_MONTH_SF").get_dataframe()`
   - `dataiku.Dataset("PAYER_MODEL_ANALOG_MCO_SF").get_dataframe()`
   - `dataiku.Dataset("PAYER_MODEL_STEP_SF").get_dataframe()`
   - Signatures of `apply_analog`, `compute_national_ms`, `get_mco_ms`, `get_mco_ocgrp`, `get_mco_metadata`
   - Constants `MS_COLS`, `OCGRP_COLS`, `MONTH_LABELS`, `CHANGE_MONTH_OPTIONS`, `CHANGE_MONTH_IDX_MAP`, `N_ACTUAL`, `N_TOTAL`
2. **Diff review** - reviewer confirms the diff touches only markup, CSS, and rendering code; no arithmetic or dataset access lines changed
3. **Python compile check** - `python -m py_compile DSS_app.py` (readonly, safe) to catch syntax errors from the CSS block edits
4. **Manual smoke test in Dataiku** - user runs the webapp and validates the six known scenarios from [README.md](README.md) Phase 3 checklist:
   - MCO dropdown loads
   - Current Status auto-populates
   - All 10 STEP_TABLE transitions produce identical numbers to today
   - Chart shows actual up to Mar 2026, forecast Apr 2026 onward
   - Multiplier and change month behave identically
5. **Regression parity check** - for a fixed scenario (e.g. `CVS HEALTH-ADV, Preferred -> Not Covered, Jul 2026`), verify pre-change and post-change KPI values match the values shown by the current implementation on the same inputs, digit-for-digit.

## Critical files

- [DSS_app.py](DSS_app.py) - all changes land here; CSS block (lines 37-515) gets new `.agent-*` classes, agent page block (lines 781-1183) is restructured while every calculation and dataset call is preserved verbatim
- [wireframe.md](wireframe.md) - updated ASCII layout so docs match the new shell
- [README.md](README.md) - source of truth for the projection logic; consulted to confirm nothing there needs updating (spec unchanged)
- [backend_flow.md](backend_flow.md) - referenced to confirm the backend contract this UI reads against; not modified

## Out of scope

- No changes to projection math, roll-up logic, or dataset schemas
- No changes to the landing page or Business Rules page
- No new features (export, share, PDF, multi-scenario compare) - can be follow-ups
- No changes to `.gitignore`, requirements, or deployment config

## Risks and mitigations

- **Streamlit CSS override brittleness under Dataiku:** scope every new selector to `.agent-*` and avoid overriding internal Streamlit selectors beyond what already exists
- **Segmented control via `st.radio`:** the horizontal radio styled as chips is a known-good Streamlit pattern; if visual polish falls short, fall back to two `st.button`s styled identically, still with no backend impact
- **Cache invalidation:** the roll-up cache key includes `analog_name` and `reverse` (derived from `step_key`), so any transition change re-computes correctly
- **Sidebar becoming cramped:** if the three new sections push content below the fold on 900 px tall screens, wrap "Scenario Details" in an `st.expander(..., expanded=True)`
