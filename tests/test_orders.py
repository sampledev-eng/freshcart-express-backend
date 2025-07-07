from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_order():
    client.post("/products/", json={"name": "Orange", "description": "", "price": 2.0, "stock": 5})
    response = client.post("/orders/", json=[{"product_id": 1, "quantity": 1}], params={"user_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "placed"

    track = client.get(f"/orders/{data['id']}/tracking")
    assert track.status_code == 200
