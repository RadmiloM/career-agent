from fastapi.testclient import TestClient

from app.main import app


def test_preflight_request_allows_frontend_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5174"
    assert response.headers.get("access-control-allow-credentials") == "true"
