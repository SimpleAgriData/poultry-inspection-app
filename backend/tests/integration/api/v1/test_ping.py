from fastapi.testclient import TestClient


class TestPingEndpoint:
    def test_ping_response(self, client: TestClient) -> None:
        response = client.get("/api/v1/ping")
        assert response.status_code == 200
        assert response.json() == {"message": "pong"}
