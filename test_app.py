from project import app
from t2c.rewards import RATES


def client():
    return app.test_client()


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


def test_chat_route_returns_response():
    r = client().post("/chat", json={"message": "Hello"})
    assert r.status_code == 200
    assert "response" in r.get_json()


def test_chatbot_payout_rates_match_reward_module():
    """Regression test: the chatbot must quote the same rates as the
    reward calculator, not a hardcoded contradictory number."""
    r = client().post("/chat", json={"message": "What are the rates?"})
    response = r.get_json()["response"]
    for material, (lo, hi) in RATES.items():
        assert material in response
        assert f"₦{lo}-₦{hi}/kg" in response
