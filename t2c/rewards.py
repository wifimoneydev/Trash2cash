"""V2 reward engine.

Computes an estimated reward for a specific catalogue material (by
canonical material id) and a weight in kg. All rate data comes from
t2c.materials — this module contains no hardcoded prices of its own,
and nothing else in the codebase should either. The API, the
calculator UI, Ask T2C, and the local chatbot fallback all call into
this module (or t2c.materials directly) rather than keeping their own
copy of a rate.

V2 contract change from V1: V1's calculate_reward()/normalize_material()
took a loose material string ("plastic", "nylon", "aluminum") and
returned an averaged (min, max) range. V2 works against specific
catalogue material ids (e.g. "pet_bottles") and a single rate_per_kg —
see docs/T2C_V2_SPECIFICATION.md section 4 and
docs/T2C_V2_IMPLEMENTATION.md for the full before/after.
"""

from t2c.materials import get_material


def get_rate_per_kg(material_id):
    """Return the reference rate (Naira/kg) for a material id, or None
    if the material doesn't exist or doesn't currently have a rate."""
    material = get_material(material_id)
    if material is None:
        return None
    return material.get("rate_per_kg")


def calculate_reward(material_id, weight):
    """Calculate the estimated reward for a catalogue material id and
    a weight in kg.

    Fails cleanly rather than raising: an unknown material id, a
    material with no rate yet, a non-numeric weight, or a non-positive
    weight all yield a reward of 0 instead of an exception or an
    invented number.
    """
    rate = get_rate_per_kg(material_id)
    if rate is None:
        return 0

    try:
        weight = float(weight)
    except (TypeError, ValueError):
        return 0

    if weight <= 0:
        return 0

    return rate * weight
