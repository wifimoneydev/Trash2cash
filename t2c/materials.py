"""Canonical V2 material catalogue.

This is the single source of truth for material categories, material
types, aliases, acceptance status, reference rates, and preparation
guidance. Every other system — the reward calculator/API, the
Materials page, Ask T2C, and the Drop-off Finder — reads from this
module. None of them keep their own copy of a rate or an acceptance
decision.

Rate honesty note: rates below are either "reference" (a figure T2C is
reasonably confident represents a fair current estimate) or
"placeholder" (a baseline figure used so the product works end-to-end,
explicitly not yet verified against real recycler pricing). Neither is
a live market feed. See docs/T2C_V2_SPECIFICATION.md section 5 for the
disclaimer this status drives in the UI, and
docs/MATERIAL_CATALOGUE_V2.md for the full per-material data provenance
notes.
"""

from datetime import date

# ---------------------------------------------------------------------------
# Acceptance statuses
# ---------------------------------------------------------------------------
# The architecture supports all five; only ACCEPTED is used by the initial
# seven materials below, because no material/location pair currently has
# data distinguishing a narrower status. The other four exist so a future
# material can be added honestly rather than forcing it into ACCEPTED.

ACCEPTED = "accepted"
SELECTED_LOCATIONS = "selected_locations"
RATE_UNAVAILABLE = "rate_unavailable"
NOT_CURRENTLY_ACCEPTED = "not_currently_accepted"
NEEDS_IDENTIFICATION = "needs_identification"

ACCEPTANCE_STATUSES = {
    ACCEPTED,
    SELECTED_LOCATIONS,
    RATE_UNAVAILABLE,
    NOT_CURRENTLY_ACCEPTED,
    NEEDS_IDENTIFICATION,
}

# ---------------------------------------------------------------------------
# Rate statuses
# ---------------------------------------------------------------------------

RATE_REFERENCE = "reference"
RATE_PLACEHOLDER = "placeholder"

RATE_DISCLAIMER = (
    "Reference estimate only. Actual recycler rates may vary by location, "
    "material condition and current market price."
)

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"id": "rigid_plastics", "name": "Rigid Plastics"},
    {"id": "flexible_plastics", "name": "Flexible Plastics (Nylon)"},
    {"id": "metals", "name": "Metals"},
]

_RATE_SOURCE = "Trash2Cash reference rate table"
_RATE_SOURCE_DATE = date(2026, 10, 5)

# ---------------------------------------------------------------------------
# Materials — the 7 initial V2 catalogue entries
# ---------------------------------------------------------------------------

MATERIALS = [
    # --- Rigid Plastics ----------------------------------------------------
    {
        "id": "pet_bottles",
        "slug": "pet-bottles",
        "name": "PET Bottles",
        "category_id": "rigid_plastics",
        "technical_family": "PET (Polyethylene Terephthalate)",
        "description": "Water bottles, Coke/Fanta and other soft-drink bottles, and similar PET beverage bottles.",
        "aliases": [
            "pet", "pet bottle", "pet bottles", "plastic bottle", "plastic bottles",
            "water bottle", "water bottles", "coke bottle", "fanta bottle",
            "soft drink bottle", "beverage bottle",
        ],
        "examples": ["Water bottles", "Coke/Fanta bottles", "Other PET beverage bottles"],
        "preparation": [
            "Empty contents",
            "Reasonably clean",
            "Keep separate from unrelated waste",
            "Dry where practical",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 200,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_REFERENCE,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": None,
        "supported_location_ids": ["Lagos", "Abuja"],
    },
    {
        "id": "hdpe_containers",
        "slug": "hdpe-containers",
        "name": "HDPE Containers",
        "category_id": "rigid_plastics",
        "technical_family": "HDPE (High-Density Polyethylene)",
        "description": "Detergent bottles, bleach containers, plastic kegs/jerrycans, and selected household or personal-care containers.",
        "aliases": [
            "detergent bottle", "detergent bottles", "bleach bottle", "bleach bottles",
            "plastic keg", "plastic kegs", "jerrycan", "jerrycans", "jerry can", "jerry cans",
            "hdpe container", "hdpe containers", "hdpe bottle", "hdpe bottles", "hdpe",
        ],
        "examples": ["Detergent bottles", "Bleach containers", "Plastic kegs/jerrycans"],
        "preparation": [
            "Empty contents",
            "Reasonably clean",
            "Keep separate from unrelated waste",
            "Dry where practical",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 120,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_PLACEHOLDER,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": "Placeholder/reference baseline rate — not yet verified against real recycler pricing.",
        "supported_location_ids": ["Lagos", "Abuja"],
    },
    {
        "id": "other_rigid_plastics",
        "slug": "other-rigid-plastics",
        "name": "Other Accepted Rigid Plastics",
        "category_id": "rigid_plastics",
        "technical_family": "Mixed rigid plastics (e.g. PP and similar resins)",
        "description": "Selected PP containers, plastic bowls, selected buckets, selected lids/caps, and similar accepted hard plastics. Not every rigid plastic object is automatically accepted — ask T2C if unsure.",
        "aliases": [
            "pp container", "pp containers", "plastic bowl", "plastic bowls",
            "bucket", "buckets", "plastic lid", "plastic lids", "plastic cap", "plastic caps",
            "rigid plastic", "hard plastic",
        ],
        "examples": ["Selected PP containers", "Plastic bowls", "Selected buckets", "Selected lids/caps"],
        "preparation": [
            "Empty contents",
            "Reasonably clean",
            "Keep separate from unrelated waste",
            "Dry where practical",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 120,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_PLACEHOLDER,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": "Catch-all category — placeholder/reference baseline rate. Acceptance is for selected items only, not every rigid plastic object.",
        "supported_location_ids": ["Lagos", "Abuja"],
    },

    # --- Flexible Plastics (Nylon) ------------------------------------------
    {
        "id": "pure_water_sachets",
        "slug": "pure-water-sachets",
        "name": "Pure Water Sachets",
        "category_id": "flexible_plastics",
        "technical_family": "Flexible PE recycling stream",
        "description": "Used drinking-water sachets ('pure water').",
        "aliases": [
            "pure water nylon", "water nylon", "pure water sachet", "pure water sachets",
            "water sachet", "water sachets", "sachet water", "sachet water nylon", "sachet", "sachets",
        ],
        "examples": ["Used drinking-water sachets"],
        "preparation": [
            "Empty",
            "Reasonably clean",
            "Dry where practical",
            "Keep separate from unrelated waste",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 60,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_REFERENCE,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": None,
        "supported_location_ids": ["Lagos", "Abuja"],
    },
    {
        "id": "shopping_bags",
        "slug": "shopping-bags",
        "name": "Shopping / Carrier Bags",
        "category_id": "flexible_plastics",
        "technical_family": "Flexible PE recycling stream",
        "description": "Accepted polyethylene shopping/carrier bags. Not every shopping bag composition is accepted.",
        "aliases": [
            "shopping bag", "shopping bags", "carrier bag", "carrier bags",
            "nylon bag", "nylon bags", "polythene bag", "polythene bags",
        ],
        "examples": ["Accepted polyethylene shopping/carrier bags"],
        "preparation": [
            "Reasonably clean",
            "Dry where practical",
            "Keep separate from unrelated waste",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 60,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_PLACEHOLDER,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": "Placeholder/reference baseline rate. Acceptance covers selected PE bag compositions only.",
        "supported_location_ids": ["Lagos", "Abuja"],
    },
    {
        "id": "packaging_film",
        "slug": "packaging-film",
        "name": "Clean Packaging Film",
        "category_id": "flexible_plastics",
        "technical_family": "Flexible PE recycling stream",
        "description": "Accepted flexible plastic packaging film and other accepted clean PE film. Not all food wrappers or multilayer packaging are recyclable.",
        "aliases": [
            "packaging film", "plastic film", "pe film", "wrapping film", "cling film",
        ],
        "examples": ["Accepted flexible plastic packaging film", "Other accepted clean PE film"],
        "preparation": [
            "Reasonably clean",
            "Dry where practical",
            "Keep separate from unrelated waste",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 60,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_PLACEHOLDER,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": "Placeholder/reference baseline rate. Multilayer/non-PE film and most food wrappers are not covered by this entry.",
        "supported_location_ids": ["Lagos", "Abuja"],
    },

    # --- Metals --------------------------------------------------------------
    {
        "id": "aluminium_cans",
        "slug": "aluminium-cans",
        "name": "Aluminium Beverage Cans",
        "category_id": "metals",
        "technical_family": "Aluminium (non-ferrous metal)",
        "description": "Soft-drink cans, malt cans, energy-drink cans, and other aluminium beverage cans.",
        "aliases": [
            # Bare "aluminium"/"aluminum" is listed explicitly (not left to
            # substring matching) because it's genuinely unambiguous here —
            # this is the only metal in the catalogue, unlike "plastic" or
            # "nylon" which name multiple materials and are deliberately
            # NOT given a single-material alias (see alias_resolver.py).
            "aluminium", "aluminum",
            "aluminium can", "aluminum can", "aluminium cans", "aluminum cans",
            "drink can", "drink cans", "beverage can", "beverage cans",
            "coke can", "fanta can", "malt can",
        ],
        "examples": ["Soft-drink cans", "Malt cans", "Energy-drink cans"],
        "preparation": [
            "Empty contents",
            "Reasonably clean",
            "Keep separate from unrelated waste",
        ],
        "acceptance_status": ACCEPTED,
        "rate_per_kg": 500,
        "rate_min": None,
        "rate_max": None,
        "rate_status": RATE_REFERENCE,
        "rate_source": _RATE_SOURCE,
        "rate_source_date": _RATE_SOURCE_DATE,
        "last_verified": _RATE_SOURCE_DATE,
        "notes": None,
        "supported_location_ids": ["Lagos", "Abuja"],
    },
]

_BY_ID = {m["id"]: m for m in MATERIALS}
_BY_SLUG = {m["slug"]: m for m in MATERIALS}
_CATEGORY_BY_ID = {c["id"]: c for c in CATEGORIES}


def list_categories():
    """Return all categories, in display order."""
    return list(CATEGORIES)


def get_category(category_id):
    """Return a category dict by id, or None."""
    return _CATEGORY_BY_ID.get(category_id)


def list_materials(category_id=None):
    """Return all materials, optionally filtered to one category."""
    if category_id is None:
        return list(MATERIALS)
    return [m for m in MATERIALS if m["category_id"] == category_id]


def get_material(material_id):
    """Return a material dict by canonical id, or None."""
    return _BY_ID.get(material_id)


def get_material_by_slug(slug):
    """Return a material dict by URL slug, or None."""
    return _BY_SLUG.get(slug)


def materials_for_location(city):
    """Return the materials whose supported_location_ids include this city."""
    return [m for m in MATERIALS if city in m["supported_location_ids"]]
