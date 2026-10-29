from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_respuesta_http_404():
    response = client.post("/orders/ID_INEXISTENTE/confirm")
    assert response.status_code == 404

def test_confirmar_pedido_exitoso():
    response = client.post("/orders/O001/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"