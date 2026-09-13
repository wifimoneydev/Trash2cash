# Trash2Cash Current State

*Audit date: 2026-09-13. Based on direct code inspection, static analysis, and live execution (Flask test client, pytest, chatbot inference) — not on README claims.*

*Updated 2026-09-13 after Phase 1 (Repository Cleanup and Canonicalization). The original audit below is preserved as the pre-cleanup baseline; see the Phase 1 section immediately below for current state.*

---

## Phase 1: Repository Cleanup and Canonicalization — Completed

### Canonical copy selected, and why

Four overlapping copies of the app existed (root, `trash2cash/`, `trash2cash/trash2cash/`, `trash2cash/t2cchatbot/spider/`). They were compared file-by-file (`diff`, mtimes) rather than assumed:

- **App shell** (`app.py`/`project.py`, templates, `static/css`): the **root copy** won on every file compared — it was the newest by mtime and the most feature-complete (POST-capable contact route, updated `home()` naming, nicer templates with animations). The three nested copies were mutually near-identical, older, and in one case (`spider/project.py`) missing the chatbot import entirely.
- **`t2cchatbot`**: only existed in one place, `trash2cash/t2cchatbot/` — promoted to canonical by necessity, after stripping its committed `venv/` and its own internal `spider/` duplicate.
- **`t2cvision`**: root copy won — identical core code to the nested copy, plus non-empty scaffold directories the nested copy lacked.
- **README**: the root `trash2cash/README.md` and the CS50-submission-style `trash2cash/trash2cash/README.md` (identical to the `spider/` copy) contained genuinely different content, not just staleness. The CS50 submission version (with video demo link and fuller narrative) was kept as the basis for the new root `README.md`, corrected in the sections that overstated current functionality (e.g. "real-time market prices," "nearest drop-off centers are recommended").

### What was removed

- The entire nested `trash2cash/` directory tree (three levels of duplicate app copies), including a git-tracked **4,580-file Python virtualenv** (`trash2cash/t2cchatbot/venv/`) and a duplicate `spider/` copy of the whole app nested inside the chatbot directory.
- The empty, now-superseded `t2cvision/` shell at root (code moved to `t2c/vision/`) and old duplicate `.DS_Store` / dead `gitignore` (no leading dot) files.
- The dead root-level `__init__.py` (empty, unused — nothing imported the repo root as a package).
- The empty root-level `t2cchatbot/` stub and the local, gitignored `venv/` and `t2cvision/venv/` directories were **left in place on disk** (untouched, per instruction not to delete a developer's local environment that sits outside tracked files) — they are not committed and contain no unique code. They're safe to delete manually; a fresh venv can be built from the new root `requirements.txt`.
- **Known follow-up, not done in this phase**: the removed venv's blobs still exist in git history and in Git LFS storage (this repo has LFS configured — even test-fixture `.pkl` files from inside the old venv's `site-packages` had been pushed to LFS). Shrinking history/LFS storage requires a history rewrite (e.g. `git filter-repo` + `git lfs prune`), which changes commit hashes and needs separate, explicit sign-off before touching the shared `origin` remote — not attempted here.

### Modules unified

- New `t2c/` package: `t2c/chatbot/` (moved from `trash2cash/t2cchatbot/`, minus venv/spider/the dead empty `utils.py`), `t2c/vision/` (moved from root `t2cvision/`), plus two new shared modules:
  - **`t2c/rewards.py`** — `RATES`, `get_rate_range()`, `calculate_reward()`. Values are unchanged from the original `project.py` (₦80–100 plastic, ₦70–200 nylon, ₦200–500 aluminum) — nothing invented.
  - **`t2c/locations.py`** — `LOCATIONS`, `get_locations()`. Same static LGA lists as before, explicitly documented as static, not live.
- `project.py` now imports both from `t2c/`, and still re-exports `calculate_reward`/`get_rate_range`/`get_locations` at module level so `test_project.py` needed no changes.
- `app.py` is now the single canonical entrypoint (`from project import app`; `python app.py` starts it). It previously had its own broken, parallel set of routes and a dead import (`t2cchatbot.utils.tokenize`, from a file that was empty) — that duplicate implementation is gone.
- One `requirements.txt` (Flask, nltk, scikit-learn, joblib, tensorflow, numpy, matplotlib — every import actually used anywhere in the canonical tree) and one `requirements-dev.txt` (adds pytest).

### Chatbot payout contradiction — fixed

`t2c/chatbot/chatbot.py`'s `get_bot_response()` now special-cases the `payout_rates` intent to build its answer from `t2c.rewards.RATES` at call time, instead of returning a hardcoded USD string that disagreed with the real Naira rates. Verified live: asking the chatbot "What are the rates?" now returns the exact same ₦80–100/₦70–200/₦200–500 figures the `/process` calculator uses. A regression test (`test_app.py::test_chatbot_payout_rates_match_reward_module`) asserts this so it can't silently drift apart again. The classifier itself (NLTK + scikit-learn Naive Bayes, 7 intents, ~20 training phrases) is unchanged — no retraining, no LLM.

### Contact form — fixed

`project.py`'s `/contact` route previously called `flash()`/`redirect()` without importing them and without a `SECRET_KEY`, so any POST raised an unhandled exception. Both imports and a (non-production, clearly-a-placeholder) `app.secret_key` were added. The form remains exactly what it was: it prints the submission to the console and redirects back — no email sending, no storage — and that's now documented rather than silently broken.

### T2CVision rescaling bug — fixed

`identify.py` previously divided pixel values by 255 a second time on top of the `Rescaling(1./255)` layer already inside the trained model, which would have corrupted any real inference. That manual rescale is removed. Separately — since **no trained model file exists anywhere in this repo** — `identify.py` now fails with a clear, explicit error naming the missing file and pointing at `trainvision.py`, instead of a raw stack trace or (worse) a silent wrong answer. No model was fabricated or trained during this phase.

### Duplicate chat widget — fixed

`templates/index.html` rendered two independent chat UIs: a static, non-functional one (`#chat-toggle`/`#chatbox`, wired only to show/hide, never called `/chat`) and a second one injected at runtime by `static/chatbot/chatbot.js` (which does call `/chat`). The dead static markup and its inline script were removed; the one working widget remains.

### Verified working from repo root (Final Verification)

```
pytest                    → 9 passed (3 original business-logic tests + 6 new route/regression tests)
python app.py             → starts cleanly, serves real HTTP 200s on / and /about (verified via test client and a live server on an alternate port — port 5000 is occupied by macOS AirPlay Receiver locally, unrelated to this app)
python -c "import project, app"   → clean import from repo root, no sys.path hacks needed
```

Live-verified via Flask test client: home page renders, `/process` computes ₦450.0 for 5kg plastic (unchanged, correct math), `/chat` responds for both a generic intent and `payout_rates` (now consistent with `t2c.rewards`), `/contact` GET renders and POST redirects (302) instead of crashing, and both static assets (`css/styles.css`, `chatbot/chatbot.js`) return 200.

### Current canonical structure

```
app.py                  # entrypoint — python app.py
project.py              # Flask routes + app object
templates/               # 4 HTML templates
static/                  # css/, chatbot/chatbot.js
t2c/
├── __init__.py
├── rewards.py           # RATES, get_rate_range, calculate_reward
├── locations.py         # LOCATIONS, get_locations
├── chatbot/
│   ├── chatbot.py        # get_bot_response (Naive Bayes + dynamic payout_rates)
│   ├── train_chatbot.py
│   ├── data/intents.json, data/chat_model.pkl
│   └── README.md
└── vision/
    ├── identify.py       # CLI inference (fails clearly — no model present)
    ├── trainvision.py    # MobileNetV2 transfer-learning pipeline
    ├── data/dataset-resized/   # stock TrashNet, 2,527 images
    ├── pet1.jpeg, pet2.jpeg
    └── README.md
test_project.py          # reward/location business-logic tests
test_app.py               # route + chatbot-consistency tests (new)
requirements.txt / requirements-dev.txt
README.md
T2C_PROJECT_STATUS.md
```

### Still broken / not addressed in Phase 1 (by design — out of scope)

- No database, accounts, or persisted reward/exchange history.
- No live rates or geodata — both `t2c/rewards.py` and `t2c/locations.py` are honestly-labeled static tables, not APIs.
- T2CVision has no trained model artifact — training was not run (explicitly out of scope for this phase).
- The chatbot's other six intents are still static canned strings (only `payout_rates` was wired to shared data — that was the one causing an actual contradiction; the rest don't reference numbers that could drift).
- `debug=True` remains the default in `app.py`/`project.py`'s `main()` — fine for local dev, still not production-safe (deployment is a later phase).
- Git history and LFS storage still contain the old venv blobs (see "What was removed" above) until a separate, explicitly-approved history rewrite.

### Recommended next phase

**Phase 2 candidates, in order:**
1. Rewards/drop-off data layer: decide if `t2c/rewards.py`/`t2c/locations.py` should gain a config file or admin-editable source, still without inventing "live" data that doesn't exist.
2. Chatbot: consider a confidence threshold + fallback response for out-of-distribution input (observed in the original audit: gibberish input gets confidently misclassified as a real intent).
3. T2CVision: actually run `trainvision.py` to completion, save a real model, and record honest metrics — only after that, wire an `/identify` endpoint into `project.py`.
4. Persistence/accounts — deliberately last, so it's built on the now-stable, de-duplicated codebase.

---

## Original Audit (Pre-Cleanup Baseline)

*The sections below describe the repository as it existed before Phase 1. Kept for historical reference — several findings here (the nested duplication, committed venv, chatbot/reward contradiction, broken contact form, vision rescaling bug, duplicate chat widget) have since been fixed, as documented above.*

## Product Vision

Trash2Cash (T2C) is a recycling incentive platform for Nigeria (initially Lagos and Abuja). The intended unified product lets a user: identify recyclable waste, estimate its cash value, find a drop-off location, ask questions via an assistant, and (eventually) track activity/rewards over time. Three modules exist today, built at different times, with no shared codebase or data layer: the main Flask app, T2CChatbot, and T2CVision.

## Critical structural finding: the repository is nested inside itself

Before module-level findings: the working tree contains **three to four full copies of the main app**, nested inside each other:

```
trash2cash/                              (repo root — CANONICAL, most current code)
├── app.py, project.py, templates/, static/, t2cvision/
└── trash2cash/                          (duplicate copy #1 — stale, has t2cchatbot/)
    ├── app.py, project.py, templates/, static/, t2cvision/, t2cchatbot/
    │   └── venv/                        (4,580 files — a committed Python virtualenv)
    │   └── spider/                      (duplicate copy #2 of the main app)
    └── trash2cash/                      (duplicate copy #3, one level deeper)
```

Verified with `diff`: `app.py` is byte-identical across all copies; `project.py` and `templates/*.html` differ between copies (the root copy is a newer, more feature-complete but *more broken* version — see below). This is almost certainly the result of repeatedly dragging/copying the project folder into itself and committing each time. It roughly triples the size of the tracked repo and makes it genuinely ambiguous which copy is "the app."

**Only `trash2cash/t2cchatbot/` exists** (not duplicated at root), which matters a lot: the root-level `app.py` and `project.py` both `import` from `t2cchatbot`, but there is no `t2cchatbot` package next to them — so **the root copy cannot run at all**, while the nested `trash2cash/` copy can (because `t2cchatbot` is its sibling).

## Existing Modules

### Main Trash2Cash

**Architecture**
- Python Flask, server-rendered with Jinja2 templates (`templates/*.html`), no frontend framework, no build step. Plain CSS (`static/css/styles.css`, 278 lines) and vanilla JS.
- Two competing entry points exist at the root: `app.py` (thin chatbot-only API) and `project.py` (the real CS50-style app with `home`, `process`, `about`, `contact`, `chat` routes, plus `def main()`). `project.py` is the one referenced by `test_project.py` and is the de-facto main app.
- No `requirements.txt` for the main app anywhere — dependencies (Flask, and transitively nltk/scikit-learn/joblib for the chatbot import) are undocumented.

**Working features (verified live)**
- Reward calculator: `calculate_reward()` in `project.py` correctly computes `(min_rate+max_rate)/2 * weight` for Plastic/Nylon/Aluminum. Verified via `pytest test_project.py` (3/3 pass) and via a live POST to `/process` (5kg plastic → ₦450.0, correct).
- `/chat` route: correctly proxies to the chatbot and returns a real response (verified live).
- `/about` and `/` (home) render successfully.

**Partial / dead features**
- `LOCATIONS` dict (Lagos → Ikeja/Surulere/Yaba/Lekki; Abuja → Garki/Wuse/Maitama/Kubwa) and `get_locations()` exist and are unit-tested, but **are never rendered anywhere**. The home route passes `locations=LOCATIONS` and `rates=RATES` into `index.html`, but that template never references either variable — it only has hardcoded prose mentioning rate ranges. The UI only ever offers city-level choice (Lagos/Abuja), not LGA-level, despite the data existing for it.
- Two independent chat-widget UIs are shipped simultaneously: a static one hardcoded into `index.html`/`contact.html` (`#chat-toggle` / `#chatbox`, wired only to a `toggleChat()` show/hide — it never calls `/chat`), and a second one injected at runtime by `static/chatbot/chatbot.js` (`#chatbot-icon` / `#chat-container`, which *does* call `/chat`). A visitor sees two chat bubbles; only one is functional.
- Contact form: the **root** `project.py`'s `/contact` route handles POST, calls `flash()` and `redirect()`, but **never imports them** (`from flask import Flask, render_template, request, jsonify` — no `flash`/`redirect`) and the app has no `SECRET_KEY` (required for `flash`/sessions). This route would raise `NameError` on any submission. The **nested** `trash2cash/project.py` copy has a simpler GET-only `/contact` (verified live — POST correctly 405s there instead of crashing, but the form has nowhere to submit to). No contact submission is ever stored anywhere; the older copy just `print()`s it to the console.

**Missing features**
- No backend database of any kind (no SQLite/Postgres/ORM anywhere in the repo).
- No user accounts, auth, sessions, or reward/exchange history/tracking.
- No real drop-off geodata (no addresses, no coordinates, no map, no geolocation API) — only two hardcoded city names and, unused, eight LGA name strings.
- No live/API-driven pricing — `RATES` is a hardcoded Python dict.

**Problems**
- Root-level `app.py`/`project.py` cannot import (`ModuleNotFoundError: No module named 't2cchatbot'`) — confirmed by direct execution. The project's own test suite (`test_project.py`) **fails to even collect** when run from the repo root for the same reason, and only passes from inside the nested `trash2cash/` copy.
- `debug=True` hardcoded in every Flask entrypoint (`app.py`, `project.py`, and all duplicates) — fine for local dev, a real risk (remote code execution via the Werkzeug debugger) if ever deployed as-is.
- `calculate_reward` matches material via case-insensitive substring (`material_lower in key.lower()`), not an exact/enum match — currently safe because the three form values happen to be prefixes of their keys, but fragile (a new material whose value isn't a clean substring of exactly one key would silently mismatch or fall through to a reward of 0 with no error surfaced to the user).
- Dead file: a bare `gitignore` (no leading dot) sits next to the real `.gitignore` at both the root and the nested copy — it does nothing; git only reads `.gitignore`.
- `.DS_Store` files and empty `t2cvision/app`, `t2cvision/models`, `t2cvision/scripts`, `t2cvision/notebooks` directories are checked into the working tree as unused scaffolding.

### T2CChatbot

**Architecture**
- A classic **bag-of-words intent classifier**, not a language model: `CountVectorizer` → `MultinomialNB` (scikit-learn), tokenized/stemmed with `nltk.word_tokenize` + `PorterStemmer`. Trained by `train_chatbot.py`, serialized to `data/chat_model.pkl` via `joblib`, and loaded at import time by `chatbot.py`.
- `utils.py` is **completely empty (0 bytes)**. Root `app.py` imports `tokenize`/`stem_words` from it (`from t2cchatbot.utils import tokenize, stem_words`) — those functions are actually defined inside `chatbot.py`, not `utils.py`. This import would fail even if `t2cchatbot` were reachable from root.

**Working (verified live)**
- `get_bot_response()` in `chatbot.py` loads correctly, classifies, and returns a plausible canned reply for in-distribution inputs (tested "Hello" → greeting response; "How much do you pay for plastic?" → payout_rates response).
- Training script (`train_chatbot.py`) is a working, minimal, reproducible pipeline over `data/intents.json`.

**Partial / not implemented**
- No OpenAI/GPT integration anywhere — confirmed by repo-wide grep for `openai`/`gpt`/`api_key`; there is no `.env` file and no API key handling. The bot is 100% local, static-response.
- No memory/session/context — `get_bot_response(user_input)` takes a single stateless string; nothing persists between calls.
- No integration with the real reward calculator or location data. The chatbot's `payout_rates` intent returns a **hardcoded, different, and wrong** answer ("we pay $0.30/kg for plastic and $0.70/kg for aluminum" — in USD, not Naira) that does not match `project.py`'s actual `RATES` (₦80–100/kg plastic, ₦200–500/kg aluminum). A user asking the bot vs. using the calculator gets two different, contradictory numbers.
- `dropoff` intent points users to `trash2cash.org/locations`, a URL that doesn't correspond to anything in this codebase.

**Exact intents supported (7 total, from `data/intents.json`)**: `greeting`, `how_it_works`, `payout_rates`, `pickup`, `dropoff`, `goodbye`, `plastic_types`. Each has ~3–5 example patterns and one fixed response string.

**Reliability limitation (verified live)**: with only ~20 total training examples across 7 classes and no out-of-distribution/confidence threshold, Naive Bayes always picks *some* class confidently — a nonsense input ("asdkjfh random gibberish") was classified as `greeting` and answered as if it were a real greeting, with no fallback/"I don't understand" behavior actually triggering in practice.

**Dead/duplicate code**: `utils.py` is dead weight (empty, referenced only by the broken root `app.py`). `trash2cash/t2cchatbot/spider/` is a full duplicate copy of the main app nested three levels deep (see structural finding above) — not chatbot-specific but lives under this module's directory.

**README vs. reality**: the `t2cchatbot/README.md` is largely fiction relative to the code. It describes spaCy/transformers, GPT-3.5/4 fine-tuned prompts, a "Smart Memory" feature, WhatsApp/voice/multilingual plans, files that don't exist (`responses.py`, `train_model.py`, `data/corpus.json`, `.env`), and fabricated sample conversations (specific Ikeja outlet address, PP/HDPE plastic acceptance) that have no basis in `intents.json`. None of this is implemented.

### T2CVision

**Architecture**
- Transfer learning via **MobileNetV2** (ImageNet weights, frozen base + a later fine-tuning phase unfreezing the last ~100 layers), not a "basic CNN" as the README states. Built with `tf.keras.Sequential`: augmentation (`RandomFlip`, `RandomRotation`) → `Rescaling(1/255)` → MobileNetV2 → `GlobalAveragePooling2D` → `Dropout(0.3)` → `Dense(128)` → `Dense(num_classes, softmax)`.

**Dataset**
- The **unmodified, stock TrashNet dataset** (garythung/trashnet), 2,527 images across the original 6 classes: `cardboard` (403), `glass` (501), `metal` (410), `paper` (594), `plastic` (482), `trash` (137). There is **no Nigeria-specific data** (no pure-water-sachet/nylon class) despite the README's "next steps" describing exactly that as in progress — it hasn't started. `t2cvision/trashnet/` is an empty placeholder directory.
- 80/20 train/validation split via `image_dataset_from_directory(..., validation_split=0.2)`, no held-out test set. No class-imbalance handling despite `trash` having ~3.5x fewer images than `paper`.

**Model/dataset status**
- **No trained model artifact exists anywhere in the repo or on disk** (`t2cvision/models/` is empty; `.gitignore` explicitly excludes `*.h5`/`*.pkl`/`checkpoints/`/`models/`/`runs/`). Training has apparently never been run to completion and saved, or the result was never kept.
- `t2cvision/requirements.txt` is **empty (0 bytes)** — dependencies (tensorflow, matplotlib, joblib) are undocumented.

**Known accuracy problems**
- Cannot be verified or reproduced — there is no saved model, no logged metrics, no confusion matrix, nothing to load. Any accuracy claim in the README is unverifiable from the current repo state.
- A concrete bug that would corrupt inference if a model *did* exist: `identify.py` manually normalizes pixels (`img_array / 255.0`) before calling `model.predict()`, but the saved model already contains a `layers.Rescaling(1./255)` layer internally (from `trainvision.py`). This double-rescales every inference image (effectively `/65025`), which would badly degrade or randomize predictions.

**Missing features / integration**
- No API or UI of any kind — `identify.py` is a bare CLI script (`python identify.py <path>`), and it can't currently run at all (would fail immediately trying to load a nonexistent `model/t2c_classifier_finetuned.h5`).
- **Zero integration with the main Trash2Cash app.** There is no route, no import, no call anywhere in `app.py`/`project.py` that touches `t2cvision`. It is a fully standalone, disconnected module today.
- `t2cvision/app/`, `t2cvision/scripts/`, `t2cvision/notebooks/` are empty placeholder directories — scaffolding for work that hasn't started.
- Duplicate copy under `trash2cash/t2cvision/` is byte-identical to the root copy for `identify.py`/`trainvision.py` (verified via `diff`) but lacks the `app/`, `models/`, `scripts/`, `notebooks/` scaffolding — confirming the root copy is the newer/current one.

**Deployment blockers**: no trained model, no pinned dependencies, hardcoded relative paths (`"data/dataset-resized"`, `"model/..."`) that only work if the script is run from inside `t2cvision/` with that exact layout present.

## README Accuracy Review

| Claim | Where | Status |
|---|---|---|
| Static HTML/CSS/JS site, no backend ("script.js" reward calc, "no backend integration yet") | Main `trash2cash/README.md` | **Outdated.** Describes an earlier pre-Flask prototype. The actual app is server-rendered Flask with Python-side reward calculation; `script.js`/pure client-side calc no longer exists. |
| LGA-level location dropdown (Ikeja, Lekki, Wuse, etc.) in the main form | Main README | **Outdated/inaccurate.** Real UI only offers city-level (Lagos/Abuja); LGA data exists in code (`LOCATIONS`) but is unused in any template. |
| "AI-powered drop-off containers", automated rewards system | Main README (`about.html` too) | **Planned only.** No hardware/IoT/automation exists; pure marketing language. |
| spaCy/transformers + GPT-3.5/4 via OpenAI API | `t2cchatbot/README.md` | **Inaccurate / never implemented.** Confirmed zero references to OpenAI anywhere in code. Actual implementation is CountVectorizer + MultinomialNB. |
| "Smart Memory" (remembers past conversation/location) | `t2cchatbot/README.md` | **Planned only, not implemented.** No session or state handling in `chatbot.py`. |
| Chatbot "calculates estimated cash reward using real-time rates" / connects to "T2C Backend API" | `t2cchatbot/README.md` | **Inaccurate.** Response is a static hardcoded string, in the wrong currency, disconnected from and inconsistent with the real `RATES` in `project.py`. |
| Files `responses.py`, `train_model.py`, `data/corpus.json`, `.env`, `templates/` | `t2cchatbot/README.md` | **Do not exist.** README documents a different file layout than what's in the repo. |
| Sample conversations (specific outlet address, PP/HDPE claims) | `t2cchatbot/README.md` | **Fabricated.** No such data exists in `intents.json` or anywhere else. |
| "Basic CNN model", accuracy issues distinguishing "nylon vs. plastic" | `t2cvision/README.md` | **Outdated/inaccurate.** Current architecture is MobileNetV2 transfer learning, not a basic CNN; there is no "nylon" class in the dataset used (stock TrashNet has no such category), so this described failure mode doesn't map onto the current code. |
| "Exploring building a custom dataset" for local Nigerian trash types | `t2cvision/README.md` | **Planned only.** Dataset is still the unmodified public TrashNet set; no custom collection has started. |

## Duplication / Integration Problems

- **The nested self-copies are the single biggest problem** (see structural finding above): three-plus full copies of the main app tree, a committed 4,580-file virtualenv, and divergent versions of `project.py`/templates across copies with no clear source of truth. This alone should block any further feature work until resolved.
- **Reward/rate data has two independent sources of truth that already disagree**: `project.py`'s `RATES` dict (₦, per-kg ranges) vs. the chatbot's hardcoded `payout_rates` response ($, flat numbers). Same category of risk exists for location data (`LOCATIONS` in `project.py`, static text in the chatbot's `dropoff` intent, and separately hardcoded `<option>` lists in `process.html`) — three places describe locations, none reference each other.
- **T2CVision and T2CChatbot are both fully disconnected islands** — no code path in the main app calls into either. Nothing routes an uploaded image to T2CVision; nothing routes a reward/location question through a shared data layer instead of a hand-typed string.
- Two chat widgets rendered on the same page (see Main app findings) is itself a duplication bug, not just an architecture concern.

## Security / Production Concerns

- `debug=True` in every Flask entrypoint — Werkzeug interactive debugger would be reachable if this were ever exposed as-is.
- No `SECRET_KEY` configured, yet one code path (`flash()` in root `project.py`) depends on session support that isn't set up.
- A full virtualenv (`trash2cash/t2cchatbot/venv/`, 4,580 files, including activation scripts with absolute local paths) is committed to git history — not a secret leak here specifically, but bad hygiene and a real risk pattern (venvs can carry cached credentials/tokens on other machines).
- No input validation beyond HTML `required`/`type=number` attributes; `calculate_reward` receives `weight` as a raw string and does `float(weight)` with no try/except — a malformed value would raise an unhandled 500 rather than a user-facing error.
- No secrets, API keys, or `.env` files found in the tracked tree (this is a genuine positive — nothing to rotate).

## Proposed Unified Architecture

*(For discussion only — not implemented, per audit scope.)*

1. **One canonical repository root.** Resolve the nested-copy problem first: pick the root-level `trash2cash/` tree as canonical (it has the newer `project.py`/templates), move `t2cchatbot` up to sit beside it as a real sibling package, and delete the nested duplicates (`trash2cash/trash2cash/`, `trash2cash/t2cchatbot/spider/`) and the committed `venv/` from git history.
2. **A single Flask app** (built on today's `project.py`) as the front door, with `t2cvision` and `t2cchatbot` demoted to internal Python packages/modules it imports — not separate deployables, at least initially. This matches the chatbot README's own "T2C Backend API" diagram, just without the fictional parts.
3. **One data module for rates and locations** (a small `t2c_data.py` or similar) that `project.py`, the chatbot's intent responses, and any future vision output all import from — eliminating the ₦/$ rate mismatch and the three independent copies of location data.
4. **T2CVision integrates as a function/route, not a CLI script**: an `/identify` endpoint that accepts an uploaded image, runs inference, and returns a predicted material — which the reward form could pre-fill. This requires an actual trained, saved model first (currently there is none).
5. **T2CChatbot integrates by calling into the same reward/location module** instead of returning fixed strings, so "how much for 2kg of plastic?" produces a real, consistent number instead of a hardcoded guess.

## Recommended Development Roadmap

**P0 — Repository/environment reliability**
- Deduplicate the nested copies; commit to one tree as canonical.
- `git rm -r --cached` the committed `venv/`; verify `.gitignore` actually excludes it and the root `t2cvision/data/dataset-resized` (currently only the nested copy's dataset path is ignored, which is presumably why the root copy's 2,527 dataset images are still tracked despite a commit titled "Remove large dataset from Git").
- Add a real root-level `requirements.txt` covering Flask + chatbot deps; fill in `t2cvision/requirements.txt` (currently empty).
- Fix the two concrete import breaks: root `app.py`'s dead `t2cchatbot.utils` import, and root `project.py`'s missing `flash`/`redirect` import (plus add a `SECRET_KEY` if `flash` is kept).
- Get `test_project.py` runnable and green from the repository root.

**P1 — Unified application architecture**
- Decide the single canonical Flask entrypoint (retire whichever of `app.py`/`project.py` isn't kept) and fold `t2cchatbot` in as a proper sibling package.

**P2 — Rewards/drop-off data layer**
- Consolidate `RATES`/`LOCATIONS` into one module; make the chatbot and any future vision output read from it instead of hardcoded strings, so numbers can never disagree again.
- Either wire the existing LGA-level `LOCATIONS` data into the UI or remove the dead/unused code path.

**P3 — Chatbot integration**
- Connect `payout_rates`/`dropoff` intents to the real data layer (P2) instead of static text; remove the dead `utils.py`; decide whether NLTK/Naive Bayes is sufficient long-term or needs a confidence threshold + fallback response for out-of-distribution input (observed failure mode today).

**P4 — T2CVision improvement/integration**
- Fix the double-rescaling bug in `identify.py` before ever training again.
- Actually run and save a trained model (none currently exists) and record real metrics/confusion matrix before making any accuracy claims.
- Only after a model exists: expose it via an internal function/route the main app can call, per the proposed architecture.
- Custom Nigeria-specific dataset collection is a larger, separate effort — sequence it after the pipeline itself is proven to work end-to-end on TrashNet.

**P5 — Persistence/accounts**
- No database exists today. Needed for any reward history, user accounts, or tracking — deliberately sequenced after the above so it's built against a stable, de-duplicated codebase rather than three copies of it.

**P6 — Deployment**
- Turn off `debug=True`, pin dependencies, and only then consider hosting — none of the current entrypoints are deployment-ready as-is.

---

## Summary

1. **Main Trash2Cash app today**: a Flask app with a working, tested reward calculator (₦, 3 materials, correct math) and a working chatbot proxy route — but the root copy of the app cannot actually start (`ModuleNotFoundError`), and only a nested nearly-duplicate copy runs. Location logic is more granular in code than in the UI, and the contact form is broken (root) or a no-op print statement (nested copy). No database, no accounts, no real APIs.
2. **T2CChatbot today**: a small Naive Bayes text classifier over 7 hardcoded intents (~20 example phrases total). No OpenAI, no memory, no real integration with reward/location logic — it gives users a different, wrong payout rate than the actual calculator.
3. **T2CVision today**: a reasonable MobileNetV2 transfer-learning training script over the stock, unmodified TrashNet dataset — but there is no trained model saved anywhere, no way to verify any accuracy claim, a real double-normalization bug waiting in the inference script, and zero integration with the rest of the product.
4. **Most README claims about OpenAI/GPT, smart memory, LGA-level dynamic locations, AI-powered drop-off hardware, and custom Nigerian datasets are aspirational and unimplemented** — several read as a spec for a future version, not documentation of the current one.
5. **What currently works** (verified live): reward calculation math, the `/chat` route + chatbot inference for in-distribution questions, the 3-test `pytest` suite, and page rendering for home/about/process — all only from the correct (nested) copy of the repo.
6. **What's broken**: the root-level app entirely (import errors), the root-level contact form (missing imports), vision inference (no model file exists, plus a rescaling bug), and the second, non-functional chat widget baked into the HTML.
7. **Unification recommendation**: collapse the duplicated repo copies into one tree, keep one Flask entrypoint, extract rates/locations into a single shared data module, and integrate chatbot and vision as internal packages/routes of that one app rather than as separate projects — in that order.
8. **Top 5 priorities**: (1) deduplicate the repo and purge the committed venv, (2) fix the broken imports/entrypoints so the canonical app runs from a clean checkout, (3) unify rates/location data into one source of truth, (4) get a real trained, saved T2CVision model with honest metrics before claiming any accuracy, (5) only then integrate chatbot and vision into the single app.

*No rewrites, merges, retraining, new dependencies, or infrastructure were introduced during this audit. Only reads, `diff`, `pytest`, and Flask test-client requests were used to verify behavior; one lightweight `pip install nltk` was performed to exercise the existing chatbot code as-is.*
