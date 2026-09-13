"""Tests for the OpenAI-powered assistant. OpenAI itself is always
mocked here — these tests run without a real API key or network access,
and must stay deterministic regardless of whether a real key happens to
be configured in the environment running the suite."""

import json

from t2c.assistant.assistant import get_assistant_response, _run_tool
from t2c.assistant.schema import parse_intent, IntentParseError
from t2c.rewards import calculate_reward, RATES
from t2c.chatbot.chatbot import FALLBACK_RESPONSE


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class FakeClient:
    """Stands in for openai.OpenAI. The intent-extraction call always
    passes response_format={"type": "json_object"}; the phrasing call
    doesn't — used here to tell the two calls apart without depending
    on call order."""

    def __init__(self, intent_json, phrase_text=None, raise_on_intent=None, raise_on_phrase=None):
        self.intent_json = intent_json
        self.phrase_text = phrase_text
        self.raise_on_intent = raise_on_intent
        self.raise_on_phrase = raise_on_phrase
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        if kwargs.get("response_format"):
            if self.raise_on_intent:
                raise self.raise_on_intent
            return _FakeCompletion(self.intent_json)
        if self.raise_on_phrase:
            raise self.raise_on_phrase
        if self.phrase_text is not None:
            return _FakeCompletion(self.phrase_text)
        # Default: echo the verified fact back, like a well-behaved model would.
        user_content = kwargs["messages"][-1]["content"]
        fact = user_content.split("Verified fact: ", 1)[-1]
        return _FakeCompletion(fact)


def intent_payload(**overrides):
    payload = {"intent": "unsupported", "material": None, "weight_kg": None, "location": None, "question": ""}
    payload.update(overrides)
    return json.dumps(payload)


def test_openai_reward_intent():
    client = FakeClient(intent_payload(intent="reward_estimate", material="aluminum", weight_kg=5))
    result = get_assistant_response("How much for 5kg of aluminum?", client=client)
    assert result["mode"] == "openai"
    expected = calculate_reward("aluminum", 5)
    assert f"{expected:.2f}" in result["response"]


def test_openai_location_intent_no_fabricated_address():
    client = FakeClient(intent_payload(intent="location_lookup", location="Ikeja"))
    result = get_assistant_response("Where can I recycle in Ikeja?", client=client)
    assert result["mode"] == "openai"
    assert "Ikeja" in result["response"]
    assert "Lagos" in result["response"]
    # honesty about missing address data, not a fabricated street address
    assert "address" in result["response"].lower()


def test_openai_material_intent():
    client = FakeClient(intent_payload(intent="material_info", material="plastic"))
    result = get_assistant_response("Do you accept plastic?", client=client)
    assert result["mode"] == "openai"
    lo, hi = RATES["Plastic (PET bottles)"]
    assert f"{lo}" in result["response"] and f"{hi}" in result["response"]


def test_unsupported_material_is_rejected_cleanly():
    client = FakeClient(intent_payload(intent="material_info", material="glass"))
    result = get_assistant_response("Do you accept glass?", client=client)
    assert result["mode"] == "openai"
    assert "not currently listed" in result["response"] or "not currently" in result["response"]
    # never silently invents glass as an accepted material
    assert "glass is accepted" not in result["response"].lower()


def test_invalid_structured_output_falls_back_locally():
    client = FakeClient(intent_json="not valid json at all")
    result = get_assistant_response("Hello", client=client)
    assert result["mode"] == "local_fallback"
    assert result["response"]  # still a real, non-crashing response


def test_openai_failure_falls_back_to_local():
    client = FakeClient(intent_payload(), raise_on_intent=TimeoutError("simulated timeout"))
    result = get_assistant_response("Hello", client=client)
    assert result["mode"] == "local_fallback"
    assert result["response"]


def test_missing_key_falls_back_to_local(monkeypatch):
    import t2c.assistant.assistant as assistant_module
    monkeypatch.setattr(assistant_module, "get_client", lambda: None)
    result = get_assistant_response("Hello")
    assert result["mode"] == "local_fallback"
    assert result["response"]


def test_reward_values_come_from_shared_module_not_the_llm():
    client = FakeClient(intent_payload(intent="reward_estimate", material="nylon", weight_kg=7))
    result = get_assistant_response("I have 7 kilos of nylon", client=client)
    tool_result = _run_tool(parse_intent(intent_payload(intent="reward_estimate", material="nylon", weight_kg=7)))
    assert tool_result["data"]["reward"] == calculate_reward("nylon", 7)
    assert f"{tool_result['data']['reward']:.2f}" in result["response"]


def test_phrasing_cannot_inject_a_fabricated_number():
    """If the phrasing pass hallucinates a number that isn't in the
    verified fact, the safety net discards it and uses the exact fact
    text instead."""
    client = FakeClient(
        intent_payload(intent="location_lookup", location="Ikeja"),
        phrase_text="Sure! Our confirmed outlet is at 123 Main Street.",
    )
    result = get_assistant_response("Where can I recycle in Ikeja?", client=client)
    assert "123" not in result["response"]
    assert "Ikeja" in result["response"]


def test_conversation_follow_up_reuses_last_material():
    session = {}
    client = FakeClient(intent_payload(intent="reward_estimate", material="plastic", weight_kg=5))
    first = get_assistant_response("How much for 5kg plastic?", session=session, client=client)
    assert "Plastic" in first["response"]

    # Follow-up mentions only a new weight, no material.
    client2 = FakeClient(intent_payload(intent="reward_estimate", material=None, weight_kg=10))
    second = get_assistant_response("What about 10kg?", session=session, client=client2)
    expected = calculate_reward("plastic", 10)
    assert f"{expected:.2f}" in second["response"]


def test_mode_indicator_present_in_both_paths(monkeypatch):
    client = FakeClient(intent_payload(intent="general_help"))
    openai_result = get_assistant_response("How does this work?", client=client)
    assert openai_result["mode"] == "openai"

    import t2c.assistant.assistant as assistant_module
    monkeypatch.setattr(assistant_module, "get_client", lambda: None)
    local_result = get_assistant_response("How does this work?")
    assert local_result["mode"] == "local_fallback"


def test_invalid_intent_value_falls_back_safely():
    with_bad_intent = json.dumps({"intent": "delete_everything", "material": None, "weight_kg": None, "location": None, "question": ""})
    client = FakeClient(with_bad_intent)
    result = get_assistant_response("Hello", client=client)
    assert result["mode"] == "local_fallback"


def test_parse_intent_rejects_non_dict_and_bad_types():
    import pytest
    with pytest.raises(IntentParseError):
        parse_intent("[1, 2, 3]")
    with pytest.raises(IntentParseError):
        parse_intent(json.dumps({"intent": "reward_estimate", "material": 5, "weight_kg": None, "location": None, "question": ""}))
    with pytest.raises(IntentParseError):
        parse_intent(json.dumps({"intent": "reward_estimate", "material": None, "weight_kg": "five", "location": None, "question": ""}))
