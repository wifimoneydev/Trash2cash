from project import app
from t2c.materials import MATERIALS, list_materials
import t2c.assistant.assistant as assistant_module


def client():
    return app.test_client()


def _force_local_fallback(monkeypatch):
    """These /chat tests check the endpoint's plumbing and the local
    chatbot's grounding — not whether OpenAI happens to be configured in
    whatever environment runs this suite. Forcing local_fallback keeps
    them deterministic either way. The OpenAI path has its own tests in
    test_assistant.py, mocked so they don't need a real key or network."""
    monkeypatch.setattr(assistant_module, "get_client", lambda: None)


def test_home_page_renders():
    r = client().get("/")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "PET Bottles" in body
    assert "View all materials" in body


# --- Materials ---------------------------------------------------------

def test_materials_page_renders_all_by_default():
    r = client().get("/materials")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    for material in MATERIALS:
        assert material["name"] in body


def test_materials_page_filters_by_category():
    r = client().get("/materials?category=metals")
    body = r.get_data(as_text=True)
    assert "Aluminium Beverage Cans" in body
    assert "PET Bottles" not in body


def test_materials_page_search_by_alias():
    r = client().get("/materials?q=sachet+water")
    body = r.get_data(as_text=True)
    assert "Pure Water Sachets" in body
    assert "Aluminium Beverage Cans" not in body


def test_materials_page_search_no_match_shows_empty_state():
    r = client().get("/materials?q=unobtainium")
    assert r.status_code == 200
    assert "didn" in r.get_data(as_text=True).lower() or "no materials matched" in r.get_data(as_text=True).lower()


def test_material_detail_page_renders():
    r = client().get("/materials/pet-bottles")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "PET Bottles" in body
    assert "₦200/kg" in body
    assert "Reference estimate only" in body  # rate disclaimer present


def test_material_detail_unknown_slug_is_404():
    r = client().get("/materials/not-a-real-material")
    assert r.status_code == 404


def test_api_materials_returns_full_catalogue():
    r = client().get("/api/materials")
    body = r.get_json()
    assert body["ok"] is True
    assert len(body["materials"]) == len(MATERIALS)


def test_api_materials_search():
    r = client().get("/api/materials?q=detergent")
    body = r.get_json()
    ids = [m["id"] for m in body["materials"]]
    assert "hdpe_containers" in ids
    assert "pet_bottles" not in ids


# --- Reward Calculator ---------------------------------------------------

def test_rewards_page_renders():
    r = client().get("/rewards")
    assert r.status_code == 200


def test_rewards_page_prefills_from_query_params():
    r = client().get("/rewards?material=pet_bottles")
    body = r.get_data(as_text=True)
    assert 'value="rigid_plastics" selected' in body
    assert 'value="pet_bottles"' in body and "selected" in body.split('value="pet_bottles"')[1].split(">")[0]


def test_rewards_route_calculates_reward():
    r = client().post("/rewards", data={"category": "rigid_plastics", "material": "pet_bottles", "weight": "5"})
    assert r.status_code == 200
    assert "₦1000.00" in r.get_data(as_text=True)


def test_rewards_route_rejects_unsupported_material():
    r = client().post("/rewards", data={"category": "rigid_plastics", "material": "glass_jars", "weight": "5"})
    assert r.status_code == 200
    assert "choose a specific material" in r.get_data(as_text=True)


def test_rewards_route_rejects_invalid_weight():
    r = client().post("/rewards", data={"category": "rigid_plastics", "material": "pet_bottles", "weight": "not-a-number"})
    assert r.status_code == 200
    assert "Please enter a weight of 0 or more" in r.get_data(as_text=True)


def test_api_reward_valid():
    r = client().post("/api/reward", json={"material_id": "aluminium_cans", "weight": 5})
    assert r.status_code == 200
    body = r.get_json()
    assert body["ok"] is True
    assert body["material_name"] == "Aluminium Beverage Cans"
    assert body["reward"] == 2500.0
    assert "Reference estimate only" in body["disclaimer"]


def test_api_reward_unsupported_material():
    r = client().post("/api/reward", json={"material_id": "glass_jars", "weight": 5})
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "unsupported_material"


def test_api_reward_invalid_weight():
    r = client().post("/api/reward", json={"material_id": "pet_bottles", "weight": "abc"})
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "invalid_weight"


def test_api_reward_negative_weight():
    r = client().post("/api/reward", json={"material_id": "pet_bottles", "weight": -5})
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "invalid_weight"


# --- Drop-off Finder -------------------------------------------------------

def test_locations_page_renders():
    r = client().get("/locations")
    assert r.status_code == 200
    assert "Ikeja" in r.get_data(as_text=True)


def test_locations_page_material_filter_shows_compatibility():
    r = client().get("/locations?material=pet_bottles")
    assert r.status_code == 200
    assert "PET Bottles" in r.get_data(as_text=True)


def test_api_locations_known_city():
    r = client().get("/api/locations?city=Lagos")
    body = r.get_json()
    assert body["ok"] is True
    lgas = [rec["lga"] for rec in body["records"]]
    assert "Ikeja" in lgas
    # no fabricated address/coordinates on any returned record
    for rec in body["records"]:
        assert rec["address"] is None
        assert rec["latitude"] is None
        assert rec["longitude"] is None


def test_api_locations_with_material_never_invents_compatibility():
    r = client().get("/api/locations?city=Lagos&material=pet_bottles")
    body = r.get_json()
    for rec in body["records"]:
        assert rec["material_compatibility"] in ("selected_locations", "not_yet_verified")


def test_api_locations_unknown_city():
    r = client().get("/api/locations?city=Kano")
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "unknown_city"


def test_api_locations_unsupported_material():
    r = client().get("/api/locations?city=Lagos&material=glass_jars")
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "unsupported_material"


# --- Assistant / contact / regression --------------------------------------

def test_assistant_page_renders():
    r = client().get("/assistant")
    assert r.status_code == 200


def test_contact_get_renders():
    r = client().get("/contact")
    assert r.status_code == 200


def test_contact_post_does_not_crash():
    r = client().post("/contact", data={"name": "a", "email": "a@a.com", "message": "hi"})
    assert r.status_code == 302  # redirects back to /contact instead of raising


def test_chat_route_returns_response(monkeypatch):
    _force_local_fallback(monkeypatch)
    r = client().post("/chat", json={"message": "Hello"})
    assert r.status_code == 200
    body = r.get_json()
    assert "response" in body
    assert body["mode"] == "local_fallback"


def test_chatbot_payout_rates_match_catalogue(monkeypatch):
    """Regression test: the local chatbot must quote the same rates as
    the canonical material catalogue, not a hardcoded or stale number."""
    _force_local_fallback(monkeypatch)
    r = client().post("/chat", json={"message": "What are the rates?"})
    response = r.get_json()["response"]
    for material in list_materials():
        assert material["name"] in response
        assert f"₦{material['rate_per_kg']}/kg" in response
