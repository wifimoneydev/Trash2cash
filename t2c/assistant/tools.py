"""Grounded business-logic tools for the assistant.

Every fact returned here comes from t2c.rewards / t2c.locations — never
from the LLM. Each tool returns {"ok": bool, "fact": str, "data": {...}}.
`fact` is the exact, verified text the model is allowed to phrase
naturally; `data` is the raw values, for tests/logging.
"""

from t2c.rewards import RATES, normalize_material, calculate_reward, get_rate_range
from t2c.locations import LOCATIONS, find_records
from t2c.chatbot.chatbot import tag_responses, FALLBACK_RESPONSE

SUPPORTED_MATERIALS_TEXT = ", ".join(RATES.keys())
SUPPORTED_LOCATIONS_TEXT = "; ".join(
    f"{city} ({', '.join(lgas)})" for city, lgas in LOCATIONS.items()
)


def _all_rates_fact():
    parts = [f"{name}: ₦{lo}-₦{hi}/kg" for name, (lo, hi) in RATES.items()]
    return "Current rates — " + "; ".join(parts) + "."


def reward_tool(material, weight_kg):
    if material is None:
        # A general "what are the rates" question, with no specific
        # material mentioned — not an unrecognized material.
        return {
            "ok": True,
            "fact": _all_rates_fact(),
            "data": {"material": None, "recognized": None},
        }

    key = normalize_material(material)

    if key is None:
        return {
            "ok": False,
            "fact": (
                f"'{material}' isn't in our verified material list. "
                f"We currently accept: {SUPPORTED_MATERIALS_TEXT}."
            ),
            "data": {"material": material, "recognized": False},
        }

    if weight_kg is None:
        lo, hi = get_rate_range(key)
        return {
            "ok": False,
            "fact": f"{key} pays ₦{lo}-₦{hi}/kg. How many kilograms do you have, so I can estimate your reward?",
            "data": {"material": key, "recognized": True, "weight_kg": None, "rate_range": (lo, hi)},
        }

    lo, hi = get_rate_range(key)
    reward = calculate_reward(key, weight_kg)

    if weight_kg <= 0:
        fact = f"{key} pays ₦{lo}-₦{hi}/kg, but a weight of {weight_kg}kg earns ₦0 — there's no material to weigh."
    else:
        fact = (
            f"{key} pays ₦{lo}-₦{hi}/kg. For {weight_kg}kg, the estimated "
            f"reward is ₦{reward:.2f}. This is an estimate from a fixed "
            f"rate table, not a live market price."
        )

    return {
        "ok": True,
        "fact": fact,
        "data": {"material": key, "weight_kg": weight_kg, "reward": reward, "rate_range": (lo, hi)},
    }


def location_tool(location):
    if not location:
        return {
            "ok": False,
            "fact": (
                "Which city or area? We currently cover: "
                f"{SUPPORTED_LOCATIONS_TEXT}."
            ),
            "data": {"location": location, "records": []},
        }

    records = find_records(location)

    if not records:
        return {
            "ok": False,
            "fact": (
                f"We don't currently have any listed areas matching '{location}'. "
                f"We currently cover: {SUPPORTED_LOCATIONS_TEXT}."
            ),
            "data": {"location": location, "records": []},
        }

    lgas = ", ".join(r["lga"] for r in records)
    city = records[0]["city"]
    fact = (
        f"{city} — listed area(s): {lgas}. These are static reference "
        f"areas, not confirmed outlets: we don't yet have a verified "
        f"street address, coordinates, or open status for any of them."
    )
    return {"ok": True, "fact": fact, "data": {"location": location, "records": records}}


def material_info_tool(material):
    if not material:
        fact = f"We currently accept: {SUPPORTED_MATERIALS_TEXT}."
        return {"ok": True, "fact": fact, "data": {"material": None, "recognized": None}}

    key = normalize_material(material)
    if key is None:
        fact = (
            f"'{material}' is not currently listed in our verified material set. "
            f"We currently accept: {SUPPORTED_MATERIALS_TEXT}."
        )
        return {"ok": False, "fact": fact, "data": {"material": material, "recognized": False}}

    lo, hi = get_rate_range(key)
    fact = f"Yes — {key} is accepted, paying ₦{lo}-₦{hi}/kg."
    return {"ok": True, "fact": fact, "data": {"material": key, "recognized": True, "rate_range": (lo, hi)}}


def faq_tool():
    fact = tag_responses.get("how_it_works", ["Trash2Cash lets you trade recyclable materials for cash."])[0]
    return {"ok": True, "fact": fact, "data": {}}


def unsupported_tool():
    return {"ok": False, "fact": FALLBACK_RESPONSE, "data": {}}
