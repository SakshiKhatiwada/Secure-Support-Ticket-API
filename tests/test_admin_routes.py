from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)

def test_admin():
    response = client.get("/admin/users")
    
    assert response.status_code == 200