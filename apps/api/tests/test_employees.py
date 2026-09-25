import uuid

from httpx import AsyncClient


async def test_get_employee_not_found(client: AsyncClient):
    response = await client.get(f"/employees/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


async def test_create_employee(client: AsyncClient):
    response = await client.post(
        "/employees",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "phone_number": "3312345678",
            "email": "john.doe@example.com",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"].startswith("JODO90")
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Doe"
    assert response.json()["birth_date"] == "1990-01-01"
    assert response.json()["phone_number"] == "3312345678"
    assert response.json()["email"] == "john.doe@example.com"
