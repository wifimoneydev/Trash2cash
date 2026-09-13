"""OpenAI-powered Trash2Cash assistant, grounded in t2c business logic.

get_assistant_response() is the single entrypoint the Flask app calls.
It tries OpenAI first (intent extraction -> grounded tool call ->
natural-language phrasing, fact-checked against the tool's verified
output), and falls back to the existing local Naive Bayes chatbot on
any failure: missing key, network error, timeout, rate limit, or
malformed structured output. This function never raises — the caller
always gets a usable response, plus a "mode" flag saying which path
produced it (openai vs local_fallback), for tests/logging only.
"""

import re

from t2c.chatbot.chatbot import get_bot_response
from .client import get_client, DEFAULT_MODEL
from .schema import parse_intent, SCHEMA_DESCRIPTION
from .tools import reward_tool, location_tool, material_info_tool, faq_tool, unsupported_tool

MAX_HISTORY_TURNS = 3

SYSTEM_PROMPT = (
    "You are an intent-extraction component for the Trash2Cash recycling "
    f"assistant in Nigeria. {SCHEMA_DESCRIPTION}"
)

PHRASING_SYSTEM_PROMPT = (
    "You are the Trash2Cash assistant, a friendly recycling helper for "
    "Nigeria. You will be given a VERIFIED FACT that has already been "
    "looked up from Trash2Cash's own confirmed records — treat it as "
    "certain, current, and authoritative, not as something you're unsure "
    "about. Restate it naturally and concisely for the user, including "
    "every number/rate/name it contains exactly as given — do not round, "
    "omit, hedge on, or refuse to state any number that is in the "
    "verified fact. Light, natural Nigerian English is fine if the user "
    "used it, but don't overdo slang. Do NOT add any number, rate, "
    "address, or material that is NOT in the verified fact. If the fact "
    "itself says something isn't available, say that plainly."
)

_NUMBER_RE = re.compile(r"\d[\d,]*\.?\d*")


def _history_to_prompt(history):
    if not history:
        return ""
    lines = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        if turn.get("message"):
            lines.append(f"Earlier: \"{turn['message']}\" (material discussed: {turn.get('material') or 'none'})")
    return "\n".join(lines)


def _extract_intent(client, message, history):
    context = _history_to_prompt(history)
    user_prompt = f"{context}\nUser: {message}" if context else message
    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=200,
    )
    return parse_intent(completion.choices[0].message.content)


def _resolve_with_session_fallback(intent_data, session):
    """Deterministic, non-LLM fill-in for ambiguous follow-ups (e.g.
    "what about 10kg?" after a plastic question): reuse the last
    resolved material/location from this session rather than asking the
    LLM to guess. Never invents a value that wasn't actually said
    earlier in this same session."""
    if session is None:
        return intent_data
    resolved = dict(intent_data)
    if resolved["intent"] == "reward_estimate" and not resolved["material"]:
        last_material = session.get("t2c_last_material")
        if last_material:
            resolved["material"] = last_material
    if resolved["intent"] == "location_lookup" and not resolved["location"]:
        last_location = session.get("t2c_last_location")
        if last_location:
            resolved["location"] = last_location
    return resolved


def _remember(intent_data, session):
    if session is None:
        return
    if intent_data.get("material"):
        session["t2c_last_material"] = intent_data["material"]
    if intent_data.get("location"):
        session["t2c_last_location"] = intent_data["location"]
    history = list(session.get("t2c_history") or [])
    history.append({"message": intent_data.get("question", ""), "material": intent_data.get("material")})
    session["t2c_history"] = history[-MAX_HISTORY_TURNS:]


def _run_tool(intent_data):
    intent = intent_data["intent"]
    if intent == "reward_estimate":
        return reward_tool(intent_data["material"], intent_data["weight_kg"])
    if intent == "location_lookup":
        return location_tool(intent_data["location"])
    if intent == "material_info":
        return material_info_tool(intent_data["material"])
    if intent == "general_help":
        return faq_tool()
    return unsupported_tool()


def _contains_only_known_numbers(text, fact):
    """Safety net: the phrased response must not introduce any number
    that isn't already present in the verified fact string — guards
    against the phrasing pass inventing a rate, weight, or reward."""
    fact_numbers = set(_NUMBER_RE.findall(fact))
    response_numbers = set(_NUMBER_RE.findall(text))
    return response_numbers.issubset(fact_numbers)


def _phrase_naturally(client, message, fact):
    try:
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": PHRASING_SYSTEM_PROMPT},
                {"role": "user", "content": f"User asked: {message}\nVerified fact: {fact}"},
            ],
            temperature=0.4,
            max_tokens=150,
        )
        phrased = (completion.choices[0].message.content or "").strip()
        if phrased and _contains_only_known_numbers(phrased, fact):
            return phrased
    except Exception:
        pass
    return fact  # deterministic, always-grounded fallback text


def get_assistant_response(message, session=None, client=None):
    """Single entrypoint for the /chat route.

    Always returns {"response": str, "mode": "openai" | "local_fallback"}.
    Never raises: any failure in the OpenAI path (missing key, auth
    error, timeout, rate limit, malformed JSON, network error) falls
    back to the local classifier instead of surfacing a raw error.
    """
    if client is None:
        client = get_client()

    if client is not None:
        try:
            history = session.get("t2c_history") if session is not None else None
            intent_data = _extract_intent(client, message, history)
            intent_data = _resolve_with_session_fallback(intent_data, session)
            tool_result = _run_tool(intent_data)
            response_text = _phrase_naturally(client, message, tool_result["fact"])
            _remember(intent_data, session)
            return {"response": response_text, "mode": "openai"}
        except Exception:
            pass  # any failure at all -> safe local fallback below

    return {"response": get_bot_response(message), "mode": "local_fallback"}
