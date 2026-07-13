from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


def test_get_bill_for_seeded_account():
    with TestClient(app) as client:
        r = client.get("/bills/1")
        assert r.status_code == 200
        body = r.json()
        assert body["account_id"] == 1
        assert body["amount"] > 0
        assert isinstance(body["breakdown"], dict)


def test_get_bill_for_nonexistent_account_returns_404():
    with TestClient(app) as client:
        r = client.get("/bills/999")
        assert r.status_code == 404
        assert "999" in r.json()["detail"]


def test_get_usage_for_seeded_account():
    with TestClient(app) as client:
        r = client.get("/usage/1")
        assert r.status_code == 200
        records = r.json()
        assert len(records) > 0
        for record in records:
            assert "date" in record and "data_used_mb" in record and "minutes_used" in record


def test_get_usage_for_nonexistent_account_returns_404():
    with TestClient(app) as client:
        r = client.get("/usage/999")
        assert r.status_code == 404


def test_list_plans_returns_seeded_catalog():
    with TestClient(app) as client:
        r = client.get("/plans")
        assert r.status_code == 200
        plans = r.json()
        assert len(plans) == 5
        names = {p["name"] for p in plans}
        assert "Unlimited 5G" in names
        assert "Family Max" in names
