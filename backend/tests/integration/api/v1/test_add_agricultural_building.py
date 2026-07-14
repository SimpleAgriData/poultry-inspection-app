from fastapi.testclient import TestClient


class TestAddAgriculturalHoldingTestCase:
    @staticmethod
    def test_add_agricultural_holding_success(client: TestClient) -> None:
        payload = {
            "name": "Sunny Farms",
            "hatchery": "Sunny Hatchery",
            "eco_control_number": "EC123456",
            "breed": "Breed A",
            "address_street": "123 Farm Lane",
            "address_zip": "12345",
            "address_city": "Farmville",
        }

        response = client.post("/api/v1/add-agricultural-holding", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert (
            data["message"] == "Agricultural Holding 'Sunny Farms' added successfully"
        )
