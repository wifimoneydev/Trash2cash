"""Business-logic regression tests, imported through project.py the way
the original CS50 submission's test file did.

V2 contract change: calculate_reward()/get_material() now take a
canonical material id (e.g. "pet_bottles") from the V2 material
catalogue, not a broad string like "Plastic (PET bottles)". The old
get_rate_range() (an averaged min/max tuple) is gone — materials now
have one rate_per_kg each. See docs/T2C_V2_SPECIFICATION.md section 4
and docs/T2C_V2_IMPLEMENTATION.md for the full before/after.
"""

from project import calculate_reward, get_material, get_rate_per_kg, get_locations


def test_get_rate_per_kg():
    assert get_rate_per_kg("pet_bottles") == 200
    assert get_rate_per_kg("aluminium_cans") == 500
    assert get_rate_per_kg("unknown_material") is None


def test_calculate_reward():
    assert calculate_reward("pet_bottles", 2) == 400.0
    assert calculate_reward("pure_water_sachets", 1.5) == 90.0
    assert calculate_reward("unknown_material", 5) == 0


def test_get_material():
    pet = get_material("pet_bottles")
    assert pet["name"] == "PET Bottles"
    assert pet["category_id"] == "rigid_plastics"
    assert get_material("unknown_material") is None


def test_get_locations():
    assert "Ikeja" in get_locations("Lagos")
    assert "Wuse" in get_locations("Abuja")
    assert get_locations("Unknown") == []
