# Plan: One line before change month, two lines from change month onward

## Current behavior (what's wrong)
Three traces on the chart:
1. **Actual National MS** — indices `0 : N_ACTUAL` (Jan'25 to Mar'26), solid navy
2. **Baseline (no change)** — indices `N_ACTUAL - 1 : N_TOTAL` (Mar'26 to Dec'27), **dashed gray** — starts at the last actual, so it visually appears as a second series between Mar'26 and the change month
3. **Projected (post change)** — indices `change_idx : N_TOTAL`, solid red

Result: between last actual (Mar'26) and the change month (Oct'26 in the screenshot), the chart draws the gray dashed baseline — visually a "different" series even though there's no scenario applied yet. User wants that region to read as a single continuous market-share line.

## Target behavior
- **Months 0 → change month (inclusive)** — one line, one data point per month.
  - Actuals portion (`0 : N_ACTUAL`) stays styled as today (solid navy, `lines+markers`).
  - The pre-change forecast portion (`N_ACTUAL - 1 : change_idx + 1`) renders as a **continuation of the same series** — same navy color, no marker, subtle dotted stroke to signal "this is forecast, not actual", but visually reads as one line.
  - No legend entry for the pre-change continuation (keeps legend to 3 items).
- **Months change month → end** — two lines:
  - Baseline (no change): `change_idx : N_TOTAL` — dashed gray (unchanged style)
  - Projected (post change): `change_idx : N_TOTAL` — solid red (unchanged style)
- Baseline **no longer starts at the last actual** — it starts at `change_idx`, so there is no gray dashed line between last actual and change month.

## Implementation (single file: `DSS_app.py`, `agent` branch, ~line 2571+)

### 1. Restructure the series slicing
Replace the per-view slicing block with:
```python
if chart_view == "National":
    _base_full   = baseline_natl_ms
    _proj_full   = projected_natl_ms
    _actual_lbl  = 'Actual National MS'
    _yaxis_title = 'National Market Share (%)'
else:
    _base_full   = baseline_ms
    _proj_full   = projected
    _actual_lbl  = 'Actual MCO MS'
    _yaxis_title = f'{selected_mco} Market Share (%)'

_series_actual    = _base_full[:N_ACTUAL]
# Pre-change forecast continuation: last actual through change month (inclusive)
_prechange_lo     = max(N_ACTUAL - 1, 0)
_prechange_hi     = max(change_idx + 1, _prechange_lo)   # empty if change_idx < N_ACTUAL - 1
_series_prechange = _base_full[_prechange_lo:_prechange_hi]
# Baseline post-change starts AT the change month, not at last actual
_series_baseline  = _base_full[change_idx:]
_series_proj      = _proj_full[change_idx:]
```

### 2. Trace 1 — Actuals (unchanged)
Keep the existing solid-navy `lines+markers` trace over `range(N_ACTUAL)`.

### 3. Trace 2 — NEW: Pre-change forecast continuation
Only render when there's at least one pre-change forecast month (`change_idx >= N_ACTUAL`):
```python
if len(_series_prechange) >= 2:
    fig.add_trace(go.Scatter(
        x=list(range(_prechange_lo, _prechange_hi)),
        y=_series_prechange,
        mode='lines',
        line=dict(color=PFZ_DARK_BLUE, width=2, dash='dot'),
        hovertemplate='%{text}<br>MS: %{y:.2f}%<extra></extra>',
        text=[MONTH_LABELS[i] for i in range(_prechange_lo, _prechange_hi)],
        showlegend=False,      # visually part of the actual line
        hoverinfo='skip' if False else None,
    ))
```
- Same navy color as actuals → reads as continuation.
- `dash='dot'` distinguishes forecast from actual on close inspection.
- `showlegend=False` keeps the legend at 3 entries.
- Endpoints `N_ACTUAL - 1` (last actual) and `change_idx` (the split) are shared with adjacent traces so lines meet exactly.

### 4. Trace 3 — Baseline (no change), scoped to post-change only
Change:
```python
x=list(range(N_ACTUAL - 1, N_TOTAL))
```
to:
```python
x=list(range(change_idx, N_TOTAL))
```
Data slice already updated in Step 1. Legend label unchanged: `Baseline (no change)`.

### 5. Trace 4 — Projected (unchanged)
Existing red `lines+markers` trace over `range(change_idx, N_TOTAL)`. No change.

### 6. Y-axis range calculation
Include the new pre-change slice in the min/max union:
```python
_all_v = list(_series_actual) + list(_series_prechange) + list(_series_baseline) + list(_series_proj)
```
(Currently uses `_series_actual + _series_baseline + _series_proj`.)

### 7. Edge cases
- `change_idx == N_ACTUAL - 1` (change at the last actual month): `_series_prechange` has 1 point (skipped by the `>= 2` guard), Baseline + Projected start immediately at that point — matches spec.
- `change_idx < N_ACTUAL` (theoretically past-dated scenario; UI probably prevents but guard anyway): pre-change trace skipped; Baseline overlaps Actual — acceptable since it's an unusual case.
- `change_idx > N_ACTUAL - 1` (normal): pre-change dotted line spans `[N_ACTUAL-1, change_idx]`.

## Out of scope
- No changes to `compute_national_ms`, `apply_analog`, `get_mco_ms`, `MS_COLS`, `ANALOG_CURVES`, or any calculation.
- No changes to the KPI cards, scenario sidebar, or Business Rules tab.
- No new legend entries (kept at 3: Actual / Baseline / Projected).
- Layout, y-axis padding, forecast vrect shading, and change-month vertical line: unchanged.

## Verification
- `python -m py_compile DSS_app.py`
- Manually verify National + MCO views: pre-change months show single navy line; post-change months show gray + red split.
