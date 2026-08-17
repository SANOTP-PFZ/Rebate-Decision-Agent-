# Plan — Landing Page Redesign

## Where we are today

The current landing page (`DSS_app.py` lines 1303-1330) is functional but plain:

- A wide sky-blue **header bar** with a small Pfizer logo + `REBATE DECISION AGENT` wordmark.
- A narrow centered **Disclaimer card** with a paragraph and 4 bullets.
- A big blue **"Rebate Decision Agent"** primary button + a white **"Business Rules"** secondary button, stacked vertically in a narrow center column.
- No footer, no branding beyond the header, no visual hierarchy, no imagery / iconography, lots of empty vertical space.

The **agent page** (already redesigned) looks polished — the landing should feel like the same product.

## Design goals

1. **Hero first, disclaimer second.** A visitor landing here should immediately understand *what* this tool is and *what they can do*, not scroll past legalese.
2. **Two clear destinations** — Rebate Decision Agent (primary action) and Business Rules (reference) — presented as **navigation cards**, not stacked full-width buttons.
3. **Same visual language as the agent page** — navy `#0A1A3D` / `#163990`, accent `#41B6E6`, Manrope headings, Inter body, hairline borders, soft shadows, no bright fills.
4. **Compact disclaimer** — collapsible or in an inset, not the visual center of the page.
5. **Footer** matching the agent page (`Data as of Mar 2026 • Source: Xponent (Plantrak) via Dataiku • Pfizer Confidential`).
6. **Zero backend changes** — only edits inside the `if st.session_state.page == 'landing':` block and its CSS (`.pfizer-header`, `.disclaimer-box`, landing-scoped button rules).

## Proposed new layout (top → bottom)

```
┌────────────────────────────────────────────────────────────────┐
│  [Pfizer logo]  Rebate Decision Agent                          │  ← slim brand bar
│                 Nurtec® Payer Model                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   HERO                                                          │
│   ┌──────────────────────────────────────────────────────┐    │
│   │  Nurtec® Payer Model                                  │    │
│   │  Simulate the market-share impact of formulary        │    │
│   │  status changes across MCOs, in seconds.              │    │
│   │                                                        │    │
│   │  • 2,700+ MCOs   • 36-month horizon   • 3 analogs     │    │
│   └──────────────────────────────────────────────────────┘    │
│                                                                │
│   NAV CARDS (2 columns)                                        │
│   ┌───────────────────────┐   ┌───────────────────────┐       │
│   │  ▶  Rebate Decision   │   │  📘 Business Rules    │       │
│   │     Agent             │   │                       │       │
│   │                       │   │  How projections are   │       │
│   │  Model a formulary    │   │  computed, data        │       │
│   │  status change and    │   │  sources, and analog   │       │
│   │  see 12-month impact  │   │  methodology.          │       │
│   │                       │   │                       │       │
│   │  Open agent  →        │   │  View rules  →        │       │
│   └───────────────────────┘   └───────────────────────┘       │
│      (primary — navy fill)      (secondary — white)            │
│                                                                │
│   COMPACT DISCLAIMER                                           │
│   ┌──────────────────────────────────────────────────────┐    │
│   │ ⓘ  Indicative projections only — not a financial      │    │
│   │    commitment. [ Read full disclaimer ▾ ]              │    │
│   └──────────────────────────────────────────────────────┘    │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  Data as of Mar 2026 • Source: Xponent (Plantrak) via Dataiku  │
│  • Pfizer Confidential                                          │
└────────────────────────────────────────────────────────────────┘
```

## Detailed changes

### 1. Brand bar (replace `.pfizer-header`)

- Slimmer height (~64 px instead of the current ~90 px thick block).
- Left: real Pfizer logo (same CDN URL we use on the agent sidebar) + `Rebate Decision Agent` + subtitle `Nurtec® Payer Model`.
- Right: environment badge (`Internal • Dataiku`) — small pill for context.
- Hairline border at bottom, not a gradient block.

### 2. Hero block

- Manrope heading, large: **"Nurtec® Payer Model"**.
- Inter body, muted: one-sentence value prop about what this tool does.
- Small stat row: `2,700+ MCOs · 36-month horizon · 3 analogs (BCBS, Providence, Blended)` — as inline pills.

### 3. Nav cards (2-column grid)

- **Card A — Rebate Decision Agent (primary):** navy `#163990` fill, white text, arrow-right icon, one-line description, `Open agent →` CTA. Clickable card (whole card is the button target). Hover: `translateY(-2px)` + deeper shadow.
- **Card B — Business Rules (secondary):** white card, hairline border, navy text, `View rules →` CTA. Same hover pattern.
- Equal height, `grid-template-columns: 1fr 1fr; gap: 20px`. On narrow viewports collapse to 1 column.
- Icons: use inline SVG (no external deps) — a small "lightning" or "target" for the agent, a "book" for rules.

### 4. Compact disclaimer

- One-liner in an inset panel with `ⓘ` glyph and a `Read full disclaimer ▾` toggle (Streamlit `st.expander`).
- Expander body contains the current 4 bullets. Closed by default.
- This reclaims ~200 px of vertical space above the fold.

### 5. Footer

- Reuse the agent-page `.agent-footer` style (center-aligned, muted, hairline top).
- Same content string.

### 6. CSS namespace

- New classes: `.landing-brandbar`, `.landing-hero`, `.landing-stat-pill`, `.landing-nav-grid`, `.landing-nav-card`, `.landing-nav-card--primary`, `.landing-nav-card--secondary`, `.landing-disclaimer-compact`, `.landing-footer`.
- Scope everything to a `body:has(.landing-page-marker)` root so it can't leak into the agent or rules pages.
- Keep existing `.pfizer-header` in the code but stop rendering it on the landing page (still used for the rules page — or migrate rules to the new brandbar in a follow-up).

## Streamlit-specific notes

- Nav cards can't be a real `<a href>` (Streamlit doesn't allow route links), so implement each card as a native `st.button` with `use_container_width=True` and style the button itself to look like the card (padding, alignment, inner HTML label via `st.markdown` above the button + button as CTA row). Or: wrap the whole thing as a single big button and put the description inside the button label using an HTML label workaround.
- **Cleaner alternative**: render the card visuals with `st.markdown`, and place a small transparent full-width button *over* the card using absolute positioning. This is the pattern used in polished Streamlit apps to make entire tiles clickable. Trade-off: fragile against Streamlit's DOM changes.
- **Simplest**: two `st.button` calls styled to look like large cards, each with a multi-line label. Streamlit renders `\n` in button labels as line breaks with `use_container_width` — we style with min-height, left-align text, add pseudo-element arrow.

I'd recommend the **simplest option** first and only go to the absolute-positioning trick if the button label limitation is too restrictive.

## Non-goals for this pass

- No changes to the agent page (already polished).
- No changes to backend / data / calc functions.
- No changes to the Business Rules page in this pass (can be a follow-up so it inherits the same brandbar + footer).
- No routing changes — still page-state driven with `go_to_agent` / `go_to_rules` / `go_to_landing`.

## Verification steps

1. `py_compile` after each edit block.
2. Grep the 16 preserved backend anchors (`load_data`, `apply_analog`, `compute_national_ms`, `STEP_TABLE`, `ANALOG_CURVES`, etc.) to confirm no accidental changes.
3. Visual check: reload the landing page in Dataiku and verify (a) brand bar looks slim + branded, (b) hero + stat pills render, (c) both nav cards are the same height, (d) primary card has navy fill, (e) disclaimer collapses, (f) footer matches agent page.
4. Click both nav cards → confirm they route to agent / rules.
5. Confirm no regression on agent page (nothing landing-namespaced should apply there).

## Open questions (answer inline if you want to pin them down before I implement)

1. **Hero copy** — is `"Simulate the market-share impact of formulary status changes across MCOs, in seconds."` acceptable, or do you want me to draft a couple alternatives?
2. **Environment badge** — include a small `Internal • Dataiku` pill in the brand bar, or drop it?
3. **Icons on nav cards** — inline SVGs are fine, or would you prefer emoji fallbacks for zero-dependency simplicity?
4. **Business Rules brand bar** — migrate it to the new brand bar in this same pass, or leave for a follow-up?
