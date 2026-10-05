# Trash2Cash — Engineering Development History

This is an engineering record, not marketing copy. Every entry below is reconstructed only from verifiable repository evidence: `git log`, tags, branches, commit diffs, and existing project documentation (`T2C_PROJECT_STATUS.md`, `docs/T2C_V2_SPECIFICATION.md`, `docs/T2C_V2_IMPLEMENTATION.md`, `docs/MATERIAL_CATALOGUE_V2.md`, `docs/IMAGE_ASSET_AUDIT.md`, `docs/MOBILE_UX_AUDIT.md`). No dates, bug counts, metrics, or decisions are invented. Where the repository does not provide enough evidence to reconstruct a step (diagnosis, validation, or lesson), that gap is stated explicitly rather than filled.

All commit hashes below were re-verified against `git log` at the time this document was written. Current git state:

- `main`, `backup/t2c-v1`, and tag `t2c-v1-stable` all point to `1380fd4e869f27231137a3020c30e695f623b92f` ("Mobile UX fixes and real photography integration") — confirmed via `git rev-parse main backup/t2c-v1 t2c-v1-stable`.
- `feature/t2c-v2` branches from that same commit and currently sits at `6a91bfbe5a65a4aabdb566fab5d70f20b4bb17fe` ("Improve customer-facing rate status labels").

---

## Pre-history: early prototyping (2025-05-23 to 2025-06-21)

### Challenge / discovery
The earliest commits (`e4fc186c` through `5305e323`) show a Flask chatbot prototype being built up, with repo structure problems appearing early: an embedded git repository inside `t2cchatbot/spider`, duplicate nested copies of the project (`trash2cash/`, `trash2cash/trash2cash/`), a tracked virtualenv, and a large image dataset committed directly to git.

### Evidence
Commit messages from this period: "Fix: removed embedded git repo from t2cchatbot," "Fixed embedded repo in t2cchatbot/spider," "fixed broken about and contact routes & applied better styling" (appears twice, on diverging branches `d4f17330`/`c73eebe0`, both merged back via `50f278cc` and `083ef2bb`), "Temp commit before cleaning venv history," "Remove large dataset from Git," "Add plastic image dataset" (a merge commit).

### Diagnosis
Not independently reconstructable in detail. Commit messages are terse ("update," "Temp commit") and do not describe root causes for the broken about/contact routes or why the repo structure duplicated itself. The later Phase 1 cleanup (see below) describes the *end state* of this duplication in detail, which is the best available evidence for what this period left behind.

### Fix
Large-file and embedded-repo issues were addressed iteratively across several commits (`a248ccb6` .gitignore + `.DS_Store` removal, `aa4c1aa2` large dataset removal, `e869af9c`/`5305e323` further `.gitignore` updates) rather than in one pass.

### Validation
No test suite existed yet in this period — no evidence of automated validation.

### Result
By the end of this period the repo contained four overlapping copies of the app (confirmed directly by the Phase 1 commit message below) and a git-tracked virtualenv, which Phase 1 later had to remove.

### Lesson
Explicitly stated in the repository as a known follow-up, not resolved in this history: the removed virtualenv's blobs and LFS-tracked `.pkl` files from that period still exist in git history (`T2C_PROJECT_STATUS.md`, Phase 1 section) — shrinking that history requires a deliberate `git filter-repo` + `git lfs prune` pass with separate sign-off, "not attempted" as of Phase 1.

---

## V1 Phase 0 — Checkpoint before repository cleanup
**Commit:** `f6ee4d34` (2026-09-13 10:47:33 -0400)

### Challenge / discovery
Before starting the nested-duplicate cleanup and package restructuring (Phase 1), pending local state needed to be captured as a safety checkpoint.

### Evidence
Commit message: "Snapshot of pending local state (workspace config, regenerated chatbot pickle, macOS metadata) plus the Phase 1 audit report, committed as a safety checkpoint before the nested-duplicate cleanup and package restructuring begins." Diffstat: `T2C_PROJECT_STATUS.md` (192 lines added), workspace config, regenerated `chat_model.pkl`.

### Diagnosis
N/A — this is a deliberate pre-work checkpoint, not a bug fix.

### Fix
N/A.

### Validation
Not applicable to a checkpoint commit; no test-count claim made.

### Result
A safe rollback point existed before any structural changes to the repository.

### Lesson
Checkpointing before a destructive-looking operation (removing duplicate trees) gives a recovery point without needing a separate backup mechanism — a pattern repeated later and more formally in the V1 protection strategy (see below).

---

## V1 Phase 1 — Repository cleanup and canonicalization
**Commit:** `77d795a3` (2026-09-13 10:59:40 -0400)

### Challenge / discovery
Four overlapping copies of the app existed: repo root, `trash2cash/`, `trash2cash/trash2cash/`, and `trash2cash/t2cchatbot/spider/`, including a git-tracked 4,580-file virtualenv and a nested duplicate app copy.

### Evidence
Commit message and `T2C_PROJECT_STATUS.md` Phase 1 section (read directly): the four copies were compared "file-by-file (`diff`, mtimes) rather than assumed." The root copy won on every compared file (newest by mtime, most feature-complete — POST-capable contact route, nicer templates). `t2cchatbot` existed in only one place and was promoted by necessity after stripping its internal `venv/` and nested `spider/` duplicate. `t2cvision`'s root copy won, having non-empty scaffold directories the nested copy lacked.

### Diagnosis
The nested duplication meant `app.py` had "its own broken, parallel set of routes and a dead import (`t2cchatbot.utils.tokenize`, from a file that was empty)." The chatbot's `payout_rates` intent returned a hardcoded USD string that contradicted the real Naira rates used by the calculator. The `/contact` route was missing `flash`/`redirect` imports and a `secret_key`, so posting the form raised an error. `t2c/vision/identify.py` had a double pixel-rescaling bug, and a missing trained model failed with a raw traceback rather than a clear error.

### Fix
Collapsed to one canonical tree rooted at the repo root. Introduced the `t2c/` package (`t2c/chatbot/`, `t2c/vision/`, new `t2c/rewards.py` and `t2c/locations.py` as single sources of truth for payout rates and drop-off data, "values unchanged from the original `project.py`"). Made `app.py` the one entrypoint. Fixed the chatbot's payout response to read from `t2c.rewards`. Fixed the `/contact` route's missing imports/secret key. Fixed the vision double-rescaling bug and made a missing model fail with an explicit error. Removed a second, non-functional chat widget from `index.html`. Added one root `requirements.txt`/`requirements-dev.txt`.

### Validation
Commit message states: "Verified from repo root: `pytest` (9 passed), `python app.py` (starts and serves real requests), and clean imports with no sys.path hacks."

### Result
Single canonical app tree; 9 passing tests (up from none recorded previously); chatbot rates now consistent with the calculator.

### Lesson
Selecting a canonical copy by direct file comparison (diff/mtime) rather than by default/assumption caught real functional differences between the duplicates (e.g. the `spider/` copy was missing the chatbot import entirely) that a naive "keep the root" choice could have gotten wrong in either direction.

---

## V1 Phase 2 — Business data reliability and chatbot quality
**Commits:** `740f46fc` (2026-09-13 11:16:39 -0400), `142dc356` (2026-09-13 11:25:53 -0400)

### Challenge / discovery
The reward/location/chatbot business logic had no measured quality baseline, and `normalize_material()` / weight handling didn't fail cleanly on bad input.

### Evidence
Commit message: confidence-gated chatbot responses were added (`MultinomialNB predict_proba`, 0.30 threshold); a new 53-case evaluation set (`t2c/chatbot/data/eval_set.json`) was added "to measure real intent accuracy and OOD/fallback behavior instead of guessing at quality."

### Diagnosis
Without confidence gating, the chatbot would guess on inputs it didn't understand. Training data (`data/intents.json`) had only 24 examples across 7 intents — too sparse, per the measured before/after accuracy change.

### Fix
Added confidence threshold (0.30), chosen empirically "as the highest value that doesn't reject the model's own canonical training phrases (bare 'Hi'/'Hello' score 0.315)." Expanded `intents.json` from 24 to 57 examples (same 7 intents, more paraphrases/Nigerian-English variants). Added `normalize_material()` so unknown materials/non-numeric/negative weights fail cleanly (return 0) instead of raising. Added `list_location_records()` with explicit `None` placeholders for unverified fields — "no data invented." `142dc356` added `.env` to `.gitignore` ("Ignore environment secrets").

### Validation
Commit message states the training-data expansion raised "same-threshold accuracy from 60.4% to 69.8%," and documents the trade-off explicitly: "this also lowered raw OOD recall at a fixed threshold, reported rather than hidden." Full suite: "28 passed, up from 9" (19 new tests: `test_rewards.py`, `test_locations.py`, `test_chatbot.py`).

### Result
Measured (not assumed) chatbot accuracy baseline of 69.8%, with the OOD recall trade-off explicitly documented rather than hidden.

### Lesson
The commit message itself states the lesson: reporting a metric that got worse (OOD recall) alongside the one that improved (accuracy) is preferable to only reporting the favorable number.

---

## V1 Phase 3 — OpenAI-powered Ask T2C assistant, grounded in verified business logic
**Commit:** `7039c3cf` (2026-09-13 12:01:09 -0400)

### Challenge / discovery
The existing local Naive Bayes chatbot could not hold natural conversation or handle phrasing variation well. The goal was a conversational layer that still never fabricates facts.

### Evidence
Commit message: new `t2c/assistant/` package — `client.py` (optional OpenAI client, returns `None` rather than erroring when unavailable), `schema.py` (validated structured intent, so "untrusted model JSON is never passed straight to business logic"), `tools.py` (tools that "call only `t2c.rewards` / `t2c.locations`, never OpenAI"), `assistant.py` (orchestrates extract → resolve → run tool → phrase, "with a numeric safety net that discards any phrasing introducing a number not in the verified fact").

### Diagnosis
A live evaluation run exposed two real bugs: `normalize_material` didn't match natural phrasing like "aluminum cans"/"nylon sachets" (only literal substrings of parenthesized canonical keys), and the reward tool asked for weight instead of stating the rate when material was known but weight wasn't given.

### Fix
Both bugs fixed; commit message notes both fixes "benefit the calculator too, not just the new assistant." Added a 60-case live evaluation set and `evaluate.py`. Added `test_assistant.py` (13 tests, OpenAI fully mocked) and updated two `/chat` tests to force `local_fallback` via monkeypatch for determinism regardless of whether a real key is configured.

### Validation
Commit message states live results: "98.3% tool selection, 93.2% argument extraction, 98.3% grounded-answer accuracy, 3.3% raw hallucination rate before the safety net." Local-fallback numbers (69.8% / 38.5% OOD recall) are stated as unchanged and "reported separately, not mixed in." Full suite: 41 passed, "no live network calls required."

### Result
A working OpenAI-grounded assistant with a verified, always-available local fallback, and bugs found via live evaluation (not guesswork) fixed before being counted as done.

### Lesson
Commit message frames the architecture's core principle directly: "OpenAI never computes a fact itself — it extracts intent/arguments and phrases pre-computed, verified answers." This principle is the basis for why hallucination is measured and bounded rather than assumed to be zero.

---

## V1 Phase 4 — Product integration and UI redesign
**Commit:** `fa393061` (2026-09-13 12:37:14 -0400)

### Challenge / discovery
Four separate capabilities (reward calculator, drop-off finder, assistant, T2CVision placeholder) existed without a coherent shared product experience; the existing UI had real defects.

### Evidence
Commit message: "Two real failures (button text on the base green, badge text)" in WCAG contrast were "caught and fixed before shipping" by checking the actual contrast formula rather than eyeballing. One nav template "had invalid HTML (a bare `<a>` outside its `<li>`)," another "referenced CSS classes that were never defined anywhere."

### Diagnosis
The old combined reward/location form had a location field "never actually used by the reward calculation." `project.py`'s `/contact` route called `flash()` but `contact.html` never rendered `get_flashed_messages()`, so confirmations were silently discarded. `about.html` contained a present-tense overclaim ("AI-powered... automated rewards system") not matched by actual functionality.

### Fix
New shared `static/css/styles.css` design-token system. New `templates/base.html` + `_icons.html` (hand-drawn inline SVGs) replacing drifted, hand-copied nav markup across four templates. Split reward calculator and location finder into dedicated pages plus two new JSON endpoints (`POST /api/reward`, `GET /api/locations`) that "call only `t2c.rewards` / `t2c.locations` — no reward math or location data duplicated in JavaScript." New dedicated Ask T2C page replacing the floating widget. Fixed the discarded flash-message bug. Rewrote the about-page overclaim to frame automation as future vision. Every location card/API response states plainly that no verified address/coordinates exist yet, with `test_app.py` asserting this directly.

### Validation
Commit message: "Full suite: 51 passed (41 from Phase 3 + 10 new)." States explicitly that no browser/screenshot tool was available, so "responsive/visual claims were verified structurally: HTML tag-balance checked programmatically for every page, and layouts reasoned through by hand for overflow risk at the required breakpoints (375–1440px)." One real overflow risk (hero rate-preview row) was found this way and fixed; the mobile-nav breakpoint was "recalculated and moved up to 1080px rather than left at a guessed value."

### Result
One coherent, audited UI with measured contrast fixes and a documented limitation (no real browser testing available in this environment, stated rather than hidden).

### Lesson
Commit message is explicit about the limits of its own verification method: structural/programmatic checks (tag-balance, contrast formula, breakpoint math) were used in place of actual browser rendering, and that substitution is disclosed rather than presented as equivalent to real visual testing.

---

## V1 stabilization — Mobile UX fixes and real photography integration
**Commit:** `1380fd4e869f27231137a3020c30e695f623b92f` (2026-10-05 13:53:19 -0500)

This is the commit now protected as the stable V1 baseline — confirmed current head of `main`, `backup/t2c-v1`, and tag `t2c-v1-stable`.

### Challenge / discovery
A mobile-first audit found five real issues: the hero rate panel was ordered above the headline on small screens, the primary CTA disappeared entirely from the mobile nav menu, three interactive controls (nav toggle, city tabs, suggestion chips) were under the 44px touch-target minimum, the chat panel used plain `vh` units (vulnerable to mobile keyboard/browser-chrome obstruction), and the reward result could land below the fold with no way to find it.

### Evidence
Commit message (full text, read directly via `git show --format=fuller`) lists each of the five issues verbatim as above, plus: "Adds real photography (cropped from licensed source images, originals preserved in `assets/`) to the homepage and About page... served as optimized, responsively-sized WebP files with explicit dimensions to avoid layout shift and lazy-loaded below the fold." `docs/IMAGE_ASSET_AUDIT.md` and `docs/MOBILE_UX_AUDIT.md` exist and document both passes "including what was and wasn't verified."

### Diagnosis
Per the commit message, each of the five mobile issues was found via a structured mobile-first audit at specific breakpoints, not by guesswork.

### Fix
Addressed all five listed mobile issues; added real photography as WebP with explicit dimensions and lazy loading; documented both audits; also excluded the local `ui-ux-pro-max` design-reference tooling from version control.

### Validation
The commit message does not restate a test-suite pass/fail count for this specific commit; `docs/MOBILE_UX_AUDIT.md` and `docs/IMAGE_ASSET_AUDIT.md` are cited as containing the verification detail, including explicit statements of "what was and wasn't verified" (i.e., the documents themselves disclose their own verification limits rather than claiming full device coverage).

### Result
This commit became the stabilized, protected V1 baseline immediately afterward (see V1 protection strategy, below).

### Lesson
Not independently stated in this commit beyond what's in the audit docs themselves; this document does not restate `IMAGE_ASSET_AUDIT.md`/`MOBILE_UX_AUDIT.md` content in detail since those documents already exist as the authoritative record of that work.

---

## V1 protection strategy
**Git objects:** tag `t2c-v1-stable`, branch `backup/t2c-v1`, branch `main` — all independently verified via `git rev-parse` to point to `1380fd4e869f27231137a3020c30e695f623b92f`.

### Challenge / discovery
Before starting V2's taxonomy redesign (a breaking change to the material/rate model), the known-good V1 state needed a durable, hard-to-lose reference point distinct from whatever `main` might become during V2 work.

### Evidence
`docs/T2C_V2_SPECIFICATION.md` records: "Records V1 protection state (commit, tag, backup branch) for reference throughout V2 development" (per its own commit message, `c7153215`). Direct `git` inspection this session confirms `main`, `backup/t2c-v1`, and `t2c-v1-stable` all currently still point to the same commit — the protection has not been altered since it was established.

### Diagnosis
N/A — preventative measure, not a bug fix.

### Fix
A tag (`t2c-v1-stable`) and a dedicated branch (`backup/t2c-v1`) were created pointing at the same commit as `main`, and `feature/t2c-v2` was branched from that commit rather than from a moving `main`.

### Validation
Verified this session via `git rev-parse main backup/t2c-v1 t2c-v1-stable` — all three resolve to `1380fd4e869f27231137a3020c30e695f623b92f`, matching the expected V1 commit given for this audit.

### Result
V2 development on `feature/t2c-v2` can proceed with a breaking data-model change while V1 remains independently recoverable via three separate references (tag, backup branch, and `main` itself, so far unmoved).

### Lesson
Redundant references (tag + branch + untouched `main`) to the same protected commit mean no single accidental branch deletion or reset can lose the V1 baseline.

---

## V2 Phase 0 — Specification
**Commit:** `c7153215` (2026-10-05 14:02:25 -0500)

### Challenge / discovery
V2's material taxonomy redesign (moving from a 3-bucket Plastic/Nylon/Aluminum model to a specific-material catalogue) needed to be specified before implementation, per the V1 protection requirement above.

### Evidence
Commit message: `docs/T2C_V2_SPECIFICATION.md` added, 790 lines, covering "material taxonomy, canonical rate data model, Reward Calculator V2, Materials experience, material-aware Drop-off Finder, Ask T2C catalogue integration, alias resolution, mobile navigation fix, testing/evaluation requirements, and implementation guardrails."

### Diagnosis
N/A — specification authoring, not a bug fix.

### Fix
N/A.

### Validation
Not applicable to a specification-only commit.

### Result
A written specification existed before any V2 code was changed, and records the V1 protection state for later reference.

### Lesson
Not independently stated beyond the document's own existence; see V2 catalogue build below for where the specification was actually implemented and tested against.

---

## V2 catalogue build — canonical material catalogue, Materials page, calculator/drop-off rework, mobile nav fix
**Commit:** `bc591a31` (2026-10-05 14:28:51 -0500)

### Challenge / discovery
The old reward model used three broad buckets with averaged min/max ranges per material; this didn't support material-specific rates, aliases, or preparation guidance, and had no single source of truth shared across the calculator, API, Ask T2C, and local chatbot.

### Evidence
Commit message: `t2c/materials.py` added as "the single source of truth" (3 categories, 7 materials, each with "aliases, familiar examples, a technical family field... preparation guidance, and a labeled reference/placeholder rate"). `t2c/alias_resolver.py` added as "deterministic (non-NLP) free-text-to-material resolution."

### Diagnosis
The alias resolver's design explicitly addresses a found risk before it could ship: "a bare generic word never silently resolves to one specific material by accident" — i.e. the ambiguity between e.g. "nylon" (3 possible materials) and an unambiguous category mention was identified and designed around directly in this commit (further detail on the specific bug this prevented is in `docs/T2C_V2_IMPLEMENTATION.md`, read directly: a bare word like "nylon" or "plastic" could otherwise resolve via substring-matching to one specific material purely because that word was a literal substring of one alias). A real mobile nav bug was also found: "the dropdown menu's top offset was a hardcoded pixel value that went stale once touch targets grew, clipping the menu on real devices."

### Fix
`t2c/rewards.py` rebuilt around canonical material id + weight. New `/materials` and `/materials/<slug>` routes/templates. `/rewards` reworked into dependent category → material flow; `/api/reward` now takes `material_id`. `/locations`/`/api/locations` gained an optional material filter labeling results `"selected_locations"` or `"not_yet_verified"` against the catalogue's own `supported_location_ids` — "never invents compatibility that isn't in the data." `t2c/assistant/tools.py` ported to the new catalogue so an unresolvable material gets an honest "not confident" response or a clarifying question instead of an invented rate. Mobile nav fix: offset now measured from the navbar's actual rendered height instead of hardcoded.

### Validation
Commit message states "all affected tests updated to the new contract; full suite passing," without a specific number in this commit (the number is given in the next commit, `1e62fbd6`).

### Result
A single canonical material data source feeding the reward engine, API, calculator, Materials UI, Ask T2C, and local chatbot fallback.

### Lesson
`docs/T2C_V2_IMPLEMENTATION.md` states the lesson for the alias bug directly: restricting the "query is substring of an alias" direction to multi-word queries only, and requiring single bare words to either have an explicit, deliberately-added unambiguous alias or fall through to a conservative, short category-hint list, avoids silently guessing on genuinely ambiguous single-word input.

---

## V2 evaluation and documentation — evaluation set, real bugs found by testing
**Commit:** `1e62fbd6` (2026-10-05 14:41:54 -0500)

### Challenge / discovery
The V2 catalogue and Ask T2C integration needed to be verified against real phrasing, not just unit tests against known-good inputs.

### Evidence
Commit message: a new 64-case live evaluation set "covering every example phrase from the V2 specification plus Nigerian English, spelling variation, combined questions, follow-ups, unsupported-feature, and out-of-domain questions" was run against the real assistant and "exposed three genuine issues."

### Diagnosis
Three real issues found by the live run, stated verbatim in the commit message:
1. "A missing alias ('bleach containers' wasn't recognized as HDPE even though it's literally in that material's own description)."
2. "An intent-routing ambiguity ('what materials do you take overall' was read as a general product question instead of a materials question)."
3. "Indirect reward phrasing ('I want to sell X') wasn't recognized as a reward question."

### Fix
Added the missing alias; clarified the intent-extraction prompt to classify general "what do you accept" questions as `material_info`; added explicit guidance that indirect reward phrasing counts the same as a literal "how much."

### Validation
Commit message states final results: "96.9% tool selection, 100% argument extraction, 96.9% grounded-answer accuracy, 1.6% raw hallucination rate." Local fallback chatbot "re-evaluated separately and unchanged (69.8% / 38.5% OOD recall), confirming no regression there." `docs/MATERIAL_CATALOGUE_V2.md` (per-material data provenance) and `docs/T2C_V2_IMPLEMENTATION.md` (architecture, API contract changes, full test/evaluation numbers) added this commit.

### Result
Three genuine, evaluation-discovered defects fixed before being counted as done; local fallback confirmed not regressed by the catalogue change.

### Lesson
`docs/T2C_V2_IMPLEMENTATION.md` states this explicitly: these were "real issues this live run caught and fixed (not eval-script artifacts)" — distinguishing genuine behavioral bugs from eval-harness noise, and re-running the full evaluation after each fix rather than assuming the fix worked.

---

## V2 polish — customer-facing rate terminology improvement
**Commit:** `6a91bfbe5a65a4aabdb566fab5d70f20b4bb17fe` (2026-10-05 16:18:07 -0500)

### Challenge / discovery
The Materials and material-detail pages displayed the internal data-management term `rate_status` value directly to users (e.g. the literal word "placeholder"), which is accurate internally but not customer-appropriate wording.

### Evidence
Diff (`git show 6a91bfbe`, read directly this session): `project.py` gained a `RATE_STATUS_LABELS` dict (`{"reference": "Reference Rate", "placeholder": "Estimated Rate"}`) and a Jinja `rate_status_label` template filter. `templates/material_detail.html` changed `{{ material.rate_status | title }} rate` to `{{ material.rate_status | rate_status_label }}`. `templates/materials.html` changed a raw `{{ material.rate_status }}` to the same filter.

### Diagnosis
Two templates independently rendered `rate_status` with different, ad hoc formatting (one with `| title` plus a hardcoded "rate" suffix, one with no formatting at all) — a wording inconsistency as well as an internal-terminology leak.

### Fix
Centralized the customer-facing wording in one place (`project.py`'s `RATE_STATUS_LABELS`) so both templates render identically and can't drift apart again, without touching `t2c/materials.py`'s canonical values.

### Validation
Verified directly this session: `t2c/materials.py` still stores only the internal values `RATE_REFERENCE`/`RATE_PLACEHOLDER` (grep confirms no `rate_status` value other than these two anywhere in the catalogue). The `.badge` CSS class applies `text-transform: uppercase` (confirmed in `static/css/styles.css`), so "Reference Rate"/"Estimated Rate" render visually as "REFERENCE RATE"/"ESTIMATED RATE," matching the expected customer-facing behavior. Full test suite re-run this session: **69 passed**, matching the expected count exactly, confirming no rate/disclaimer/logic change accompanied the wording fix.

### Result
Customers see "REFERENCE RATE" / "ESTIMATED RATE" instead of raw internal terminology; internal `rate_status` values and all rate/disclaimer logic are unchanged; no test regressed.

### Lesson
Not independently stated in the commit message itself; the fix pattern (one filter function instead of per-template formatting) is consistent with the same single-source-of-truth principle used throughout V2 (`t2c/materials.py` for data, `t2c/alias_resolver.py` for resolution, now `RATE_STATUS_LABELS` for presentation wording).

---

## V2 production-readiness preparation
**Status:** Not yet committed/deployed at the time this entry was written — tracked here as the audit findings and the changes made in response, not as a completed deployment. No deployment has occurred; `main`, `backup/t2c-v1`, and `t2c-v1-stable` were re-verified unchanged before and after this work.

### Challenge / discovery
A read-only deployment-readiness audit of `feature/t2c-v2` (performed in this session, prior to any change) found the branch architecturally deployable on Render/Railway (no database, no persistent-storage requirement, graceful optional-API-key handling) but not deploy-safe as-is, for five concrete reasons:
1. No production WSGI server — both entrypoints (`app.py`, `project.py`'s `main()`) ran Flask's development server with hardcoded `debug=True`.
2. `t2c/chatbot/chatbot.py` called `nltk.download('punkt')` unconditionally at module import time — a network dependency on every cold start/new worker.
3. `requirements.txt` was completely unpinned and bundled TensorFlow/NumPy/Matplotlib, which nothing in the running Flask app imports (confirmed by grep: no reference to `t2c.vision` in `project.py` or `app.py`).
4. No Python runtime version was declared anywhere, despite the app being verified locally only on Python 3.9.6.
5. No dedicated health-check route existed, though this was flagged as something to evaluate rather than assume necessary.

### Evidence
Audit performed via read-only `git`/`grep`/`find`/`pip show` inspection (see the deployment-readiness report delivered earlier this session). Confirmed via direct inspection of `t2c/assistant/client.py` that `OPENAI_API_KEY`/`OPENAI_MODEL` are the only two environment variables read anywhere in the app, both optional, with key absence returning `None` rather than raising.

### Diagnosis
**The import-time NLTK risk was more specific than first assessed.** Inspecting `t2c/chatbot/chatbot.py`'s actual usage (`nltk.word_tokenize()`, used only by `tokenize()`) and testing directly against the installed `nltk` version (3.9.2) showed that `word_tokenize()` resolves to the `tokenizers/punkt_tab/english` resource, not `tokenizers/punkt` — verified by simulating an empty NLTK data path and observing the exact `LookupError` naming `punkt_tab`. This means the original `nltk.download('punkt')` call was already fetching an incomplete/wrong-named resource for this nltk version; it only "worked" locally because `punkt_tab` happened to already be cached in this machine's `~/nltk_data` from an unrelated prior download. On a genuinely fresh deployment with no such cache, the original code's behavior would have depended on that mismatch resolving itself favorably, which is not guaranteed.

### Fix
1. **WSGI**: Added `gunicorn==23.0.0` to `requirements.txt`. No change to `app.py`/`project.py`'s local dev entrypoints — `python app.py` still works unchanged for local development; the production start command is `gunicorn project:app`, used only by the deploy platform.
2. **NLTK**: Removed `nltk.download('punkt')` entirely. Bundled only the exact resource proven necessary — `tokenizers/punkt_tab/english/` (four small text files, 244KB total) — at `t2c/chatbot/nltk_data/` inside the repo, and added that directory to `nltk.data.path` at import time. Verified by setting `nltk.data.path = []` (simulating a machine with zero cached NLTK data and no network) and confirming `tokenize()` and `get_bot_response()` both still work correctly from the bundled copy alone. `t2c/chatbot/chatbot.py`'s classification logic, intents, and confidence threshold were not touched. `t2c/chatbot/train_chatbot.py` (a dev-only training script, not imported by the running web app) still calls `nltk.download('punkt')` and was intentionally left unmodified — out of scope for a production-readiness change, since it never runs during deployment or application import.
3. **Dependencies**: Split `requirements.txt` into a pinned production set (Flask, nltk, scikit-learn, joblib, gunicorn, openai, python-dotenv — pinned to the exact versions verified installed and passing locally) and a new `requirements-vision.txt` (TensorFlow, NumPy, Matplotlib, same pinning approach) for T2CVision development only. `requirements-dev.txt` (`-r requirements.txt` + `pytest`) was left unchanged — confirmed by grep that no test file imports `t2c.vision`, so the dev/test dependency set doesn't need the vision packages either. No T2CVision code was removed.
4. **Runtime**: Added `runtime.txt` declaring `python-3.9.6`, matching the version already verified locally — not an upgrade.
5. **Health check**: Evaluated existing routes before adding anything. `GET /` renders a real template with no external calls (confirmed by reading `project.py`'s `home()` — it only reads the static material catalogue) and returns 200 reliably; verified directly via Flask's test client. No dedicated health-check endpoint was added; `/` is designated as the health-check route for the deploy platform.

### Validation
All performed in this session, against the changed code:
- `pytest -q`: **69 passed**, unchanged from before this work — same count as every prior session's run.
- Clean-process import check: `project.py` (and transitively `t2c/chatbot/chatbot.py`) imports successfully with no prior `sys.modules` state.
- NLTK fresh-deployment simulation: `nltk.data.path = []`, then `tokenize()`/`get_bot_response()` both verified working from the bundled resource alone, with zero network access.
- `OPENAI_API_KEY` absence: verified by patching `t2c.assistant.client.get_api_key` to return `None` directly (not by touching the real local `.env` file) — `get_client()` returns `None`, and `POST /chat` returns HTTP 200 with `"mode": "local_fallback"`, not an error.
- Gunicorn boot test: `gunicorn project:app --bind 127.0.0.1:8099` started cleanly (one `sync` worker booted with no errors in the log), and `GET /`, `/materials`, `/about` all returned 200 against the running gunicorn process; the process was then stopped and confirmed not running.
- `requirements.txt` inspected directly to confirm no TensorFlow/NumPy/Matplotlib reference remains in the production dependency file.

### Result
`feature/t2c-v2` now has a declared production WSGI server and start command, a deterministic chatbot import with no network dependency at any stage (build or runtime), a pinned and vision-free production dependency set (with vision deps preserved separately for developers who need them), a declared Python runtime version matching what's actually been tested, and a designated health-check route — without any change to product behavior, rates, taxonomy, aliases, acceptance logic, APIs, Ask T2C behavior, or visual design. **Deployment itself has not occurred** — this entry records readiness work, not a completed deploy.

### Lesson
Inspecting the *exact* resource name a library resolves at runtime (via a fresh-environment simulation), rather than trusting that an existing `nltk.download('punkt')` call was correct because it happened to work on one already-provisioned machine, surfaced a latent mismatch between the downloaded resource name and the one actually used by the installed library version — the kind of gap that only shows up on a genuinely fresh deployment, exactly the scenario this production-readiness pass was meant to de-risk.

---

## Items the specification/prompt named that this history did not independently verify

- **"V1 stabilization" validation detail**: the exact device/breakpoint test matrix for the 1380fd4e mobile fixes lives in `docs/MOBILE_UX_AUDIT.md` and `docs/IMAGE_ASSET_AUDIT.md` and was not re-transcribed here in full — those documents remain the authoritative source, not this summary.
- **Pre-2026-09-13 diagnosis detail**: the root cause of the "broken about and contact routes" fixed twice in the May–June 2025 prototyping period (on two diverging branches) is not recoverable from the commit messages available; only that it was fixed is evidenced.
- **Exact "lesson" framing** for several milestones above is this document's own synthesis from stated evidence (e.g. "redundant references mean no single accidental deletion can lose the baseline"), not a verbatim quote from a commit — flagged inline at each such entry rather than presented as a direct quotation.
