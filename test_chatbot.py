from t2c.chatbot.chatbot import get_bot_response, classify, FALLBACK_RESPONSE, CONFIDENCE_THRESHOLD
from t2c.rewards import RATES


def test_correct_intent_classification():
    assert get_bot_response("Hello") != FALLBACK_RESPONSE
    assert get_bot_response("Bye") == "Goodbye! Thanks for helping the planet with Trash2Cash."


def test_low_confidence_triggers_fallback():
    tag, confidence = classify("asdkjfh qqzxw random gibberish")
    assert confidence < CONFIDENCE_THRESHOLD
    assert get_bot_response("asdkjfh qqzxw random gibberish") == FALLBACK_RESPONSE


def test_ood_queries_do_not_get_a_confident_wrong_answer():
    """These are unrelated to Trash2Cash. Either fallback is returned, or
    a low-confidence match — never treated as certain."""
    for text in ["what's the weather like today", "tell me a joke", "sing me a song"]:
        tag, confidence = classify(text)
        response = get_bot_response(text)
        if response != FALLBACK_RESPONSE:
            # If it wasn't rejected, it must at least be a legitimate,
            # deliberately low-confidence borderline case, not silently
            # treated as certain.
            assert confidence < 0.6


def test_reward_intent_uses_shared_rate_table():
    response = get_bot_response("What are the rates?")
    for material, (lo, hi) in RATES.items():
        assert material in response
        assert f"₦{lo}-₦{hi}/kg" in response


def test_location_intent_responds():
    response = get_bot_response("Where can I drop off trash?")
    assert response != FALLBACK_RESPONSE


def test_accepted_materials_intent_responds():
    response = get_bot_response("What types of plastic do you accept?")
    assert response != FALLBACK_RESPONSE
    assert "PET" in response or "HDPE" in response
