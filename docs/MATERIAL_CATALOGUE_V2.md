# Material Catalogue V2 — Data Documentation

This document records, for every material in the V2 catalogue, exactly what kind of data it is: a reference figure, a placeholder baseline, or an explicit assumption. Nothing here is presented as more verified than it actually is.

**Single source of truth:** `t2c/materials.py`. Every other system (reward engine, API, Materials page, Ask T2C, local chatbot fallback) reads from that module. This document explains the data it contains; it does not duplicate the data itself.

## Rate status definitions

- **reference** — a figure Trash2Cash is reasonably confident represents a fair current estimate.
- **placeholder** — a baseline figure used so the product works end-to-end, explicitly not yet verified against real recycler pricing.

Neither status means "live market price." See the in-product disclaimer (`t2c.materials.RATE_DISCLAIMER`): *"Reference estimate only. Actual recycler rates may vary by location, material condition and current market price."*

## Categories (3)

| Category id | Name |
|---|---|
| `rigid_plastics` | Rigid Plastics |
| `flexible_plastics` | Flexible Plastics (Nylon) |
| `metals` | Metals |

The "Flexible Plastics (Nylon)" name deliberately keeps the familiar Nigerian term in the user-facing label while each material underneath it records its real technical family (`Flexible PE recycling stream`), not the polymer "nylon" (polyamide) — see `docs/T2C_V2_SPECIFICATION.md` section 2.

## Materials (7)

### Rigid Plastics

| Field | PET Bottles | HDPE Containers | Other Accepted Rigid Plastics |
|---|---|---|---|
| id | `pet_bottles` | `hdpe_containers` | `other_rigid_plastics` |
| Rate | ₦200/kg | ₦120/kg | ₦120/kg |
| Rate status | **reference** | **placeholder** | **placeholder** |
| Acceptance | accepted | accepted | accepted (selected items only) |
| Technical family | PET | HDPE | Mixed (e.g. PP) |
| Provenance | Supplied directly as the authoritative initial rate. | Baseline figure; not yet checked against real recycler pricing — flagged in `notes`. | Baseline figure; this is a catch-all category, not every rigid plastic object — flagged in `description` and `notes`. |

### Flexible Plastics (Nylon)

| Field | Pure Water Sachets | Shopping / Carrier Bags | Clean Packaging Film |
|---|---|---|---|
| id | `pure_water_sachets` | `shopping_bags` | `packaging_film` |
| Rate | ₦60/kg | ₦60/kg | ₦60/kg |
| Rate status | **reference** | **placeholder** | **placeholder** |
| Acceptance | accepted | accepted (selected compositions only) | accepted (selected film only) |
| Technical family | Flexible PE recycling stream | Flexible PE recycling stream | Flexible PE recycling stream |
| Provenance | Supplied directly as the authoritative initial rate. | Baseline figure — not every shopping bag composition is accepted. | Baseline figure — multilayer/non-PE film and most food wrappers are explicitly NOT covered by this entry. |

### Metals

| Field | Aluminium Beverage Cans |
|---|---|
| id | `aluminium_cans` |
| Rate | ₦500/kg |
| Rate status | **reference** |
| Acceptance | accepted |
| Technical family | Aluminium (non-ferrous metal) |
| Provenance | Supplied directly as the authoritative initial rate. |

## Acceptance status vocabulary

The architecture (`t2c/materials.py`) defines five acceptance statuses:

- `accepted`
- `selected_locations`
- `rate_unavailable`
- `not_currently_accepted`
- `needs_identification`

**All 7 initial materials use `accepted`.** The other four exist for future materials where a narrower status has real backing data — none of the current seven need one, and none is assigned speculatively.

## Location relationships

Every material's `supported_location_ids` is `["Lagos", "Abuja"]` — the two cities `t2c/locations.py` already covers. This is an honest default, not a verified per-material partnership: there is no data distinguishing "this material is accepted in Lagos but not Abuja," so no such distinction is invented. If that data ever exists for a specific material, its `supported_location_ids` should be narrowed accordingly and its `acceptance_status` likely moved to `selected_locations`.

Location **records themselves** (the actual LGA list) are unchanged from V1 — `t2c/locations.py` was not modified. No address, coordinate, phone number, or outlet name has been added for any location, for any material.

## Materials explicitly NOT included

Per the specification's own guardrail: copper, brass, steel, iron, e-waste, batteries, and glass are not in the V2 catalogue. They are not "not accepted" in a verified sense either — they are simply not yet researched. Ask T2C and the Materials page both treat an unrecognized material as "not confident this matches verified data," not as a confirmed rejection, and never fabricate a rate for any of them.

## Assumptions made explicit

- `rate_source` for every material is `"Trash2Cash reference rate table"` — i.e., these are the exact figures supplied in the V2 specification, not independently sourced.
- `rate_source_date` and `last_verified` are both set to 2026-10-05, the date the V2 catalogue was authored. Neither implies an external market check occurred on that date — it marks when these specific figures were set as Trash2Cash's own reference table.
- `notes` is populated only where there's something a reader should know beyond the rate/status fields (e.g. "this is a catch-all category"). It is `None` where there's nothing further to flag.
