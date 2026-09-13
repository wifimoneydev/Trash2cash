from t2c.locations import get_locations, list_location_records, LOCATIONS


def test_known_location():
    assert "Ikeja" in get_locations("Lagos")
    assert "Wuse" in get_locations("Abuja")


def test_unknown_location_fails_safely():
    assert get_locations("Unknown") == []
    assert get_locations("") == []
    assert get_locations(None) == []


def test_no_duplicate_lga_names_across_cities():
    all_names = [name for names in LOCATIONS.values() for name in names]
    assert len(all_names) == len(set(all_names))


def test_list_location_records_shape():
    records = list_location_records("Lagos")
    assert len(records) == len(LOCATIONS["Lagos"])
    for record in records:
        assert record["city"] == "Lagos"
        assert record["lga"] in LOCATIONS["Lagos"]
        # Explicit placeholders, not fabricated data:
        assert record["name"] is None
        assert record["address"] is None
        assert record["latitude"] is None
        assert record["longitude"] is None
        assert record["status"] == "unverified"


def test_list_location_records_unknown_state_is_empty():
    assert list_location_records("Unknown") == []


def test_list_location_records_all_states():
    all_records = list_location_records()
    total_lgas = sum(len(names) for names in LOCATIONS.values())
    assert len(all_records) == total_lgas
