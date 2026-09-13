from t2c.rewards import calculate_reward, get_rate_range, normalize_material, RATES


def test_material_normalization_accepts_form_values_and_full_names():
    assert normalize_material("plastic") == "Plastic (PET bottles)"
    assert normalize_material("Plastic (PET bottles)") == "Plastic (PET bottles)"
    assert normalize_material("  PLASTIC  ") == "Plastic (PET bottles)"
    assert normalize_material("nylon") == "Nylon (Pure water sachets)"
    assert normalize_material("aluminum") == "Aluminum (Cans)"


def test_material_normalization_rejects_unknown_or_bad_input():
    assert normalize_material("glass") is None
    assert normalize_material("") is None
    assert normalize_material(None) is None
    assert normalize_material(123) is None


def test_invalid_material_fails_cleanly():
    assert calculate_reward("glass", 5) == 0
    assert calculate_reward("", 5) == 0
    assert calculate_reward(None, 5) == 0
    assert get_rate_range("glass") == (0, 0)


def test_non_numeric_weight_fails_cleanly():
    assert calculate_reward("plastic", "abc") == 0
    assert calculate_reward("plastic", None) == 0
    assert calculate_reward("plastic", "") == 0


def test_boundary_weights():
    assert calculate_reward("plastic", 0) == 0
    assert calculate_reward("plastic", -5) == 0
    assert calculate_reward("plastic", 0.001) > 0


def test_valid_calculation_matches_current_rates():
    lo, hi = RATES["Plastic (PET bottles)"]
    assert calculate_reward("plastic", 2) == (lo + hi) / 2 * 2


def test_chatbot_and_calculator_share_the_same_rate_table():
    """The chatbot's payout_rates response is built from t2c.rewards.RATES
    (see t2c/chatbot/chatbot.py::_payout_rates_response) — this just
    pins down that RATES itself hasn't silently changed shape."""
    for material, rate_range in RATES.items():
        assert len(rate_range) == 2
        assert rate_range[0] <= rate_range[1]
