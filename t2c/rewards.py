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


def get_rate_range(material):
    """Return the (min, max) rate range in Naira/kg for a given material."""
    return RATES.get(material, (0, 0))


def calculate_reward(material, weight):
    """Calculate reward based on material and weight."""
    material_lower = material.lower()
    for key, (min_rate, max_rate) in RATES.items():
        if material_lower in key.lower():
            return (min_rate + max_rate) / 2 * float(weight)
    return 0
