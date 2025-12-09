from fastapi.testclient import TestClient
from api_llm.main import app

client = TestClient(app)

def test_consulta_endpoint_200():
    response = client.post("/consulta", json={"query": "¿Qué juegos tiene Ubisoft?"})
    assert response.status_code == 200
    assert "respuesta" in response.json()
