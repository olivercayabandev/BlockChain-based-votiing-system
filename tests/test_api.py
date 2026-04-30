from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_positions_endpoint():
    r = client.get("/api/positions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_position_endpoint():
    payload = {"title": "Test Position", "max_votes": 2}
    r = client.post("/api/positions", json=payload)
    assert r.status_code in (200, 201)
    data = r.json()
    assert isinstance(data, dict)
    # Attempt to cleanup if an id is returned
    if 'id' in data:
        pid = data['id']
        client.delete(f"/api/positions/{pid}")


def test_get_blockchain_endpoint():
    r = client.get("/api/blockchain")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
