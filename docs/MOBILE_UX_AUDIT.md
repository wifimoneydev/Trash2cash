# Mobile-First UX Audit — Trash2Cash

*Audit date: 2026-09-23. Verified by reading every relevant template/CSS/JS file and reasoning through actual computed layout math (container widths, padding, font metrics, touch-target sizes) at each required breakpoint — not by guessing. No browser or screenshot tool was available in this environment; see "Verification method" below for exactly what that does and doesn't cover.*

## Verification method (read this first)

There is no browser automation or screenshot tool available in this session. Every finding below was reached one of these ways, and each finding says which:

1. **Computed layout math** — actual container widths, paddings, font sizes, and touch-target dimensions calculated by hand from the real CSS values at each breakpoint (375/390/430/768/1024/1440px), the same way the Phase 4 redesign's contrast ratios were computed rather than eyeballed.
2. **Direct code reading** — tracing what actually happens (DOM order, CSS `order`, `display: none`, viewport units) rather than assuming.
3. **Automated checks that did run**: `pytest` (51/51), HTML tag-balance checking, CSS brace-balance checking, live HTTP requests to every route and every new image file.

What this does **not** cover: actual rendered pixels, font-rendering edge cases, real mobile keyboard behavior, real touch interaction feel. Recommend a real-device pass before treating this as fully closed — flagged again at the end.

---

## Findings by area

### Navigation

| # | Finding | Severity | Status |
|---|---|---|---|
| N1 | The primary "Calculate Reward" CTA was set to `display: none` on any viewport ≤1080px — it didn't shrink, it **disappeared entirely** from the mobile nav. A mobile user opening the menu saw six text links and no path to the app's main action. | **High** | Fixed — the CTA now renders as a full-width button inside the mobile menu list instead of vanishing. |
| N2 | The hamburger toggle button was ~34×34px (icon 20px + padding ~7px each side) — below the 44×44px minimum touch target. | Medium | Fixed — explicit `width: 44px; height: 44px` with centered icon. |
| N3 | Header height itself (computed): ~60px total (0.9rem padding-block × 2 + content) — reasonable, not "too tall." | — | No change needed. |
| N4 | Mobile menu link rows: ~50px each (computed from padding-block 0.85rem + line-height) — comfortably above the touch-target minimum already. | — | No change needed. |

### Homepage

| # | Finding | Severity | Status |
|---|---|---|---|
| H1 | On mobile, `.hero-panel { order: -1; }` moved the **rate-preview panel above the headline and CTA**. A first-time mobile visitor's first content was a price table, before "Turn Waste Into Value" or any explanation of what Trash2Cash is. This directly fails the "is the value proposition understandable immediately" check. | **High** | Fixed — removed the `order` override; headline/CTA now stay first in natural document order on mobile. |
| H2 | Vertical spacing (`section { padding-block: clamp(3rem, 6vw, 5.5rem); }`, reduced further to 2.5rem at ≤480px) — computed at 375px this resolves to the 3rem/2.5rem floor, not the larger end of the clamp. No excessive empty space found. | — | No change needed. |
| H3 | Feature grid and steps both collapse to 1 column at ≤640px — verified no cramped multi-column squeeze at any required breakpoint. | — | No change needed. |
| H4 | New photo-collage section (added this pass): the accent image's negative offset (`right: -1.75rem`) exceeded the collage's centered margin at 375px by ~6.5px — a real horizontal-overflow risk, caught before shipping by computing exact numbers, not by assumption. | Medium (self-introduced, caught pre-ship) | Fixed — narrower collage + reduced offset at ≤480px. |

### Reward Calculator (flagged as a key mobile workflow)

| # | Finding | Severity | Status |
|---|---|---|---|
| R1 | Input font-size is 16px — correctly prevents iOS Safari's auto-zoom-on-focus (a common mobile form bug). | — | Already correct. |
| R2 | `inputmode="decimal"` is set on the weight field — triggers the numeric keyboard. | — | Already correct. |
| R3 | Submit button and inputs are ≥44px tall (computed from padding). | — | Already correct. |
| R4 | **Result visibility**: the result panel renders directly below the submit button inside the same card. On a short viewport (e.g. iPhone SE, 375×667) with the dark intro section above the form, the button can sit near the bottom of the visible area — meaning the newly-revealed result could land below the fold with nothing prompting the user to scroll down and find it. This matters specifically because the brief calls out that a user may be standing with materials in hand, wanting the number *now*. | **Medium** | Fixed — `showResult()` now checks if the panel is fully within the viewport and smooth-scrolls it into view if not (respects `prefers-reduced-motion`). |
| R5 | Values persist for editing after a result (native form + JS both preserve field values). | — | Already correct. |
| R6 | Loading state ("Calculating…", disabled button) and error state (red panel, clear message) both present. | — | Already correct. |

### Drop-off Finder

| # | Finding | Severity | Status |
|---|---|---|---|
| D1 | City-tab pill buttons computed to ~42.7px tall — just under the 44px guideline. | Low-Medium | Fixed — `min-height: 44px` added. |
| D2 | Location cards: `minmax(240px, 1fr)` grid resolves to a single column at every mobile width tested (343px available at 375px) — no cramped cards. | — | No change needed. |
| D3 | No distance/hours/address data is shown, by design (matches the existing "not yet available" honesty pattern) — not a UX bug, a deliberate accuracy choice already in place. | — | No change needed. |

### Ask T2C

| # | Finding | Severity | Status |
|---|---|---|---|
| A1 | `.chat-shell` height was set in plain `vh` units (`min(680px, 72vh)`, `78vh` at ≤480px). Plain `vh` on mobile browsers is calculated against the *largest possible* viewport and does not reliably shrink when the on-screen keyboard opens or the address bar is visible — the classic "chat input hidden behind the keyboard" bug this brief explicitly warns about. | **Medium-High** | Fixed — added `dvh` (dynamic viewport height) as a progressive enhancement layered after the `vh` fallback, so modern mobile browsers size the shell against the *actual* visible area. |
| A2 | Suggested-prompt chips computed to ~36px tall — below the touch-target minimum. | Medium | Fixed — `min-height: 44px` added. |
| A3 | `.msg` bubbles had no `overflow-wrap` rule — a long unbroken token (rare, but possible) could overflow the bubble's `max-width` instead of wrapping. | Low | Fixed — `overflow-wrap: break-word` added. |
| A4 | Send button (48×48px) and message max-width (88% at ≤640px) were already correctly sized. | — | No change needed. |
| A5 | The chat box sits in normal page flow below a hero section, not pinned to the viewport — reaching it requires an initial scroll on mobile. Considered adding a sticky "jump to chat" affordance; decided against it (see "Deliberately not done" below). | Low | Not changed — judgment call, documented. |

### Images (new this pass)

| # | Finding | Severity | Status |
|---|---|---|---|
| I1 | All 13 raw images carried a visible third-party watermark and (mostly) real organization branding — audited in full in `docs/IMAGE_ASSET_AUDIT.md`. | **High** (resolved via user confirmation, not a code fix) | Resolved — permission confirmed; watermark removed via geometric crop only, never AI-edited. |
| I2 | Placed images use `width`/`height` attributes matching true intrinsic ratio, `srcset` for responsive sizing, and `loading="lazy"` (both placements are below the fold). | — | Implemented correctly from the start; verified via `getsize()` on every generated file and live HTTP checks. |
| I3 | Total new image payload: 8 files, 652 KB combined, 34–150 KB each depending on breakpoint — no single request serves a multi-megabyte original to a phone. | — | Verified. |

### Typography

| # | Finding | Severity | Status |
|---|---|---|---|
| T1 | `h1` uses `clamp(2.25rem, 4vw + 1rem, 3.5rem)` — computed at 375px this resolves near the 2.25rem (36px) floor. Estimated (not visually confirmed) wrap: "Turn Waste Into" / "Value." across two lines, no orphaned single short word. | Low, unverified visually | Flagged for real-device confirmation, not changed blindly. |
| T2 | The longest recurring string, "Nylon (Pure water sachets)," is handled by the hero-panel-row `flex-wrap` fix already shipped in Phase 4 — re-confirmed still present and correct. | — | Already correct. |
| T3 | Location cards only show short LGA names today (Ikeja, Surulere, etc.) — no long-name wrapping risk currently, though nothing would break if a longer one were added (no `white-space: nowrap` anywhere in that component). | — | No change needed. |

### Touch

All interactive controls were checked against a 44×44px minimum. Three were under it (nav-toggle, city-tab, suggestion-chip) — all three fixed above. No interaction anywhere in the app depends on `:hover` alone; every hover style has a non-hover equivalent (native focus/active states, or the control is directly tappable regardless).

---

## Deliberately not done (Phase 5 — avoiding mechanical additions)

The brief explicitly warns against adding mobile-specific patterns "mechanically." Considered and **rejected** for lack of a genuine need in the current product:

- **Sticky bottom action bar** — the mobile nav CTA fix (N1) already restores one-tap access to the calculator without a persistent floating element that could cover content (itself a named risk in the brief's own testing checklist).
- **Horizontally swipeable content** — nothing in the current IA (a 3-material rate table, a handful of location cards, a 4-step list) is long or homogeneous enough to benefit from a swipe pattern; it would be decoration, not function.
- **Bottom-sheet interactions** — no current flow (material select, city select) has enough option volume to justify replacing a native `<select>`/button group with a custom sheet.

---

## Files changed this pass

- `static/css/styles.css` — touch targets (nav-toggle, city-tab, suggestion-chip), hero mobile ordering, mobile nav CTA, chat-shell `dvh`, `.msg` overflow-wrap, new `.photo-feature`/`.photo-collage`/`.about-photo` components + their responsive rules.
- `static/js/rewards.js` — scroll-into-view for the result panel.
- `templates/index.html` — new "Recycling starts with real work" photo section.
- `templates/about.html` — new contained image + caption in "The problem" section.
- `static/images/*.webp` (8 new files) — cropped, resized, optimized web copies of 3 approved source photos.
- `docs/IMAGE_ASSET_AUDIT.md`, `docs/MOBILE_UX_AUDIT.md` — this documentation.

No changes were made to `project.py`, `t2c/rewards.py`, `t2c/locations.py`, `t2c/assistant/*`, or any test file — confirmed by re-running the full suite (51/51 passing, unchanged from before this pass) and by not touching those files at all.

## Remaining limitations

- No real browser/device verification — everything above is structural/computed, not pixel-confirmed. This is the single biggest open item.
- Headline wrap at 375px (T1) is estimated, not confirmed.
- `dvh` has near-universal modern support but isn't 100% — very old mobile browsers silently fall back to the (less precise) `vh` value, which is a graceful degradation, not a failure, but worth knowing.
- The 10 unused source photos remain available in `assets/` if a future pass wants more imagery elsewhere (Education section, Drop-off Finder cards) — none were forced in just to "use what exists," per the brief's own instruction.

## Future recommendations

1. A real-device pass (or even just the user's own phone) to confirm T1 (headline wrap) and A1 (keyboard behavior on Ask T2C) — the two findings that couldn't be verified structurally.
2. If T2CVision ships a real "Identify Waste" camera/upload flow, audit that mobile capture UX specifically — it doesn't exist yet, so it wasn't (and couldn't honestly be) audited here.
3. Revisit the "Deliberately not done" list only if real usage data suggests otherwise — don't add sticky/swipe/bottom-sheet patterns speculatively.
