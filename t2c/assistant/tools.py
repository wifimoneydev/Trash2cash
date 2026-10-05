"""Grounded business-logic tools for the assistant.

Every fact returned here comes from t2c.materials / t2c.rewards /
t2c.locations — never from the LLM. Each tool returns
{"ok": bool, "fact": str, "data": {...}}. `fact` is the exact, verified
text the model is allowed to phrase naturally; `data` is the raw
values, for tests/logging.

V2: material resolution goes through t2c.alias_resolver against the
canonical t2c.materials catalogue (7 specific materials), replacing
V1's 3-broad-bucket t2c.rewards.normalize_material(). A phrase that
doesn't confidently resolve to one material — including one that only
names a category ("any kind of nylon") or doesn't match anything at
all ("Indomie wrappers") — never receives an invented rate.
"""

from t2c.rewards import calculate_reward, get_rate_per_kg
from t2c.materials import (
    list_categories, list_materials, get_category, get_material, RATE_DISCLAIMER,
)
from t2c.alias_resolver import resolve_material_id, resolve_category_id
from t2c.locations import LOCATIONS, find_records
from t2c.chatbot.chatbot import tag_responses, FALLBACK_RESPONSE

SUPPORTED_LOCATIONS_TEXT = "; ".join(
    f"{city} ({', '.join(lgas)})" for city, lgas in LOCATIONS.items()
)


def _all_materials_text():
    return ", ".join(m["name"] for m in list_materials())


def _all_rates_fact():
    lines = []
    for category in list_categories():
        parts = [f"{m['name']}: ₦{m['rate_per_kg']}/kg" for m in list_materials(category["id"])]
        lines.append(f"{category['name']} — " + "; ".join(parts))
    return "Current reference rates by category: " + " | ".join(lines) + f". {RATE_DISCLAIMER}"


def _category_materials_fact(category_id, original_text):
    category = get_category(category_id)
    names = [m["name"] for m in list_materials(category_id)]
    return (
        f"'{original_text}' could mean a few different things — "
        f"{category['name']} covers: {', '.join(names)}. Which one do you have?"
    )


def _uncertain_material_fact(original_text):
    return (
        f"I'm not confident '{original_text}' matches a material we have "
        f"verified data for. We currently cover: {_all_materials_text()}. "
        f"You can check /materials or describe it a bit more."
    )


def reward_tool(material, weight_kg):
    if material is None:
        # A general "what are the rates" question, with no specific
        # material mentioned — not an unrecognized material.
        return {
            "ok": True,
            "fact": _all_rates_fact(),
            "data": {"material_id": None, "recognized": None},
        }

    material_id = resolve_material_id(material)

    if material_id is None:
        category_id = resolve_category_id(material)
        if category_id is not None:
            return {
                "ok": False,
                "fact": _category_materials_fact(category_id, material),
                "data": {"material_id": None, "recognized": False, "category_hint": category_id},
            }
        return {
            "ok": False,
            "fact": _uncertain_material_fact(material),
            "data": {"material_id": None, "recognized": False},
        }

    catalog_material = get_material(material_id)
    name = catalog_material["name"]
    rate = get_rate_per_kg(material_id)

    if weight_kg is None:
        return {
            "ok": False,
            "fact": f"{name} pays ₦{rate}/kg. How many kilograms do you have, so I can estimate your reward?",
            "data": {"material_id": material_id, "recognized": True, "weight_kg": None, "rate_per_kg": rate},
        }

    reward = calculate_reward(material_id, weight_kg)

    if weight_kg <= 0:
        fact = f"{name} pays ₦{rate}/kg, but a weight of {weight_kg}kg earns ₦0 — there's no material to weigh."
    else:
        fact = (
            f"{name} pays ₦{rate}/kg. For {weight_kg}kg, the estimated "
            f"reward is ₦{reward:.2f}. {RATE_DISCLAIMER}"
        )

    return {
        "ok": True,
        "fact": fact,
        "data": {"material_id": material_id, "weight_kg": weight_kg, "reward": reward, "rate_per_kg": rate},
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
        fact = f"We currently accept: {_all_materials_text()}."
        return {"ok": True, "fact": fact, "data": {"material_id": None, "recognized": None}}

    material_id = resolve_material_id(material)
    if material_id is None:
        category_id = resolve_category_id(material)
        if category_id is not None:
            return {
                "ok": False,
                "fact": _category_materials_fact(category_id, material),
                "data": {"material_id": None, "recognized": False, "category_hint": category_id},
            }
        return {
            "ok": False,
            "fact": _uncertain_material_fact(material),
            "data": {"material_id": None, "recognized": False},
        }

    catalog_material = get_material(material_id)
    rate = get_rate_per_kg(material_id)
    prep = "; ".join(catalog_material.get("preparation", []))
    fact = f"Yes — {catalog_material['name']} is accepted, paying ₦{rate}/kg. Preparation: {prep}."
    return {
        "ok": True,
        "fact": fact,
        "data": {"material_id": material_id, "recognized": True, "rate_per_kg": rate},
    }


def faq_tool():
    fact = tag_responses.get("how_it_works", ["Trash2Cash lets you trade recyclable materials for cash."])[0]
    return {"ok": True, "fact": fact, "data": {}}


def unsupported_tool():
    return {"ok": False, "fact": FALLBACK_RESPONSE, "data": {}}
