# Image Asset Audit — `assets/` raw photography

*Audit date: 2026-09-23. Every image was individually viewed (not just measured) before writing this document.*

## Top-line finding — read this before anything else

**All 13 images carry a visible third-party TikTok watermark, "@edward.wonder," in the bottom-right corner, and the large majority also show "Lagos State Government" and/or "Pitstop Lagos" logos on the workers' safety vests.** All 13 share the exact same 2:3 aspect ratio (0.666) at several different downsampled resolutions (2560px down to 1482px tall) and filenames of the form `temp_image_<UUID>.WEBP` — the signature of images saved from a phone's iMessage/Photos share sheet, not original camera files. Taken together, this is one photographer's shoot of (most likely) a real Lagos street-cleaning crew or community clean-up event, redistributed via TikTok, not original photography shot for or owned by Trash2Cash.

This matters for three separate reasons:

1. **Rights.** There is no evidence in this repository that Trash2Cash has permission from @edward.wonder to use this photography commercially or publicly. Using it without that permission is a real copyright risk, not a hypothetical one.
2. **False affiliation.** Most images clearly show "Lagos State Government" and "Pitstop Lagos" branding on vests and uniforms. Publishing these on Trash2Cash would visually imply a partnership or endorsement from a real government body and a real organization that, as far as anything in this repo shows, does not exist. That's a misrepresentation risk independent of the copyright one.
3. **The originals aren't really "raw."** They're already-compressed, already-watermarked redistributions — there is no higher-resolution, watermark-free "original" available to fall back to.

**Update — resolved:** the user confirmed permission to use this photographer's work and confirmed the Lagos State Government / Pitstop Lagos branding shown is accurate and fine to display. The remaining issue — the TikTok watermark itself — was solved the honest way: **geometric cropping**, not AI inpainting or watermark removal. Three images were approved and placed; see "Images used" at the end of this document. The rest of this document is left as originally written (individual audit of all 13, written before the rights question was resolved) since it's still the accurate composition/crop analysis.

Originals are untouched in `assets/` — nothing was cropped, compressed, or watermark-edited in place. All working copies live in `static/images/`.

---

## Per-image audit

### 1. `temp_image_222F833F-9746-4E4E-AB36-3C3C4F999675.WEBP`
- **Dimensions:** 1336×2004 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 678 KB · **Quality:** sharp on primary subject, good telephoto background blur, slightly busy
- **Subject:** A woman in a white hijab and orange/grey hi-vis vest (Lagos State Government + partner badges), pink patterned trousers, holding a broom, mid-stride, looking down. Two more workers (one in a red coverall/"Pitstop Lagos" vest, one in navy coveralls) are in the foreground, one checking a phone.
- **Activity:** Street sweeping, multiple people, mid-task
- **People:** 3 clearly visible, partially cropped by frame edges
- **Composition:** Vertical, primary subject right-of-center, busy foreground; green foliage fills the top third
- **Negative space:** Minimal — foliage and figures fill most of the frame
- **Focal area:** The woman's face/upper body, roughly center-right
- **Crop risk:** Common social crops (square, 16:9 landscape) would very likely cut the woman's head or the other workers awkwardly — this is a poor square-crop candidate
- **Overlays:** TikTok watermark (bottom right); "Lagos State Government" and "Pitstop Lagos" logos on vests
- **Public-UI suitable:** No — watermark + government/org branding + busy composition
- **Draft alt text (if ever cleared):** "A council street-sweeping crew clearing a roadside in Lagos, Nigeria."
- **Best hypothetical use:** Recycling-education / "real communities" supporting imagery — not a hero candidate (too busy)
- **Classification:** Not recommended (rights + branding)

### 2. `temp_image_29D722FA-3BF5-4B1E-8AB9-4070CD352658.WEBP`
- **Dimensions:** 1706×2560 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 1.11 MB · **Quality:** high — sharp subject, clean bokeh
- **Subject:** A man in navy coveralls and an orange vest, bending to pick up a magenta dustpan and broom from a low wall; a second worker's legs/torso is visible behind him
- **Activity:** Sweeping/collecting debris
- **People:** 2 (one primary, one partially cropped)
- **Composition:** Vertical, subject center-low, lots of green foliage and a building in the upper two-thirds
- **Negative space:** Some, in the upper third (foliage/sky), usable for text overlay
- **Focal area:** Mid-frame, the bending figure
- **Crop risk:** Moderate — a square crop would work if cropped from the top; a wide landscape crop would lose the dustpan (the "action" of the shot)
- **Overlays:** TikTok watermark (bottom right)
- **Public-UI suitable:** No — watermark
- **Draft alt text:** "A sanitation worker collecting swept debris into a dustpan on a Lagos street."
- **Best hypothetical use:** How It Works — "Collect" step
- **Classification:** Not recommended (rights)

### 3. `temp_image_2B024E0F-8400-4B8D-A844-52A757954749.WEBP`
- **Dimensions:** 988×1482 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 397 KB · **Quality:** high — this is the single strongest action shot in the set: visible dust kicked up, sharp focus, clean single subject
- **Subject:** One man, orange vest, pink shorts, grey cap, mid-sweep with a colorful broom, leaves and visible dust at his feet
- **Activity:** Active street sweeping
- **People:** 1 (single clear subject — the cleanest composition in the batch)
- **Composition:** Vertical, subject center-left, diagonal broom line leads the eye, soft green background
- **Negative space:** Moderate, upper-right and left edge
- **Focal area:** The face and the broom/dust action at the bottom
- **Crop risk:** Low — this is the most crop-flexible image in the set; a tight square or 4:5 crop keeping the face and broom both works
- **Overlays:** TikTok watermark (bottom right); no visible government/org logo in this particular crop (vest badge not legible at this resolution)
- **Public-UI suitable:** No — watermark (the branding concern is weaker here since no legible logo, but the watermark alone still blocks it)
- **Draft alt text:** "A worker in a high-visibility vest sweeping fallen leaves from a Lagos street, dust rising in the morning light."
- **Best hypothetical use:** **This is the strongest hero/CTA candidate in the entire set if rights were secured** — single subject, genuine action, real dust/motion, minimal distracting branding
- **Classification:** Not recommended today (rights) — flagged as highest-priority to revisit if licensing is resolved

### 4. `temp_image_6998FABD-338A-4670-AD90-5FC157E23C62.WEBP`
- **Dimensions:** 1706×2560 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 1.23 MB · **Quality:** high, joyful expression, sharp
- **Subject:** A woman in orange coveralls, arm raised in a peace sign, big smile, "MOLTENI" cap, mask pulled to chin; a man in an orange vest beside her; two more workers partially in frame (one in red)
- **Activity:** Post-cleanup celebratory moment, not active work
- **People:** 4 (2 clear, 2 partial)
- **Composition:** Vertical, primary subject left-of-center, wheelbarrows visible bottom-right
- **Negative space:** Upper third (foliage/sky)
- **Focal area:** The woman's face and raised arm
- **Crop risk:** Moderate — raised arm would be cut by an aggressive top crop; safe if cropped from the sides only
- **Overlays:** TikTok watermark (bottom right); Lagos State Government-style badge partially visible on the second man's vest
- **Public-UI suitable:** No — watermark + partial branding
- **Draft alt text:** "A cleanup crew member celebrating with a raised hand after a street-sweeping shift in Lagos."
- **Best hypothetical use:** CTA section (genuine joy/energy reads well for a closing "get involved" moment) or About/mission
- **Classification:** Not recommended (rights)

### 5. `temp_image_6FDFC0A8-B4DA-4562-A461-9E9244F57480.WEBP`
- **Dimensions:** 1138×1706 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 407 KB · **Quality:** high, clean single subject
- **Subject:** One man, orange vest, earbuds in, gold watch, sweeping leaves at a curb; two blurred figures sweeping in the background
- **Activity:** Active sweeping
- **People:** 1 clear + 2 out-of-focus background
- **Composition:** Vertical, subject center, curb line leads diagonally
- **Negative space:** Moderate, upper-left (sky/road)
- **Focal area:** Face and hands/broom
- **Crop risk:** Low-moderate — a portrait or 4:5 crop is safe; a wide crop loses the broom action
- **Overlays:** TikTok watermark (bottom right); no legible logo
- **Public-UI suitable:** No — watermark
- **Draft alt text:** "A worker sweeping fallen leaves from a roadside curb in Lagos."
- **Best hypothetical use:** How It Works — "Collect" step, or Education section
- **Classification:** Not recommended today (rights) — good secondary candidate if cleared

### 6. `temp_image_74899A6D-D60C-4F93-BC76-22D37CD1771C.WEBP`
- **Dimensions:** 1706×2560 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 902 KB · **Quality:** high, clean standing portrait
- **Subject:** One woman, white cap, orange vest clearly reading "Lagos State Government" and "Pitstop Lagos," holding a water bottle, broom/dustpan resting nearby, looking off-camera
- **Activity:** Pause/standing, not mid-task
- **People:** 1
- **Composition:** Vertical, centered, buildings and a water tower in soft-focus background
- **Negative space:** Generous on both sides and top — good for text overlay if it weren't for the branding
- **Focal area:** Face, centered
- **Crop risk:** Low — very crop-flexible, centered subject
- **Overlays:** TikTok watermark (bottom right); **clearly legible "Lagos State Government" and "Pitstop Lagos" logos** on the vest
- **Public-UI suitable:** No — watermark + clearly legible government/org branding (worst offender in the set for this specific issue)
- **Draft alt text:** "A cleanup crew member pausing with water during a street-sweeping shift."
- **Best hypothetical use:** Would otherwise be a strong About/mission portrait — blocked hardest by branding of anything in the set
- **Classification:** Not recommended (rights + clearest branding conflict)

### 7. `temp_image_7E341FE4-B711-4BD5-9185-ED97F34B4D31.WEBP`
- **Dimensions:** 1526×2288 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 604 KB · **Quality:** high
- **Subject:** One person in a red coverall uniform (distinct from the orange-vest crew — possibly a different role/organization), headwrap, sweeping a curb into a pink dustpan; a black bin bag at the right edge
- **Activity:** Active sweeping
- **People:** 1
- **Composition:** Vertical, subject left-of-center, road curves away in the background — good sense of place
- **Negative space:** Right half of the frame, moderate
- **Focal area:** The sweeping motion, lower-left
- **Crop risk:** Low-moderate; a right-anchored crop preserves the subject
- **Overlays:** TikTok watermark (bottom right); small logo patch on the coverall, not clearly legible
- **Public-UI suitable:** No — watermark
- **Draft alt text:** "A sanitation worker in a red uniform sweeping a road curb in Lagos."
- **Best hypothetical use:** Education / How It Works
- **Classification:** Not recommended today (rights)

### 8. `temp_image_90FC8C6A-7507-401A-811B-174D45DE8AC1.WEBP`
- **Dimensions:** 1706×2560 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 1.08 MB · **Quality:** high
- **Subject:** One woman, bandana, long braids, orange vest, bent over sweeping into a blue dustpan at a low wall
- **Activity:** Active sweeping/collecting
- **People:** 1
- **Composition:** Vertical, subject center-low, leafy branches frame the top
- **Negative space:** Upper half, generous
- **Focal area:** Lower-center, the sweeping action
- **Crop risk:** Low — safe for portrait or square crops anchored low
- **Overlays:** TikTok watermark (bottom right); small vest badge, not clearly legible
- **Public-UI suitable:** No — watermark
- **Draft alt text:** "A worker sweeping debris into a dustpan beside a low wall in Lagos."
- **Best hypothetical use:** How It Works — "Collect" step
- **Classification:** Not recommended today (rights)

### 9. `temp_image_9878C8D2-F0B9-4CD3-8848-EEF8B5FC98B2.WEBP`
- **Dimensions:** 1706×2560 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 1.05 MB · **Quality:** high — genuinely warm, direct-to-camera expression
- **Subject:** One man, orange vest over an orange top, pushing a wheelbarrow loaded with black garbage bags, smiling directly at the camera, earpiece visible
- **Activity:** Transporting collected waste — the clearest "material recovery in motion" shot in the set
- **People:** 1
- **Composition:** Vertical, subject center, wheelbarrow leads the eye right, tree canopy frames the top
- **Negative space:** Upper third, moderate
- **Focal area:** The face (direct eye contact with camera) and the loaded wheelbarrow
- **Crop risk:** Low-moderate — a 4:5 or square crop centered on the subject works; avoid cutting the wheelbarrow's load, which is the point of the shot
- **Overlays:** TikTok watermark (bottom right); small badge on vest, partially legible ("...Lagos")
- **Public-UI suitable:** No — watermark + partial branding
- **Draft alt text:** "A worker smiling while pushing a wheelbarrow of collected waste through a Lagos street."
- **Best hypothetical use:** **Second-strongest candidate in the set** — Impact/Mission section, or How It Works "Collect → Drop off" bridge; direct eye contact makes it a strong human-connection image
- **Classification:** Not recommended today (rights) — high priority to revisit if licensing resolved

### 10. `temp_image_99C0E15A-EBE4-4F1C-8271-CB75D2491C73.WEBP`
- **Dimensions:** 1138×1706 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 306 KB (most compressed file in the set — visibly softer than the others)
- **Subject:** A group of ~9 people walking together across a bridge/overpass with wheelbarrows and brooms
- **Activity:** Group movement between work sites
- **People:** 9, none large enough in frame to be an individual focal subject
- **Composition:** Vertical, figures occupy the lower half, large open sky above
- **Negative space:** Large, upper two-thirds — genuinely useful for a hero-style text overlay compositionally
- **Focal area:** The walking group, lower-center
- **Crop risk:** Moderate — a wide landscape crop from the lower half works; a tall crop wastes the empty sky
- **Overlays:** TikTok watermark (bottom right)
- **Public-UI suitable:** No — watermark; also multiple identifiable people whose consent for commercial/public use is unknown
- **Draft alt text:** "A team of sanitation workers walking together across an overpass in Lagos."
- **Best hypothetical use:** Impact/Mission — "real communities, not just software" framing
- **Classification:** Not recommended (rights + consent-at-scale — many identifiable faces)

### 11. `temp_image_A4BF57E0-AF50-49BB-9533-A320C2579D16.WEBP`
- **Dimensions:** 1354×2032 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 700 KB · **Quality:** high
- **Subject:** One man sitting on a concrete barrier, drinking water, orange rubber gloves, **holding a long bladed tool (a cutlass/machete-style blade)** across his lap
- **Activity:** Rest break
- **People:** 1
- **Composition:** Vertical, centered, power-line pylons in the background
- **Negative space:** Moderate, upper half
- **Focal area:** Face and the bottle at his mouth
- **Crop risk:** Low for the upper body; a crop should deliberately exclude the blade if used at all
- **Overlays:** TikTok watermark (bottom right); Lagos State Government + Pitstop Lagos badges legible on vest
- **Public-UI suitable:** No — watermark, branding, **and** the visible blade is a separate reason to avoid this one specifically even if rights were resolved: it reads as alarming out of context for a consumer product image, regardless of its mundane real use (clearing vegetation)
- **Draft alt text:** "A worker taking a water break during a street-cleaning shift."
- **Best hypothetical use:** None recommended — the blade makes this the weakest candidate in the set independent of the rights issue
- **Classification:** Not recommended (rights + branding + content concern)

### 12. `temp_image_D47662EC-6C91-4412-96FB-A79CA00CDE34.WEBP`
- **Dimensions:** 1706×2560 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 1.36 MB (largest file in the set) · **Quality:** high — sharp, determined expression, strong composition
- **Subject:** One man, orange vest ("Lagos State Government" badge legible), pushing a wheelbarrow loaded with black garbage bags; a second person's legs visible at the right edge
- **Activity:** Transporting collected waste
- **People:** 1 clear + 1 partial
- **Composition:** Vertical, subject center, tree canopy frames the top, road/parked car soft-focus background
- **Negative space:** Upper-left, moderate
- **Focal area:** Face and the loaded wheelbarrow
- **Crop risk:** Low-moderate — avoid cropping the wheelbarrow's contents
- **Overlays:** TikTok watermark (bottom right); legible "Lagos State Government" badge
- **Public-UI suitable:** No — watermark + clearly legible branding
- **Draft alt text:** "A worker pushing a wheelbarrow of collected waste through a Lagos neighborhood street."
- **Best hypothetical use:** Impact/Mission, or How It Works "Collect" step — this and image 9 are the two strongest "material recovery" shots in the set
- **Classification:** Not recommended today (rights + branding) — high priority to revisit if resolved

### 13. `temp_image_EF879AD2-C7DB-4CB6-9B2C-7E5B1F1C7F1A.WEBP`
- **Dimensions:** 1050×1574 · **Aspect ratio:** 2:3 · **Orientation:** portrait
- **Size:** 690 KB · **Quality:** high, posed group portrait
- **Subject:** A large posed team of ~25+ people in orange vests, some standing, some sitting, several with arms raised, in front of trees under an open sky
- **Activity:** Posed group portrait (not mid-task)
- **People:** 25+, many individually identifiable
- **Composition:** Vertical, group fills the lower two-thirds, large sky above
- **Negative space:** Large, upper third — but the group itself is too busy/detailed for text overlay
- **Focal area:** No single subject — this is a documentary "the whole team" shot
- **Crop risk:** High for anything but a wide landscape crop of the lower portion; any portrait-oriented crop will cut people out
- **Overlays:** TikTok watermark (bottom right)
- **Public-UI suitable:** No — watermark, and 25+ identifiable people whose consent for commercial/public reuse is unknown (the highest consent-risk image in the set)
- **Draft alt text:** "A large team of cleanup volunteers posing together after a community street-cleaning event."
- **Best hypothetical use:** None recommended for UI placement even hypothetically — better suited (if ever cleared) to a blog/journal post *about* the event than to persistent product UI, given how many people are individually identifiable
- **Classification:** Not recommended (rights + consent-at-scale)

---

## Summary table

| # | File (short) | Dimensions | People | Strongest hypothetical use | Blocking issues |
|---|---|---|---|---|---|
| 1 | 222F833F | 1336×2004 | 3 | Education (weak) | watermark, branding, busy crop |
| 2 | 29D722FA | 1706×2560 | 2 | How It Works — Collect | watermark |
| 3 | 2B024E0F | 988×1482 | 1 | **Hero / CTA (strongest overall)** | watermark |
| 4 | 6998FABD | 1706×2560 | 4 | CTA / About | watermark, partial branding |
| 5 | 6FDFC0A8 | 1138×1706 | 1 (+2 bg) | How It Works — Collect | watermark |
| 6 | 74899A6D | 1706×2560 | 1 | About (weak, blocked hardest) | watermark, **clear branding** |
| 7 | 7E341FE4 | 1526×2288 | 1 | Education | watermark |
| 8 | 90FC8C6A | 1706×2560 | 1 | How It Works — Collect | watermark |
| 9 | 9878C8D2 | 1706×2560 | 1 | **Impact/Mission (2nd strongest)** | watermark, partial branding |
| 10 | 99C0E15A | 1138×1706 | 9 | Impact/Mission | watermark, consent-at-scale |
| 11 | A4BF57E0 | 1354×2032 | 1 | None | watermark, branding, **visible blade** |
| 12 | D47662EC | 1706×2560 | 1 (+1 bg) | **Impact/Mission (tied 2nd)** | watermark, **clear branding** |
| 13 | EF879AD2 | 1050×1574 | 25+ | None (better as editorial, not UI) | watermark, consent-at-scale |

**Approved for immediate use: 0 of 13.**

## What would need to be true to revisit this

1. Explicit permission from the photographer (@edward.wonder / TikTok) to use these specific images commercially on Trash2Cash, ideally in writing. **Resolved** — user confirmed.
2. A resolved answer on the "Lagos State Government" / "Pitstop Lagos" branding visible in most shots. **Resolved** — user confirmed the affiliation shown is accurate.
3. For image 13, and to a lesser extent image 10: a decision on whether posing 9–25+ identifiable strangers on product UI without documented consent is acceptable. **Not used** — neither made the final cut anyway (both were rated weaker candidates on composition grounds before this question even came up), so this was sidestepped rather than explicitly resolved. Revisit if either is wanted later.

## Images used

Three images were approved, cropped, and placed. All crops are pure geometric cuts (no content-aware fill, no AI editing) that remove the TikTok watermark entirely — verified by viewing each cropped result before resizing.

| Source | Crop | Web files | Placement |
|---|---|---|---|
| #3 `2B024E0F` (988×1482) | 0,0 → 70% × 90% → 691×1333 | `sweep-action-420.webp`, `sweep-action-691.webp` | Home — "Recycling starts with real work" section, main collage image |
| #9 `9878C8D2` (1706×2560) | 0,0 → 72% × 92% → 1228×2355 | `wheelbarrow-smile-{420,720,1000}.webp` | Home — same section, smaller overlapping accent image |
| #12 `D47662EC` (1706×2560) | 0,0 → 74% × 92% → 1262×2355 | `wheelbarrow-collect-{420,720,1000}.webp` | About — "The problem" section, single contained image with caption |

Every `<img>` ships `width`/`height` attributes matching its true intrinsic ratio (layout-shift prevention), a `srcset` across the generated sizes, and `loading="lazy"` (both placements are below the fold). Total footprint: 8 files, 652 KB combined — see the performance section of `docs/MOBILE_UX_AUDIT.md` for the full accounting.

The other 10 images remain in `assets/`, unused, available if a future pass wants them (images 2, 5, 7, 8 are the next-best candidates per the per-image notes above; image 11's visible blade and images 10/13's crowd-consent question make them the least suitable regardless of rights).
