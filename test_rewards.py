from t2c.rewards import calculate_reward, get_rate_per_kg
from t2c.materials import MATERIALS, get_material


def test_rate_lookup_known_material():
    assert get_rate_per_kg("pet_bottles") == 200
    assert get_rate_per_kg("pure_water_sachets") == 60
    assert get_rate_per_kg("aluminium_cans") == 500


def test_rate_lookup_unknown_material_is_none_not_invented():
    assert get_rate_per_kg("glass_jars") is None
    assert get_rate_per_kg("") is None
    assert get_rate_per_kg(None) is None


def test_calculate_reward_matches_rate_times_weight():
    assert calculate_reward("pet_bottles", 2) == 400.0
    assert calculate_reward("pure_water_sachets", 1.5) == 90.0
    assert calculate_reward("aluminium_cans", 3) == 1500.0


def test_unsupported_material_fails_cleanly_not_invented():
    assert calculate_reward("glass_jars", 5) == 0
    assert calculate_reward("", 5) == 0
    assert calculate_reward(None, 5) == 0


def test_non_numeric_weight_fails_cleanly():
    assert calculate_reward("pet_bottles", "abc") == 0
    assert calculate_reward("pet_bottles", None) == 0
    assert calculate_reward("pet_bottles", "") == 0


def test_boundary_weights():
    assert calculate_reward("pet_bottles", 0) == 0
    assert calculate_reward("pet_bottles", -5) == 0
    assert calculate_reward("pet_bottles", 0.001) > 0


def test_every_catalogue_material_has_a_positive_rate():
    """All 7 initial materials ship with a real numeric rate — none are
    in a rate_unavailable state yet, so none should silently compute to 0
    for a valid positive weight."""
    for material in MATERIALS:
        reward = calculate_reward(material["id"], 1)
        assert reward == material["rate_per_kg"], material["id"]


def test_rate_status_is_either_reference_or_placeholder_never_unlabeled():
    for material in MATERIALS:
        assert material["rate_status"] in ("reference", "placeholder")


def test_get_material_returns_full_record_for_known_id():
    material = get_material("pet_bottles")
    assert material["name"] == "PET Bottles"
    assert material["category_id"] == "rigid_plastics"


def test_get_material_returns_none_for_unknown_id():
    assert get_material("glass_jars") is None
