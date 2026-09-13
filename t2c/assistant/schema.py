"""Structured intent schema for the OpenAI-powered assistant.

OpenAI is asked to return JSON matching this shape. We never trust it
blindly — parse_intent() validates every field before anything is
passed to a business-logic tool.
"""

import json

ALLOWED_INTENTS = {
    "reward_estimate",
    "location_lookup",
    "material_info",
    "general_help",
    "unsupported",
}

SCHEMA_DESCRIPTION = """\
Return ONLY a JSON object with exactly these keys:
{
  "intent": one of "reward_estimate", "location_lookup", "material_info", "general_help", "unsupported",
  "material": a material name mentioned by the user, or null,
  "weight_kg": a number (kg) mentioned by the user, or null,
  "location": a city or area name mentioned by the user, or null,
  "question": a short restatement of what the user is asking, for logging
}
Do not include any other text, explanation, or markdown — only the JSON object.
Do not invent a material, weight, or location the user didn't mention.

Guidance:
- Any question about pricing, payout, rates, or "how much" is
  "reward_estimate" — even a general "what are your rates?" with no
  specific material or weight (leave those fields null in that case).
- A question about whether a specific material/waste type is accepted
  (without asking for a price) is "material_info".
- A question about where to drop off, collect, or find a location is
  "location_lookup".
- A general "how does this work" / "what is Trash2Cash" question is
  "general_help".
- Anything unrelated to recycling, rewards, or Trash2Cash is "unsupported".
"""


class IntentParseError(Exception):
    """Raised when OpenAI's output doesn't match the expected schema."""


def parse_intent(raw_text):
    """Parse and validate OpenAI's structured output.

    Raises IntentParseError on anything that doesn't match the schema —
    callers must treat that as "fall back safely", never crash.
    """
    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise IntentParseError(f"Model output was not valid JSON: {e}")

    if not isinstance(data, dict):
        raise IntentParseError("Model output was not a JSON object")

    intent = data.get("intent")
    if intent not in ALLOWED_INTENTS:
        raise IntentParseError(f"Unknown or missing intent: {intent!r}")

    material = data.get("material")
    if material is not None and not isinstance(material, str):
        raise IntentParseError(f"material must be a string or null, got {material!r}")

    weight_kg = data.get("weight_kg")
    if weight_kg is not None:
        if isinstance(weight_kg, bool) or not isinstance(weight_kg, (int, float)):
            raise IntentParseError(f"weight_kg must be a number or null, got {weight_kg!r}")

    location = data.get("location")
    if location is not None and not isinstance(location, str):
        raise IntentParseError(f"location must be a string or null, got {location!r}")

    question = data.get("question")
    if not isinstance(question, str):
        question = ""

    return {
        "intent": intent,
        "material": material,
        "weight_kg": weight_kg,
        "location": location,
        "question": question,
    }
