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


def test_process_route_calculates_reward():
    r = client().post("/process", data={"material": "plastic", "weight": "5", "location": "lagos"})
    assert r.status_code == 200
    assert "₦450.0" in r.get_data(as_text=True)  # ₦450.0


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
