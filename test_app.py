from project import app
from t2c.rewards import RATES
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


def test_rewards_page_renders():
    r = client().get("/rewards")
    assert r.status_code == 200


def test_rewards_route_calculates_reward():
    r = client().post("/rewards", data={"material": "plastic", "weight": "5"})
    assert r.status_code == 200
    assert "₦450.00" in r.get_data(as_text=True)


def test_rewards_route_rejects_unsupported_material():
    r = client().post("/rewards", data={"material": "glass", "weight": "5"})
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "verified material list" in body


def test_rewards_route_rejects_invalid_weight():
    r = client().post("/rewards", data={"material": "plastic", "weight": "not-a-number"})
    assert r.status_code == 200
    assert "Please enter a weight of 0 or more" in r.get_data(as_text=True)


def test_api_reward_valid():
    r = client().post("/api/reward", json={"material": "aluminum", "weight": 5})
    assert r.status_code == 200
    body = r.get_json()
    assert body["ok"] is True
    assert body["material"] == "Aluminum (Cans)"
    assert body["reward"] == 1750.0


def test_api_reward_unsupported_material():
    r = client().post("/api/reward", json={"material": "glass", "weight": 5})
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "unsupported_material"


def test_api_reward_invalid_weight():
    r = client().post("/api/reward", json={"material": "plastic", "weight": "abc"})
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "invalid_weight"


def test_locations_page_renders():
    r = client().get("/locations")
    assert r.status_code == 200
    assert "Ikeja" in r.get_data(as_text=True)


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


def test_api_locations_unknown_city():
    r = client().get("/api/locations?city=Kano")
    body = r.get_json()
    assert body["ok"] is False
    assert body["error"] == "unknown_city"


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


def test_chatbot_payout_rates_match_reward_module(monkeypatch):
    """Regression test: the local chatbot must quote the same rates as
    the reward calculator, not a hardcoded contradictory number."""
    _force_local_fallback(monkeypatch)
    r = client().post("/chat", json={"message": "What are the rates?"})
    response = r.get_json()["response"]
    for material, (lo, hi) in RATES.items():
        assert material in response
        assert f"₦{lo}-₦{hi}/kg" in response
