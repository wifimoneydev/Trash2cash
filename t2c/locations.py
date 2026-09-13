"""Single source of truth for Trash2Cash drop-off location data.

Honesty note: this is a static, hand-typed list of local government
areas, not a live directory of real drop-off points (no addresses,
coordinates, or verified outlet data exist yet).
"""

LOCATIONS = {
    "Lagos": ["Ikeja", "Surulere", "Yaba", "Lekki"],
    "Abuja": ["Garki", "Wuse", "Maitama", "Kubwa"],
}


def get_locations(state):
    """Return the list of LGA names for a given state, or [] if unknown."""
    return LOCATIONS.get(state, [])
