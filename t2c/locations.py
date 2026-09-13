"""Single source of truth for Trash2Cash drop-off location data.

Honesty note: this is a static, hand-typed list of 8 local government
area (LGA) names across 2 cities — not a live directory of real
drop-off points. There are no verified outlet names, street addresses,
coordinates, or open/closed status behind any of these entries yet.
The LGA names themselves are real Lagos/Abuja districts, but nothing
ties them to an actual Trash2Cash collection point today.
"""

LOCATIONS = {
    "Lagos": ["Ikeja", "Surulere", "Yaba", "Lekki"],
    "Abuja": ["Garki", "Wuse", "Maitama", "Kubwa"],
}


def get_locations(state):
    """Return the list of LGA names for a given state, or [] if unknown."""
    return LOCATIONS.get(state, [])


def list_location_records(state=None):
    """Return LOCATIONS in a richer per-entry shape a future map/
    geolocation feature can extend without a schema change.

    Every record today has only `city` and `lga` populated. The rest
    are explicit None placeholders — not fabricated data — because no
    real outlet name, address, coordinates, or status exists yet.
    """
    records = []
    for city, lgas in LOCATIONS.items():
        if state is not None and city != state:
            continue
        for lga in lgas:
            records.append({
                "name": None,       # no named outlet exists yet
                "city": city,
                "lga": lga,
                "address": None,
                "latitude": None,
                "longitude": None,
                "status": "unverified",  # static placeholder area, not a confirmed outlet
            })
    return records


def find_records(query):
    """Look up location records by a free-text city or LGA name (e.g.
    "Ikeja", "lagos", "ikeja "). Case-insensitive, whitespace-trimmed
    exact match against known city/LGA names — no fuzzy guessing.

    Returns a list of matching records (possibly empty). Matching a
    city returns every LGA under it; matching an LGA returns just that
    one record.
    """
    if not isinstance(query, str):
        return []
    query_norm = query.strip().lower()
    if not query_norm:
        return []

    if any(query_norm == city.lower() for city in LOCATIONS):
        city = next(c for c in LOCATIONS if c.lower() == query_norm)
        return list_location_records(city)

    return [
        record for record in list_location_records()
        if record["lga"].lower() == query_norm
    ]
