"""Evaluate the chatbot's intent classifier against a held-out set of
hand-written utterances (t2c/chatbot/data/eval_set.json).

Usage (run as a module from the repo root, so the t2c package resolves):
    python -m t2c.chatbot.evaluate
    python -m t2c.chatbot.evaluate --threshold 0.5

This measures real numbers against the current model/threshold — it
never fabricates a score. Import evaluate() to use it from other
scripts or tests.
"""

import argparse
import json
import os
from collections import defaultdict

from t2c.chatbot.chatbot import classify, CONFIDENCE_THRESHOLD

BASE_DIR = os.path.dirname(__file__)
EVAL_SET_PATH = os.path.join(BASE_DIR, "data", "eval_set.json")


def load_eval_set():
    with open(EVAL_SET_PATH) as f:
        return json.load(f)["cases"]


def evaluate(threshold=CONFIDENCE_THRESHOLD, cases=None):
    """Run every case through the classifier and score it against the
    confidence threshold.

    Returns a dict with overall accuracy, per-intent accuracy, OOD
    handling stats, and the list of individual misses (for debugging).
    """
    if cases is None:
        cases = load_eval_set()

    per_intent = defaultdict(lambda: {"correct": 0, "total": 0})
    misses = []
    false_confident = []  # true OOD, but confidently answered as a real intent
    correct = 0

    for case in cases:
        text = case["text"]
        expected = case["expected"]
        tag, confidence = classify(text)
        predicted = tag if confidence >= threshold else "OOD"

        is_correct = predicted == expected
        per_intent[expected]["total"] += 1
        if is_correct:
            per_intent[expected]["correct"] += 1
            correct += 1
        else:
            misses.append({
                "text": text,
                "expected": expected,
                "predicted": predicted,
                "raw_tag": tag,
                "confidence": round(float(confidence), 3),
            })
            if expected == "OOD" and predicted != "OOD":
                false_confident.append({
                    "text": text,
                    "predicted": predicted,
                    "confidence": round(float(confidence), 3),
                })

    total = len(cases)
    ood_cases = [c for c in cases if c["expected"] == "OOD"]
    ood_correct = per_intent["OOD"]["correct"] if "OOD" in per_intent else 0

    return {
        "threshold": threshold,
        "total_cases": total,
        "overall_accuracy": correct / total if total else 0.0,
        "per_intent": {
            tag: {
                "correct": stats["correct"],
                "total": stats["total"],
                "accuracy": stats["correct"] / stats["total"] if stats["total"] else 0.0,
            }
            for tag, stats in sorted(per_intent.items())
        },
        "ood_recall": ood_correct / len(ood_cases) if ood_cases else None,
        "false_confident_count": len(false_confident),
        "false_confident": false_confident,
        "misses": misses,
    }


def print_report(results):
    print(f"Threshold: {results['threshold']}")
    print(f"Overall accuracy: {results['overall_accuracy']:.1%} "
          f"({results['total_cases']} cases)")
    print()
    print("Per-intent accuracy:")
    for tag, stats in results["per_intent"].items():
        print(f"  {tag:15s} {stats['correct']}/{stats['total']}  ({stats['accuracy']:.0%})")
    print()
    if results["ood_recall"] is not None:
        print(f"OOD recall (fallback correctly triggered): {results['ood_recall']:.1%}")
    print(f"False-confident answers (true OOD, answered anyway): {results['false_confident_count']}")
    for fc in results["false_confident"]:
        print(f"  '{fc['text']}' -> {fc['predicted']} (confidence {fc['confidence']})")
    print()
    if results["misses"]:
        print(f"All misses ({len(results['misses'])}):")
        for m in results["misses"]:
            print(f"  '{m['text']}' expected={m['expected']} predicted={m['predicted']} "
                  f"(raw_tag={m['raw_tag']}, confidence={m['confidence']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=CONFIDENCE_THRESHOLD)
    args = parser.parse_args()
    print_report(evaluate(threshold=args.threshold))
