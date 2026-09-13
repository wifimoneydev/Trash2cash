"""Evaluate the OpenAI-powered assistant against a held-out set of
realistic queries (t2c/assistant/data/eval_set.json).

This makes real, live calls to OpenAI (unlike the mocked unit tests in
test_assistant.py) — it requires OPENAI_API_KEY to be configured, and
reports real, non-fabricated numbers: tool selection accuracy, argument
extraction accuracy, grounded-answer correctness, and hallucination
rate. Local-fallback (Naive Bayes) quality is a separate, already-existing
metric — see t2c/chatbot/evaluate.py — and is deliberately NOT mixed
into these numbers.

Usage (from repo root):
    python -m t2c.assistant.evaluate
"""

import json
import os
import re

from t2c.assistant.client import get_client
from t2c.assistant.assistant import (
    _extract_intent, _resolve_with_session_fallback, _run_tool, _remember,
    PHRASING_SYSTEM_PROMPT, DEFAULT_MODEL, _contains_only_known_numbers,
)
from t2c.rewards import normalize_material, calculate_reward, get_rate_range, RATES

BASE_DIR = os.path.dirname(__file__)
EVAL_SET_PATH = os.path.join(BASE_DIR, "data", "eval_set.json")

_NUMBER_RE = re.compile(r"\d[\d,]*\.?\d*")


def load_eval_set():
    with open(EVAL_SET_PATH) as f:
        return json.load(f)["cases"]


def _phrase_with_diagnostics(client, message, fact):
    """Like assistant._phrase_naturally, but returns the raw model
    output too, so hallucination attempts can be measured even though
    the safety net would have caught them before delivery."""
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
        raw = (completion.choices[0].message.content or "").strip()
    except Exception as e:
        return fact, fact, False, str(e)

    hallucinated = raw and not _contains_only_known_numbers(raw, fact)
    delivered = raw if (raw and not hallucinated) else fact
    return delivered, raw, hallucinated, None


def _args_match(intent_data, case):
    """Argument extraction accuracy for one case (only meaningful when
    tool selection was correct)."""
    ok = True
    expected_material = case.get("expected_material")
    if expected_material is not None:
        got = normalize_material(intent_data.get("material")) if intent_data.get("material") else None
        ok = ok and (got == expected_material)
    expected_weight = case.get("expected_weight_kg")
    if expected_weight is not None:
        got_w = intent_data.get("weight_kg")
        ok = ok and (got_w is not None and abs(float(got_w) - float(expected_weight)) < 1e-6)
    expected_location = case.get("expected_location")
    if expected_location is not None:
        got_loc = (intent_data.get("location") or "")
        ok = ok and (expected_location.lower() in got_loc.lower() or got_loc.lower() in expected_location.lower())
    return ok


def _grounded_correctness(delivered_text, case):
    """Category-specific check that the delivered text actually states
    the right verified fact (not just that the right tool ran)."""
    category = case["category"]
    text_lower = delivered_text.lower()

    if category == "reward" or category.startswith("followup") and case["expected_intent"] == "reward_estimate":
        material = case.get("expected_material")
        weight = case.get("expected_weight_kg")
        if material and weight is not None:
            expected_reward = calculate_reward(material, weight)
            # Zero/negative weight is phrased as a plain "₦0", not "₦0.00" —
            # accept either formatting.
            return f"{expected_reward:.2f}" in delivered_text or (
                expected_reward == 0 and "₦0" in delivered_text
            )
        if material:
            lo, hi = get_rate_range(material)
            return str(lo) in delivered_text and str(hi) in delivered_text
        # general "what are the rates" — expect all three materials' numbers
        return all(str(lo) in delivered_text and str(hi) in delivered_text for lo, hi in RATES.values())

    if category == "material_unsupported":
        return any(p in text_lower for p in [
            "not currently", "not listed", "don't accept", "doesn't accept",
            "do not accept", "does not accept", "not accepted", "isn't in our",
            "not in our", "don't currently", "doesn't currently",
            "do not currently", "does not currently",
        ])

    if category == "material_supported":
        material = case.get("expected_material")
        if material:
            lo, hi = get_rate_range(material)
            return str(lo) in delivered_text and str(hi) in delivered_text
        return all(name.split(" (")[0].lower() in text_lower for name in RATES)

    if category == "location" or (category.startswith("followup") and case["expected_intent"] == "location_lookup"):
        loc = case.get("expected_location") or ""
        return loc.lower() in text_lower

    if category == "faq":
        return "trash2cash" in text_lower

    if category in ("unsupported_feature", "out_of_domain"):
        return True  # correctness here = tool selection; see main loop

    if category == "combined":
        material = case.get("expected_material")
        if material and case.get("expected_weight_kg") is not None:
            expected_reward = calculate_reward(material, case["expected_weight_kg"])
            return f"{expected_reward:.2f}" in delivered_text
        if material:
            lo, hi = get_rate_range(material)
            return str(lo) in delivered_text and str(hi) in delivered_text
        return True

    return True  # nigerian_english / spelling reuse the categories above via expected_intent


def evaluate_openai(cases=None):
    client = get_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY not configured — cannot run the live OpenAI evaluation.")

    if cases is None:
        cases = load_eval_set()

    sessions = {}
    results = []

    for case in cases:
        session_id = case.get("session_id")
        session = sessions.setdefault(session_id, {}) if session_id else {}

        history = session.get("t2c_history")
        try:
            intent_data = _extract_intent(client, case["text"], history)
            parse_ok = True
        except Exception as e:
            intent_data = {"intent": "unsupported", "material": None, "weight_kg": None, "location": None, "question": ""}
            parse_ok = False

        resolved = _resolve_with_session_fallback(intent_data, session)
        tool_selected_correct = resolved["intent"] == case["expected_intent"]
        args_correct = _args_match(resolved, case) if tool_selected_correct else False

        tool_result = _run_tool(resolved)
        delivered, raw, hallucinated, phrase_error = _phrase_with_diagnostics(client, case["text"], tool_result["fact"])
        _remember(resolved, session)

        if case["category"] in ("unsupported_feature", "out_of_domain"):
            grounded_correct = tool_selected_correct
        else:
            grounded_correct = tool_selected_correct and _grounded_correctness(delivered, case)

        results.append({
            "text": case["text"],
            "category": case["category"],
            "expected_intent": case["expected_intent"],
            "predicted_intent": resolved["intent"],
            "tool_selected_correct": tool_selected_correct,
            "args_correct": args_correct,
            "grounded_correct": grounded_correct,
            "hallucinated_raw_attempt": bool(hallucinated),
            "parse_ok": parse_ok,
            "delivered": delivered,
        })

    total = len(results)
    tool_acc = sum(r["tool_selected_correct"] for r in results) / total
    arg_scoped = [r for r in results if r["tool_selected_correct"]]
    arg_acc = (sum(r["args_correct"] for r in arg_scoped) / len(arg_scoped)) if arg_scoped else None
    grounded_acc = sum(r["grounded_correct"] for r in results) / total
    hallucination_rate = sum(r["hallucinated_raw_attempt"] for r in results) / total
    parse_failures = sum(not r["parse_ok"] for r in results)

    by_category = {}
    for r in results:
        c = by_category.setdefault(r["category"], {"correct": 0, "total": 0})
        c["total"] += 1
        c["correct"] += int(r["grounded_correct"])

    return {
        "total_cases": total,
        "tool_selection_accuracy": tool_acc,
        "argument_extraction_accuracy": arg_acc,
        "grounded_answer_accuracy": grounded_acc,
        "hallucination_rate": hallucination_rate,
        "parse_failures": parse_failures,
        "by_category": {k: v["correct"] / v["total"] for k, v in by_category.items()},
        "misses": [r for r in results if not r["grounded_correct"]],
    }


def print_report(results):
    print(f"Cases: {results['total_cases']}")
    print(f"Tool selection accuracy:       {results['tool_selection_accuracy']:.1%}")
    if results["argument_extraction_accuracy"] is not None:
        print(f"Argument extraction accuracy:  {results['argument_extraction_accuracy']:.1%}")
    print(f"Grounded-answer accuracy:      {results['grounded_answer_accuracy']:.1%}")
    print(f"Hallucination rate (raw, pre-safety-net): {results['hallucination_rate']:.1%}")
    print(f"Parse failures (fell back internally): {results['parse_failures']}")
    print()
    print("By category:")
    for cat, acc in sorted(results["by_category"].items()):
        print(f"  {cat:22s} {acc:.0%}")
    print()
    if results["misses"]:
        print(f"Misses ({len(results['misses'])}):")
        for m in results["misses"]:
            print(f"  [{m['category']}] '{m['text']}' expected={m['expected_intent']} got={m['predicted_intent']}")
            print(f"      -> {m['delivered']!r}")


if __name__ == "__main__":
    print_report(evaluate_openai())
