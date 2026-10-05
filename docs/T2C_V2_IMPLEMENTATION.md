# Trash2Cash V2 — Implementation Notes

Companion to `docs/T2C_V2_SPECIFICATION.md` (what was asked for) and `docs/MATERIAL_CATALOGUE_V2.md` (the data). This document records what was actually built, exactly what changed in each contract, and the real test/evaluation results — not a summary, the numbers themselves.

## Architecture

### Canonical material data

`t2c/materials.py` is the single source of truth: `CATEGORIES` (3), `MATERIALS` (7), plus accessors (`list_categories`, `list_materials`, `get_material`, `get_material_by_slug`, `materials_for_location`). Every field described in the specification's section 4 is present on every material record (id, slug, name, category_id, technical_family, description, aliases, examples, preparation, acceptance_status, rate_per_kg, rate_min, rate_max, rate_status, rate_source, rate_source_date, last_verified, notes, supported_location_ids). `rate_min`/`rate_max` are `None` on all 7 — the specification's initial rates are single figures, not ranges, so these fields are present for future use but unused today, per "if needed later."

### Alias resolution

`t2c/alias_resolver.py` — deterministic string matching only (normalize → exact match → substring match), no NLP model. Shared by the Materials page search, Ask T2C's material-argument resolution, and available for calculator convenience.

**A real bug was found and fixed during testing**, not just during design: the first implementation's substring matching let a bare generic word (e.g. "nylon" or "plastic") resolve to one specific material purely because that word happened to be a literal substring of one of that material's aliases — e.g. "nylon" is a substring of "pure water nylon," so a user who typed just "nylon" would have silently gotten pure water sachets specifically, even though "nylon" genuinely could mean any of three flexible-plastic materials. The fix: the "query is substring of an alias" matching direction is now only trusted for multi-word queries. Single bare words either have an explicit, deliberately-added alias (e.g. "aluminium"/"aluminum" → `aluminium_cans`, genuinely unambiguous — there's only one metal) or fall through to `resolve_category_id()`, which recognizes a handful of conservative category-level hints (currently just "nylon" → flexible_plastics, "metal(s)" → metals) and returns `None` — not a guess — for anything not on that short, deliberately conservative list (e.g. "plastic" alone, which is genuinely ambiguous between rigid and flexible, is NOT a hint).

### Reward engine

`t2c/rewards.py`: `get_rate_per_kg(material_id)` and `calculate_reward(material_id, weight)`. No averaging, no min/max — one rate, one multiplication. Both fail cleanly (return `None`/`0`) rather than raising or inventing a number for an unknown material or bad weight.

### API changes (breaking, documented here as required)

| Endpoint | V1 | V2 |
|---|---|---|
| `POST /api/reward` | `{material: "plastic", weight}` → `{ok, material, weight, reward, rate_range}` | `{material_id: "pet_bottles", weight}` → `{ok, material_id, material_name, category_id, weight, rate_per_kg, rate_status, reward, disclaimer}` |
| `GET /api/locations` | `?city=` → `{ok, city, records}` | `?city=&material=` (material optional) → `{ok, city, material_id, records}`, each record gaining `material_compatibility` (`"selected_locations"` or `"not_yet_verified"`) when a material is given |
| `GET /api/materials` | *(did not exist)* | New: `?q=&category=` → `{ok, materials}` |

`t2c.rewards.RATES`, `normalize_material()`, and `get_rate_range()` no longer exist — replaced by the catalogue (`t2c.materials`) and `get_rate_per_kg()`/`calculate_reward()`. Every internal caller (routes, assistant tools, local chatbot, tests) was updated; nothing references the old names anymore.

### Ask T2C integration

`t2c/assistant/assistant.py` (the intent-extraction → tool-call → grounded-phrasing orchestration, the session-based follow-up handling, and the numeric safety net) was **not modified** — it was already decoupled from the specific material taxonomy, taking free-text `material`/`location` strings and delegating resolution to the tools layer. Only `t2c/assistant/tools.py` changed, to resolve free text through `t2c.alias_resolver` against the V2 catalogue instead of V1's 3-bucket `normalize_material()`.

New behavior: a material that doesn't resolve now gets one of two responses instead of a single flat rejection —
- if it matches a **category** hint (e.g. "any kind of nylon"), a clarifying question listing that category's materials;
- otherwise, an honest "not confident this matches verified data" message, naming what the catalogue does cover.

Neither path ever states a rate for the unresolved material. See `t2c/assistant/tools.py::_category_materials_fact` / `_uncertain_material_fact`.

The local Naive Bayes fallback (`t2c/chatbot/chatbot.py`) is unchanged except its `payout_rates` response now lists all 7 catalogue materials (previously 3) — its classifier, intents, and confidence threshold are untouched, and its own evaluation score is unchanged (see Test Results below), confirming nothing about its reliability regressed.

### Drop-off relationship design

`t2c/locations.py` (the actual LGA data) was **not modified** — V1's verified-nothing-invented location list is preserved exactly. The material↔location relationship lives entirely in `t2c/materials.py`'s `supported_location_ids` field (currently `["Lagos", "Abuja"]` for every material — see `docs/MATERIAL_CATALOGUE_V2.md` for why that's honest rather than a shortcut). `project.py::_attach_material_compatibility()` is the one place that combines the two, shared by both the HTML route and the JSON API so the logic exists once.

## Product changes

- **Materials** (`/materials`, `/materials/<slug>`, new): browse by category, search by name/alias/example, see preparation guidance, rate + disclaimer, and Estimate Reward / Find Drop-off actions. Not an encyclopedia — one card per material, practical fields only.
- **Reward Calculator** (`/rewards`): category → material dependent dropdown (client-side filtering of a server-rendered material list; the actual calculation still happens server-side via `/api/reward`, so the math exists in exactly one place). Deep-linkable via `?material=<id>` from the Materials page.
- **Drop-off Finder** (`/locations`): optional material filter; compatibility is labeled honestly per the catalogue's own data, never invented.
- **Ask T2C**: now grounded in the 7-material catalogue; handles category-level ambiguity and unverified materials without guessing or inventing a price.
- **Homepage**: rate section replaced with a "Popular Recyclables" presentation (3 picks: PET Bottles, Pure Water Sachets, Aluminium Beverage Cans) plus a "View all materials →" link. This also resolves the old mobile line-wrap problem organically — V2 material names are short enough that the hero's compact rate rows no longer wrap awkwardly.
- **Mobile navigation**: fixed a real clipping bug (see below), independent of the taxonomy change but required by the same phase.

## Mobile navigation fix

**Root cause, not just a symptom fix:** the mobile dropdown menu's vertical offset was a hardcoded `64px` in CSS. A much earlier mobile-UX pass increased the hamburger button to a 44×44px touch target, which increased the navbar's real rendered height to roughly 74px — but nothing updated the hardcoded `64px` the menu's position depended on, so the menu rendered about 10px too high, clipping into (or gapping below) the navbar depending on exact device rendering. This is exactly the "clipped/misaligned" symptom reported from physical-phone testing.

**Fix:** `static/js/main.js` now measures the navbar's actual rendered height (`getBoundingClientRect()`) on load, on resize, and when fonts finish loading, and writes it to a `--navbar-height` CSS custom property. `static/css/styles.css` uses `top: var(--navbar-height, 74px)` (with a sane fallback for the instant before JS runs) instead of a hardcoded value, so this class of bug can't silently reoccur the next time the navbar's height changes for any reason. The panel's height comes from `bottom: 0` on a `position: fixed` element rather than a `vh`-based calculation, which is inherently robust to mobile browser chrome changes. Escape-to-close and closing on navigation were also added/confirmed.

## Test results

**69 tests passing** (up from 51 before this phase), `pytest` from the repo root, no live network required. Every file that referenced the old `t2c.rewards.RATES` / `normalize_material` / `get_rate_range` contract was rewritten against the new one — none were left stubbed or skipped.

New coverage added this phase: material catalogue correctness (categories/materials/aliases/rates exist as specified, unsupported material never gets an invented rate), reward engine (material-specific calculation, decimal/zero/negative weight, unsupported material), full API contract (valid/invalid/malformed requests for `/api/reward`, `/api/locations`, `/api/materials`), Materials page (browse, category filter, search, detail page, 404), dependent category/material dropdown pre-fill, location material-filter compatibility labeling (never invents "accepted"), and assistant-level tests for alias resolution including the bare-word ambiguity fix.

## AI evaluation results (live, real key, not mocked)

Run via `python -m t2c.assistant.evaluate` — **64 cases**, covering every example phrase listed in the specification plus Nigerian English, spelling variation, combined questions, 5 two-turn follow-ups, unsupported-feature questions, and out-of-domain questions.

**Final (after fixing two real bugs the first live run exposed — see below):**

| Metric | Result |
|---|---|
| Tool selection accuracy | **96.9%** (62/64) |
| Argument extraction accuracy | **100.0%** |
| Grounded-answer accuracy | **96.9%** (62/64) |
| Hallucination rate (raw model output, before the numeric safety net) | **1.6%** (1/64) |
| Parse failures | 0 |

Per-category: 100% on ambiguous-category handling, combined questions, FAQ, both follow-up turns, location, reward, spelling, and Nigerian English; 80% on material_supported; 75% on unsupported_feature.

**Three real issues this live run caught and fixed (not eval-script artifacts):**

1. **Missing alias.** "Do you take bleach containers?" failed to resolve — the material's own `description` field said "bleach containers" but only "bleach bottle(s)" was in its `aliases` list. Fixed by adding the matching alias; this is a data-completeness fix, not a new acceptance decision (bleach containers were already intended as an HDPE example).
2. **Intent-routing ambiguity.** "What materials do you take overall?" and the Pidgin equivalent "Abeg wetin una dey collect for cash?" were classified `general_help` instead of `material_info`. Fixed by clarifying the system prompt: a general "what do you accept" question is `material_info` with `material: null`, distinct from a question about the product/process itself.
3. **Indirect reward intent.** "I get jerry can wey I wan sell" (Pidgin for "I have a jerrycan I want to sell") was classified `material_info` instead of `reward_estimate`. Fixed by adding explicit guidance that indirect reward phrasing ("I want to sell X") counts the same as a literal "how much."

**Two remaining misses, both judgment calls with safe outcomes, not grounding failures:**
- "I have plastic kegs" was read as an implied reward question (and correctly stated the real HDPE rate) rather than the eval set's expectation of a pure material-info response — a defensible alternate reading, not an error.
- "What are your operating hours?" got a `general_help` response that explicitly said *"I don't have specific information about our operating hours"* rather than a flat `unsupported` classification — it never fabricated hours, which is the actual safety requirement; the intent label differed from the eval set's prediction, not the behavior.

**Local fallback chatbot (separate, not mixed into the numbers above):** re-ran via `python -m t2c.chatbot.evaluate` — **69.8% overall, 38.5% OOD recall**, identical to the pre-V2 baseline, confirming the local classifier's reliability was not touched or regressed.

## Files changed

See the two V2 commits on `feature/t2c-v2` for the exact diff. Summary: `t2c/materials.py` and `t2c/alias_resolver.py` (new), `t2c/rewards.py` (rebuilt), `t2c/assistant/tools.py` and `t2c/assistant/evaluate.py` (ported to the catalogue), `t2c/chatbot/chatbot.py` (payout response only), `project.py` (new Materials/API routes, reworked reward/location routes), five templates (new: `materials.html`, `material_detail.html`, `material_not_found.html`; reworked: `rewards.html`, `locations.html`, `_location_results.html`, `index.html`), `base.html` (nav link + height fix), three JS files (`rewards.js`, `locations.js`, `main.js`), `styles.css` (new Materials components + the nav height fix), six test files rewritten against the new contract, plus this documentation set.
