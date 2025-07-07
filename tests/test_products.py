from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product():
    response = client.post("/products/", json={"name": "Apple", "description": "Red apple", "price": 1.5, "stock": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Apple"

def test_search_product():
    client.post("/products/", json={"name": "Banana", "description": "", "price": 2.0, "stock": 5})
    res = client.get("/products/", params={"q": "Ban"})
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_add_review():
    res = client.post("/products/1/reviews", json={"id":0,"user_id":1,"product_id":1,"rating":5})
    assert res.status_code == 200

def test_list_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
