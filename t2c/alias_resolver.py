"""Deterministic alias resolution for the V2 material catalogue.

Maps free-text user phrases ("pure water nylon", "coke bottle",
"detergent bottle") to a canonical material id. This is plain,
deterministic string matching — normalized case/whitespace/punctuation,
then exact-then-substring lookup — not a statistical or NLP model, per
the V2 specification's explicit instruction to prefer deterministic
alias matching over an unnecessarily complex NLP system.

Shared by: Materials page search, Ask T2C's material argument
resolution, and (optionally) reward-calculator convenience matching.
Kept deliberately simple so a future T2CVision integration has a clean
place to plug in (resolve a detected label the same way a typed phrase
is resolved today) without this module needing to change.
"""

import re

from t2c.materials import MATERIALS, CATEGORIES

# Unambiguous category-level hints: words that identify a *category* in
# everyday Nigerian usage without naming one specific material. Kept
# deliberately short and conservative — "plastic" alone is genuinely
# ambiguous between rigid and flexible plastics, so it is intentionally
# NOT listed here; guessing which one would be inventing a classification.
_CATEGORY_HINTS = {
    "nylon": "flexible_plastics",
    "metal": "metals",
    "metals": "metals",
}

_PUNCT_RE = re.compile(r"[^\w\s]")
_SPACE_RE = re.compile(r"\s+")


def normalize_text(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.strip().lower()
    text = _PUNCT_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def _build_index():
    index = {}
    for material in MATERIALS:
        phrases = [material["name"]] + list(material.get("aliases", []))
        for phrase in phrases:
            norm = normalize_text(phrase)
            if norm and norm not in index:
                index[norm] = material["id"]
    # Longest phrase first, so a specific alias ("pure water sachet")
    # is tried before a shorter, more generic one could coincidentally
    # match inside the same text.
    return dict(sorted(index.items(), key=lambda kv: -len(kv[0])))


_INDEX = _build_index()


def resolve_material_id(text):
    """Resolve free text to a canonical material id, or None.

    1. Exact match against the normalized name/alias index.
    2. Substring match (checked longest-alias-first): does a known
       alias appear inside the text (e.g. a full sentence), or does
       the text appear inside a known alias?

    Returns None rather than guessing when nothing confidently
    matches — callers (Ask T2C, the calculator) must treat None as
    "material not identified," never as "pick something close."
    """
    norm = normalize_text(text)
    if not norm:
        return None

    if norm in _INDEX:
        return _INDEX[norm]

    for phrase, material_id in _INDEX.items():
        if phrase in norm:
            # A known alias appears inside the (often longer) user text,
            # e.g. "coke bottle" inside "how much for a coke bottle".
            return material_id
        # The reverse direction — the user's text is short and sits
        # inside a longer alias, e.g. bare "aluminum" inside "aluminum
        # can" — is only trusted for multi-word queries. A single bare
        # word (e.g. "nylon", "plastic") is frequently a *category*
        # name, not a specific material, and would otherwise resolve to
        # whichever specific alias happens to contain it as a substring
        # — a false precision this deliberately avoids. Single generic
        # words are handled by resolve_category_id() instead.
        if " " in norm and norm in phrase:
            return material_id

    return None


def resolve_category_id(text):
    """Detect an unambiguous category-level hint in free text (e.g. "any
    kind of nylon" -> flexible_plastics) when no specific material
    resolves. Returns None rather than guessing for genuinely ambiguous
    words like "plastic" alone.
    """
    norm = normalize_text(text)
    if not norm:
        return None
    tokens = set(norm.split(" "))
    for word, category_id in _CATEGORY_HINTS.items():
        if word in tokens:
            return category_id
    return None


def search_materials(query, limit=None):
    """Return materials whose name, description, aliases, or examples
    contain the query (case-insensitive substring). Used by the
    Materials page search/filter."""
    norm = normalize_text(query)
    if not norm:
        return []

    results = []
    for material in MATERIALS:
        haystack_parts = [material["name"], material.get("description") or ""]
        haystack_parts += list(material.get("aliases", []))
        haystack_parts += list(material.get("examples", []))
        haystack = normalize_text(" ".join(haystack_parts))
        if norm in haystack:
            results.append(material)

    if limit is not None:
        results = results[:limit]
    return results
