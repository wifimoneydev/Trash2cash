# Trash2Cash V2 Specification

This document is the complete, authoritative specification for Trash2Cash V2. It is written so that a developer joining the project cold — with no other context — can continue the work from this document alone.

**This is a controlled product evolution of the existing application. It is NOT a greenfield rebuild, NOT permission to redesign the website, and NOT permission to replace the working assistant architecture.**

---

## 0. V1 protection record

Before any V2 work began, the stable V1 state was committed, tagged, and backed up. These references must remain intact throughout V2 development.

- **V1 commit:** `1380fd4e869f27231137a3020c30e695f623b92f`
- **Tag:** `t2c-v1-stable` → points to the V1 commit
- **Backup branch:** `backup/t2c-v1` → points to the V1 commit
- **V2 development branch:** `feature/t2c-v2` → branched from `t2c-v1-stable`

Rules that apply for the duration of V2 development:
- `main`, `backup/t2c-v1`, and the `t2c-v1-stable` tag must not be modified, force-pushed, or rewritten.
- All V2 work happens only on `feature/t2c-v2` (or branches made from it).
- `feature/t2c-v2` is not merged into `main` until V2 is fully tested and separately approved.
- `.env` is never committed, under any circumstances.
- No AI-assistance, co-author, or tooling attribution appears anywhere in commit messages, commit metadata, or tracked files.
- All commits use the existing project Git author identity only.

---

## 1. Product principle

Trash2Cash V2 should help people:

1. identify what recyclable material they have,
2. understand whether T2C supports/accepts it,
3. understand basic preparation requirements,
4. estimate its reference value,
5. find an appropriate drop-off location,
6. ask T2C for help when they are unsure what material they have.

### Core user journey

```
I HAVE WASTE
    ↓
WHAT IS IT?
    ↓
CATEGORY → MATERIAL TYPE
    ↓
IS IT ACCEPTED?
    ↓
WHAT IS IT WORTH?
    ↓
WHERE CAN I TAKE IT?
    ↓
RECYCLE
```

### Alternative path

```
I DON'T KNOW WHAT THIS IS
    ↓
ASK T2C
    ↓
MATERIAL CATALOGUE
    ↓
IDENTIFICATION / GUIDANCE
```

### Future path (not implemented now)

```
PHOTO
    ↓
T2CVision
    ↓
MATERIAL CATALOGUE
    ↓
ACCEPTANCE
    ↓
REWARD
    ↓
DROP-OFF
```

The future T2CVision integration is explicitly **not** implemented as part of V2 unless infrastructure already exists that can be safely prepared without changing current product scope. No fake/simulated image recognition may be built. If T2CVision is referenced in the UI, it must be labeled honestly as not yet available.

---

## 2. Material model V2

The V1 model (three broad buckets: Plastic, Nylon, Aluminum) is too simplistic for V2. V2 replaces it with a proper material catalogue structured as:

```
CATEGORY
    ↓
MATERIAL TYPE
    ↓
ALIASES / FAMILIAR EXAMPLES
    ↓
TECHNICAL FAMILY
    ↓
ACCEPTANCE
    ↓
REFERENCE RATE
    ↓
PREPARATION
    ↓
SUPPORTED DROP-OFF LOCATIONS
```

**UI language principle:** use familiar Nigerian terminology in the user-facing UI while keeping more technically accurate recycling information underneath as secondary/educational detail. Do not force ordinary users to understand polymer abbreviations.

Example:
- User-facing: **"Pure Water Sachets"**
- Secondary technical information: *"Flexible PE recycling stream"*

Do not present every locally called "nylon" product as technically nylon polymer — "nylon" in Nigerian usage covers flexible polyethylene packaging, not the technical polymer called nylon (polyamide). The catalogue's user-facing category name may use the familiar term ("Flexible Plastics (Nylon)") while the technical family field records the accurate polymer family.

---

## 3. Initial V2 material taxonomy

Three top-level categories, seven material types total, for the initial release. Do not add more materials than these without new verified acceptance/rate data (see Guardrails).

### A. Rigid Plastics

#### A1. PET Bottles

- **Examples:** water bottles; Coke/Fanta/soft-drink bottles; other PET beverage bottles
- **Aliases:** PET; PET bottle; plastic bottle; water bottle; coke bottle; fanta bottle; soft drink bottle; beverage bottle
- **Reference rate:** ₦200/kg
- **Rate status:** reference
- **Preparation guidance:**
  - empty contents
  - reasonably clean
  - keep separate from unrelated waste
  - dry where practical

#### A2. HDPE Containers

- **Examples:** detergent bottles; bleach containers; plastic kegs/jerrycans; selected household/personal-care containers
- **Aliases:** detergent bottle; bleach bottle; plastic keg; jerrycan; jerry can; HDPE container; HDPE bottle
- **Reference rate:** ₦120/kg
- **Rate status:** placeholder/reference baseline
- **Note:** the data architecture must make this rate easy to update later without touching multiple systems.

#### A3. Other Accepted Rigid Plastics

- **Examples:** selected PP containers; plastic bowls; selected buckets; selected lids/caps; similar accepted hard plastics
- **Reference rate:** ₦120/kg
- **Rate status:** placeholder/reference baseline
- **Important:** do not imply that every rigid plastic object is automatically accepted just because it falls in this catch-all category.

### B. Flexible Plastics (Nylon)

User-facing category name: **"Flexible Plastics (Nylon)"** — preserves familiar Nigerian terminology while avoiding technically incorrect classification internally (see Section 2).

#### B1. Pure Water Sachets

- **Examples:** used drinking-water sachets
- **Aliases:** pure water nylon; water nylon; pure water sachet; water sachet; sachet water; sachet water nylon; sachet
- **Reference rate:** ₦60/kg
- **Rate status:** reference
- **Preparation guidance:**
  - empty
  - reasonably clean
  - dry where practical
  - keep separate from unrelated waste

#### B2. Shopping / Carrier Bags

- **Examples:** accepted polyethylene shopping/carrier bags
- **Reference rate:** ₦60/kg
- **Rate status:** placeholder/reference baseline
- **Important:** do not imply every shopping bag composition is accepted.

#### B3. Clean Packaging Film

- **Examples:** accepted flexible plastic packaging film; other accepted clean PE film
- **Reference rate:** ₦60/kg
- **Rate status:** placeholder/reference baseline
- **Important:** do not imply all food wrappers or multilayer packaging are recyclable.

### C. Metals

#### C1. Aluminium Beverage Cans

- **Examples:** soft-drink cans; malt cans; energy-drink cans; other aluminium beverage cans
- **Aliases:** aluminium can; aluminum can; drink can; beverage can; coke can; fanta can; malt can
- **Reference rate:** ₦500/kg
- **Rate status:** reference

**Guardrail:** do not add copper, brass, steel, iron, e-waste, batteries, etc. merely because they can theoretically be recycled. Those are future catalogue additions only after reliable acceptance/rate data exists for them.

---

## 4. Rate data model

Rates must **not** be hardcoded independently across templates, JavaScript, chatbot intents, and backend logic. There must be **one authoritative material catalogue/source of truth**.

Each material should support fields conceptually similar to:

```
id
slug
name
category_id
technical_family
description
aliases[]
examples[]
preparation[]
acceptance_status
rate_per_kg
rate_min (if needed later)
rate_max (if needed later)
rate_status
rate_source
rate_source_date
last_verified
notes
supported_location_ids[]
```

Adapt this structure appropriately to the existing application architecture rather than forcing an unnecessary database migration. The important requirement is **one canonical material source** — every other system (reward calculator, API, Materials page, Ask T2C, Drop-off Finder) reads from it rather than maintaining its own copy.

### Acceptance statuses

At minimum, the catalogue must support these acceptance statuses:

- `accepted`
- `selected_locations`
- `rate_unavailable`
- `not_currently_accepted`
- `needs_identification`

**Rule:** do not invent a price when the catalogue says the rate is unavailable.

---

## 5. Rate disclaimer

Reference rates are **not** universal Nigerian market prices. Rates vary by:

- recycler
- location
- cleanliness
- material condition
- colour/grade where relevant
- volume
- market conditions
- position in the recycling supply chain

Use concise UX language such as:

> "Reference estimate only. Actual recycler rates may vary by location, material condition and current market price."

Do not make the interface sound uncertain everywhere, but do not present reference rates as guaranteed payouts either.

---

## 6. Homepage rate section

Replace the current broad Plastic / Nylon / Aluminum rate presentation with a cleaner **"Popular Recyclables"** presentation, for example:

```
PET Bottles
Water & soft-drink bottles
₦200/kg

Pure Water Sachets
Clean used sachets
₦60/kg

Aluminium Cans
Beverage cans
₦500/kg
```

Include a clear **"View all materials →"** link to the new Materials experience.

This should naturally eliminate the previous mobile alignment problem where the longer Nylon description pushed the price onto an awkward second line.

**Guardrail:** do not unnecessarily redesign unrelated homepage sections. Preserve the existing visual identity.

---

## 7. New Materials experience

Create a `/materials` page (or the architecturally-equivalent route) answering **"What can I recycle?"**. It must be mobile-first and easy to browse.

### Top-level presentation

- Rigid Plastics
- Flexible Plastics (Nylon)
- Metals

Each category exposes its supported material types. Each material should be able to display:

- material name
- category
- familiar examples
- technical family as secondary/educational information
- acceptance status
- preparation guidance
- reference rate, or the appropriate "unavailable" state
- rate disclaimer
- Estimate Reward CTA
- Find Drop-off CTA

**Guardrail:** do not create an encyclopedia. Keep the content practical and user-oriented.

If appropriate within the existing UI, add search/filter capability using material names, aliases, and examples. A user searching terms such as "pure water nylon," "coke bottle," or "detergent bottle" should be able to reach the relevant material.

---

## 8. Reward Calculator V2

Replace the overly broad material selector with a dependent category/material flow.

### Desired conceptual UX

```
WHAT ARE YOU RECYCLING?

Category
[ Rigid Plastics ▼ ]

Material
[ PET Bottles ▼ ]

Examples
Water bottles, Coke/Fanta bottles

Weight
[ 5.0 ] kg

Location
[ Ikeja ▼ ]

ESTIMATE REWARD
```

Changing the category updates the available material types. The result should identify the specific material, for example:

```
PET BOTTLES

5 kg × ₦200/kg

Estimated reward
₦1,000

Reference estimate only.
Actual recycler rates may vary.

Find a drop-off →
```

**Rules:**
- Do not duplicate reward arithmetic in frontend and backend unless the existing architecture requires a carefully synchronized representation.
- Prefer the backend/canonical data layer as the source of truth.
- Preserve existing API behavior where practical.
- If backward compatibility can safely be maintained, do so.
- If an API contract must change, document exactly what changed and update all callers/tests.

---

## 9. "Not sure what this is?"

Add an unobtrusive path around the material selection experience:

> "Not sure what material this is? Ask T2C →"

This routes the user toward the existing Ask T2C experience.

**Guardrail:** do not implement fake image recognition. Do not pretend T2CVision is integrated if it is not.

---

## 10. Drop-off Finder V2

Evolve the Drop-off Finder toward answering **"Where can I recycle THIS material?"** rather than merely "Where is a recycling location?"

The data model must support a **Material ↔ Supported Drop-off Locations** relationship. A location should only be described as accepting a material when application data actually supports that relationship.

**UNKNOWN MUST NOT BECOME TRUE.** If acceptance for a material/location combination is unknown, do not invent compatibility.

Design graceful states such as:
- accepted here
- selected locations
- compatibility not yet verified

**Guardrails:**
- Preserve existing verified location data.
- Do not fabricate addresses, partners, phone numbers, hours, or acceptance relationships.

---

## 11. Ask T2C V2

The existing Ask T2C assistant already has grounded architecture and must **not** be casually replaced. Inspect it first.

Preserve the existing general architecture where possible, including:
- structured intent extraction
- Python/tool execution
- grounded response generation
- safety/grounding guard
- local fallback behavior
- existing tests/evaluations

**Key V2 improvement:** Ask T2C, Reward Calculator, Materials, and Drop-off Finder must ultimately rely on the SAME material catalogue.

Example:

```
User: "How much are 10kg of pure water nylon?"

"pure water nylon"
    ↓
alias resolution
    ↓
pure_water_sachets
    ↓
canonical rate
    ↓
reward calculation
    ↓
grounded response
```

**Rule:** do not maintain separate conflicting rate tables inside chatbot intents. If legacy intents currently contain rates, migrate/refactor them carefully so the canonical material catalogue controls all numeric material facts.

### Handling uncertainty

The assistant must handle uncertainty correctly. Example:

> "I have Indomie wrappers."

It should **not** automatically invent a reward. If the material cannot be confidently mapped to an accepted catalogue item, it should respond appropriately: classification uncertain, acceptance not confirmed, and suggest checking supported materials / Ask T2C guidance.

---

## 12. Alias resolution

Build reusable, deterministic alias resolution serving:
- Materials search
- Ask T2C
- potentially calculator convenience
- future T2CVision mapping

Normalize reasonably: case, whitespace, common punctuation.

**Guardrail:** do not build an unnecessarily complex NLP system if deterministic alias matching works. Maintain a clean extension path for later.

---

## 13. Preparation guidance

Each material supports concise, practical preparation instructions, for example:
- empty contents
- keep reasonably clean
- dry where practical
- separate material types
- remove unrelated waste where necessary

**Guardrail:** do not add a complicated questionnaire to the reward calculator. Preparation is guidance, not friction.

---

## 14. Mobile navigation bug

Physical-phone testing exposed a real mobile navigation issue: the hamburger/dropdown menu opened too short/clipped and did not comfortably expose the navigation options.

### Requirements

- enough usable height to display navigation options
- no accidental clipping
- scroll naturally if content exceeds available viewport
- respect mobile viewport height
- prefer modern viewport units such as `dvh` where appropriate
- all primary destinations accessible
- CTA accessible
- touch targets ≥ approximately 44px
- menu closes appropriately after navigation
- no horizontal overflow
- keyboard/accessibility behavior remains reasonable
- do not redesign the desktop header unnecessarily

### Required test widths

At least: 375px, 390px, 430px, 768px, 1440px.

The real physical phone remains the final validation step and is performed by the product owner, not claimed as having been performed by any automated or assistant process.

---

## 15. Mobile-first V2 UX

Mobile is not "desktop stacked vertically." A real T2C user may be outside holding recyclables and using one hand to: identify material, enter weight, select location, estimate reward, find drop-off, ask T2C.

### Priorities

- readable controls
- large tap targets
- clear hierarchy
- native-feeling dropdown/select behavior
- no clipped options
- no tiny text
- no horizontal scrolling
- no important result appearing invisibly below the fold without feedback
- sensible focus/scroll behavior after calculations
- keyboard-safe chat
- responsive cards
- no excessive whitespace

Preserve existing mobile improvements that already work.

---

## 16. Visual design rule

**Do not perform another broad visual redesign.** The current T2C visual identity is approved.

Targeted UI changes are permitted only where required by:
- Materials page
- new taxonomy
- Calculator V2
- material-aware Drop-off Finder
- mobile navigation fix
- responsive layout
- clearer hierarchy

Reuse the existing typography, spacing system, component language, buttons, cards, colors, imagery, and interaction style. Do not change unrelated sections just to follow a different design preference.

---

## 17. Existing images

Preserve the recently implemented image work unless a V2 requirement genuinely conflicts with it.

**Do not:**
- replace approved imagery
- introduce stock imagery
- introduce AI-generated imagery
- remove images simply because V2 is being implemented

Maintain existing image optimization and responsive behavior.

---

## 18. Data sources / documentation

Document the V2 material catalogue and which values are:
- reference values
- placeholders
- unavailable
- verified acceptance information
- assumptions

Create/update appropriate documentation (e.g. `docs/MATERIAL_CATALOGUE_V2.md`, `docs/T2C_V2_IMPLEMENTATION.md`). Do not silently present placeholders as verified facts.

### Initial rates (authoritative for first implementation)

| Material | Rate | Status |
|---|---|---|
| PET Bottles | ₦200/kg | reference |
| HDPE Containers | ₦120/kg | placeholder/reference baseline |
| Other Accepted Rigid Plastics | ₦120/kg | placeholder/reference baseline |
| Pure Water Sachets | ₦60/kg | reference |
| Shopping / Carrier Bags | ₦60/kg | placeholder/reference baseline |
| Clean Packaging Film | ₦60/kg | placeholder/reference baseline |
| Aluminium Beverage Cans | ₦500/kg | reference |

These must remain easy to update centrally (see Section 4).

---

## 19. Testing

Rendering pages is not sufficient to consider the task complete. Preserve all existing tests and add appropriate tests for V2.

### Minimum required coverage

**Material catalogue**
- expected categories exist
- expected materials exist
- aliases resolve correctly
- rates come from canonical data
- placeholder/reference metadata preserved
- unsupported material does not receive an invented rate

**Reward engine**
- correct material-specific calculations
- decimal weights
- zero/invalid weights
- unsupported material
- rate-unavailable state
- backward compatibility where applicable

**API**
- valid requests
- invalid category/material combinations
- malformed requests
- unsupported material
- expected response structure

**Ask T2C**
- pure water nylon alias
- PET/common bottle aliases
- detergent/HDPE-type language
- aluminium can aliases
- unsupported/uncertain materials
- no invented numeric rate
- canonical rate usage
- existing fallback behavior

**Drop-off**
- material filtering
- unknown compatibility does not become accepted
- existing location data preserved

**Frontend**
- dependent category/material behavior
- Materials navigation
- calculator result
- rate disclaimer
- Ask T2C path
- mobile menu
- no obvious overflow

**Regression**
- all pre-V2 tests still pass unless an intentionally changed contract has a documented replacement

Run lint/build/static checks already appropriate for the repository.

---

## 20. AI evaluation

The existing Ask T2C system previously underwent grounded evaluation. V2 must not reduce its reliability.

Create a focused V2 evaluation set covering natural Nigerian/user phrasing, including examples such as:

- "How much is 5kg of pure water nylon?"
- "I have 10kg of sachet water nylon"
- "How much for Coke bottles?"
- "Can I recycle detergent bottles?"
- "I have plastic kegs"
- "How much are aluminium cans?"
- "Do you take Indomie wrappers?"
- "Can I recycle any kind of nylon?"
- "I have some plastic but I don't know what type it is"

### Evaluate

- intent/tool selection
- material resolution
- argument extraction
- numeric grounding
- unsupported-material handling
- hallucination resistance

**Rule:** do not weaken existing safety/grounding behavior merely to increase answer rate.

---

## 21. Accessibility

Preserve/improve:
- semantic labels
- keyboard accessibility
- visible focus
- ≥44px mobile touch targets where practical
- appropriate form labels
- useful error states
- reduced-motion behavior
- sufficient text wrapping
- no hover-only essential interactions

---

## 22. Performance

Do not introduce a large frontend framework or unnecessary dependencies merely for this feature. Reuse the existing architecture. Keep:
- assets optimized
- JavaScript modest
- page load reasonable
- no unnecessary network calls
- no duplicated giant data payloads if avoidable

---

## 23. Implementation order

```
PHASE 0   Repository audit + protect V1.                         [COMPLETE]
PHASE 1   Design canonical V2 material catalogue/data layer.
PHASE 2   Update reward engine/API carefully.
PHASE 3   Implement alias resolution.
PHASE 4   Build Materials experience.
PHASE 5   Upgrade Reward Calculator.
PHASE 6   Upgrade Drop-off Finder.
PHASE 7   Integrate catalogue into Ask T2C.
PHASE 8   Update homepage popular recyclable rates.
PHASE 9   Fix mobile navigation and perform responsive polish.
PHASE 10  Tests + AI evaluation + regression checks + documentation.
```

Do not jump directly into templates before understanding the data architecture.

### Incremental work rule

After each major phase:
- run relevant tests
- preserve existing behavior
- fix regressions before continuing
- do not silently remove functionality
- do not fabricate recycling/location data
- do not duplicate canonical material/rate data
- do not touch `main`, `backup/t2c-v1`, or `t2c-v1-stable`
- never commit `.env`
- never add AI/assistant or co-author attribution to commits
- use only the project's existing Git author identity for any commits
- normal project-oriented commit messages only

---

## 24. Guardrails (do not)

- destroy or overwrite T2C V1
- work directly on the stable branch after the V2 branch exists
- commit `.env`
- expose API keys
- invent recycling rates
- silently label placeholder rates as verified
- invent drop-off compatibility
- fabricate Nigerian recycling facts
- duplicate rate truth across multiple systems
- replace the existing grounded Ask T2C architecture without strong technical reason
- implement fake T2CVision
- perform an unrelated site redesign
- add every theoretically recyclable material
- break existing routes without documenting/migrating them
- remove working functionality just to simplify implementation
- claim browser/device testing that was not actually performed
- claim physical-phone testing (the product owner performs this)

If ambiguity arises that risks data loss, V1 corruption, security issues, or major product behavior changes: stop and explain rather than guessing.

---

## 25. Completion report requirements

On completion, a structured report must be produced containing:

1. **V1 preservation** — original branch/state, V1 commit, V1 tag, V2 branch, confirmation `.env` remains untracked/ignored
2. **Architecture** — canonical material data location, alias resolution approach, reward engine changes, API changes, Ask T2C integration, drop-off relationship design
3. **Product changes** — Materials, Reward Calculator, Drop-off Finder, Ask T2C, homepage, mobile navigation
4. **Data** — for every material: rate, rate status, acceptance status, whether reference/placeholder, where it is stored
5. **Files changed** — every significant modified/created file and why
6. **Test results** — old tests, new tests, total pass/fail, lint/build/static checks, AI evaluation results
7. **Responsive validation** — exactly which widths/checks were actually performed (no claimed real-device testing)
8. **Remaining risks / manual checks** — explicit list of anything that needs manual verification
9. **Phone test plan** — a short checklist for testing V2 on a real phone over the local network
10. **Git status** — final branch, `git status`, whether anything remains uncommitted

---

## 26. Final success criteria

V2 is successful only if:

- T2C V1 remains recoverable
- material taxonomy has one canonical source of truth
- rates are material-specific
- placeholder data is explicitly represented as such
- Calculator uses specific materials
- Materials page works
- Drop-off can reason about material compatibility without inventing it
- Ask T2C uses the canonical catalogue
- aliases understand familiar Nigerian terminology
- unsupported materials do not receive hallucinated prices
- homepage uses specific popular recyclables
- mobile navigation is fixed
- current visual identity remains recognizable
- existing functionality remains intact
- tests pass
- AI grounding remains strong
- V2 is ready for final physical-phone testing by the product owner
