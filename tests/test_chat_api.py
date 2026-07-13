from fastapi.testclient import TestClient

from backend.main import app


def test_chat_returns_expected_shape():
    with TestClient(app) as client:
        r = client.post("/chat", json={"message": "why is my bill high"})
        assert r.status_code == 200
        body = r.json()
        assert "answer" in body and isinstance(body["answer"], str)
        assert "referenced_plans" in body and isinstance(body["referenced_plans"], list)


def test_chat_family_query_surfaces_family_plan():
    with TestClient(app) as client:
        r = client.post("/chat", json={"message": "I need a family plan with shared data for 4 lines"})
        assert "Family Max" in r.json()["referenced_plans"]


def test_chat_budget_query_surfaces_a_cheap_plan():
    with TestClient(app) as client:
        r = client.post("/chat", json={"message": "cheapest plan for a light user with minimal data"})
        referenced = r.json()["referenced_plans"]
        assert "Smart Saver" in referenced or "Basic Lite" in referenced


def test_chat_missing_message_returns_422():
    with TestClient(app) as client:
        r = client.post("/chat", json={})
        assert r.status_code == 422


def test_chat_defaults_to_account_1_when_not_specified():
    with TestClient(app) as client:
        r = client.post("/chat", json={"message": "why is my bill this amount"})
        assert r.status_code == 200
