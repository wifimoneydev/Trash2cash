"""Single source of truth for Trash2Cash material payout rates.

These are the same values previously hardcoded in project.py. They are
static, hand-set figures — not a live/real-time feed from any market
data source.
"""

RATES = {
    "Plastic (PET bottles)": (80, 100),
    "Nylon (Pure water sachets)": (70, 200),
    "Aluminum (Cans)": (200, 500),
}


def normalize_material(material):
    """Map a user-supplied material string to its canonical RATES key.

    Accepts the HTML form's short values ("plastic", "nylon", "aluminum"),
    the full canonical names, in any case, with surrounding whitespace.
    Returns None if the material isn't recognized — this is the single
    place both the reward calculator and the chatbot rely on, so they
    can never disagree about what counts as a valid material.
    """
    if not isinstance(material, str):
        return None
    material_lower = material.strip().lower()
    if not material_lower:
        return None
    for key in RATES:
        if material_lower in key.lower():
            return key
    # Natural phrasing often names the material and a form/descriptor that
    # isn't a literal substring of the canonical key, e.g. "aluminum cans"
    # or "nylon sachets" vs. "Aluminum (Cans)" / "Nylon (Pure water
    # sachets)" — the parenthesis breaks a plain substring match even
    # though the material is unambiguous. Fall back to matching on the
    # material's head name (the word(s) before the parenthetical detail).
    for key in RATES:
        head = key.split(" (")[0].lower()
        if head in material_lower or material_lower in head:
            return key
    return None


def get_rate_range(material):
    """Return the (min, max) rate range in Naira/kg for a given material,
    or (0, 0) if the material isn't recognized."""
    key = normalize_material(material)
    return RATES.get(key, (0, 0))


def calculate_reward(material, weight):
    """Calculate reward based on material and weight.

    Fails cleanly rather than raising: an unrecognized material, a
    non-numeric weight, or a non-positive weight all yield a reward of
    0 instead of an exception or a nonsensical negative reward.
    """
    key = normalize_material(material)
    if key is None:
        return 0
    try:
        weight = float(weight)
    except (TypeError, ValueError):
        return 0
    if weight <= 0:
        return 0
    min_rate, max_rate = RATES[key]
    return (min_rate + max_rate) / 2 * weight
