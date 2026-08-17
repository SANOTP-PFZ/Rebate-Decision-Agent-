# Plan: Redesign Business Rules Tables

## Goal
Make the two tables on the Business Rules tab look like polished, product-grade UI (not a raw DataFrame dump). CSS/HTML rendering only — zero backend/calculation changes.

## Problems with the current tables (`st.table(step_df)`, `st.table(analog_df)`)
- Dark navy header + **dark navy index column** (the "0/1/2…" gutter) is visually heavy and duplicates row count
- No zebra striping, no hover state, no cell hierarchy
- Numeric columns (Step, Reverse, BCBS, Providence, Blended) are left-aligned strings, no sign coloring, no tabular alignment
- Status values (Not Covered, Preferred, Specialty, Covered) and Analog values (BCBS, Providence, Blended) render as flat text — no visual grouping
- No rounded container, no shadow, no hairline — table feels bolted-in, not part of the card system used elsewhere on the page

## Approach
Hand-roll two small HTML tables via Python f-strings and render with `st.markdown(..., unsafe_allow_html=True)`. Streamlit's `st.table` doesn't allow the per-cell control needed for badges and signed coloring, and `st.dataframe` is interactive but style-limited. Hand-rolled HTML is ~40 lines total and gives full control.

All new CSS is scoped under `body:has(.rules-page-marker)` (mirrors the existing landing/agent-page-marker pattern), so no risk of bleed onto other tabs.

## Design tokens (reuse existing)
- Header bg: `var(--navy-900)` at ~92% opacity, white text, Manrope, `letter-spacing: 0.04em`, uppercase
- Row bg: `#FFFFFF` / zebra `#F8FAFC`
- Hairline: `rgba(15,23,42,0.06)`
- Text: `var(--navy-900)` primary, `#475569` secondary
- Positive numeric: `#0F766E` (teal)
- Negative numeric: `#B45309` (amber, already in palette)
- Container: `border-radius: 14px`, `overflow: hidden`, `border: 1px solid var(--hairline)`, `box-shadow: 0 2px 8px rgba(15,23,42,0.05)`

## Task 1 — Scoping marker
Add near the top of the rules branch (after `st.button("Back to Home"…)`):
```python
st.markdown('<div class="rules-page-marker" style="display:none;"></div>', unsafe_allow_html=True)
```

## Task 2 — Scoped stylesheet
Add a new CSS block in the existing `<style>` region:
- `.rules-table-wrap` — rounded, hairline, shadow container
- `.rules-table` — `width:100%; border-collapse:separate; border-spacing:0; font-family:Inter; font-size:13px`
- `.rules-table thead th` — navy bg, white, Manrope, 12px uppercase, 0.04em tracking, 14px vertical padding
- `.rules-table tbody td` — 12px vertical padding, hairline bottom, `vertical-align:middle`
- `.rules-table tbody tr:nth-child(even) td` — `background:#F8FAFC`
- `.rules-table tbody tr:hover td` — `background:rgba(28,79,192,0.05)`
- `.rules-table td.num` — `text-align:right; font-variant-numeric:tabular-nums`
- `.rules-table td.num.pos` — color teal, `font-weight:600`
- `.rules-table td.num.neg` — color amber, `font-weight:600`
- `.rules-badge` — inline-flex pill: `padding:3px 10px; border-radius:999px; font-size:11.5px; font-weight:600; letter-spacing:0.01em`
- Per-status badge tints: Covered (blue-100), Preferred (indigo-100), Not Covered (slate-100), Specialty (teal-100)
- Per-analog badge tints: BCBS, Providence, Blended (each subtle hue)

## Task 3 — Status Transition Mapping table
Replace `st.table(step_df)` with a Python-built HTML string:
```python
def _status_badge(v): ...   # returns <span class="rules-badge status-{slug}">...</span>
def _analog_badge(v): ...
def _signed(v):             # returns <td class="num pos">+1</td> / neg
    cls = "pos" if v > 0 else "neg" if v < 0 else "zero"
    sign = "+" if v > 0 else ""
    return f'<td class="num {cls}">{sign}{v}</td>'

rows = "".join(
    f"<tr><td>{_status_badge(r['Current'])}</td>"
    f"<td>{_status_badge(r['Future'])}</td>"
    f"<td>{_analog_badge(r['Analog'])}</td>"
    f"{_signed(r['Step'])}{_signed(r['Reverse'])}</tr>"
    for r in step_df.to_dict('records')
)
st.markdown(
    f'<div class="rules-table-wrap"><table class="rules-table">'
    f'<thead><tr><th>Current</th><th>Future</th><th>Analog</th>'
    f'<th class="num">Step</th><th class="num">Reverse</th></tr></thead>'
    f'<tbody>{rows}</tbody></table></div>',
    unsafe_allow_html=True,
)
```
Drops the index gutter entirely.

## Task 4 — Analog Curves table
Same treatment. Numeric cells for BCBS/Providence/Blended get `num pos`/`num neg` class, rendered to 4 decimals. Month column is left-aligned with slightly muted color and slightly smaller weight. Table wrapped in the same `.rules-table-wrap`.

## Task 5 — Section header consistency (light touch)
The four `<h4>` section headers already use Manrope + a cyan underline — leave them alone but bump their `margin-top` to `28px` so tables breathe. No color/weight changes.

## Task 6 — Verify
- `python -m py_compile DSS_app.py`
- Confirm the CSS block is inside the existing `<style>` scope
- Reload webapp; check landing + agent pages render identically (scoping via `.rules-page-marker` guarantees isolation)

## Out of scope
- No changes to Data Sources cards, Projection Formula box, or National Roll-Up narrative
- No changes to `STEP_TABLE` dict or `ANALOG_CURVES` data
- No changes to computation logic, session state, or navigation
