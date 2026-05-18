from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status' : 'ok'}


def test_empty_query_questions():
    response = client.post("/query", json={"question" : " "}) 
    assert response.status_code == 400

def test_ingest_non_pdf():
    from io import BytesIO
    response = client.post(
        "/ingest",
        files = {
            'file' : ('test.txt', BytesIO(b'test content'), "test/plain")
        }
    )
    assert response.status_code == 400