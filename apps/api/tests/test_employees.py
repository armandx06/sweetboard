import asyncio
import uuid
from datetime import date

from httpx import AsyncClient

JOHN_DOE_PAYLOAD = {
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-01-01",
    "phone_number": "3312345678",
    "email": "john.doe@example.com",
}

JANE_DOE_PAYLOAD = {
    "first_name": "Jane",
    "last_name": "Doe",
    "birth_date": "1990-01-02",
    "phone_number": "3387654321",
    "email": "jane.doe@example.com",
}


async def test_create_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Doe"
    assert response.json()["birth_date"] == "1990-01-01"
    assert response.json()["phone_number"] == "3312345678"
    assert response.json()["username"].startswith("JODO90")
    assert response.json()["email"] == "john.doe@example.com"
    assert response.json()["hire_date"] is None
    assert response.json()["termination_date"] is None
    assert response.json()["active"] is False
    assert response.json()["last_login_at"] is None
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is None
    assert response.json()["temporary_password"] is not None


async def test_create_employee_race_condition(concurrent_client: AsyncClient):
    results = await asyncio.gather(
        concurrent_client.post("/employees", json=JOHN_DOE_PAYLOAD),
        concurrent_client.post("/employees", json=JOHN_DOE_PAYLOAD),
    )

    status_codes = [result.status_code for result in results]

    assert any(status == 201 for status in status_codes)
    assert any(status == 409 for status in status_codes)


async def test_get_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.get(f"/employees/{employee_id}")

    assert response.status_code == 200
    assert response.json()["id"] == employee_id


async def test_get_employee_not_found(client: AsyncClient):
    response = await client.get(f"/employees/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


async def test_list_employees(client: AsyncClient):
    response = await client.get("/employees")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_update_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}", json=JANE_DOE_PAYLOAD)

    employee = response.json()

    assert response.status_code == 200
    assert (
        employee["username"]
        == f"{employee['first_name'][:2]}{employee['last_name'][:2]}{date.fromisoformat(employee['birth_date']).strftime('%y')}01".upper()
    )
    assert employee["first_name"] == "Jane"
    assert employee["last_name"] == "Doe"
    assert employee["phone_number"] == "3387654321"
    assert employee["email"] == "jane.doe@example.com"


async def test_update_employee_integrity(client: AsyncClient):
    john_doe = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    jane_doe = await client.post("/employees", json=JANE_DOE_PAYLOAD)

    john_doe, jane_doe = john_doe.json(), jane_doe.json()

    employee_id = john_doe["id"]

    response = await client.patch(f"/employees/{employee_id}", json=JANE_DOE_PAYLOAD)

    updated_john_doe = response.json()

    assert response.status_code == 200
    assert updated_john_doe["username"] != john_doe["username"]
    assert updated_john_doe["username"] != jane_doe["username"]
    assert updated_john_doe["first_name"] == jane_doe["first_name"]
    assert updated_john_doe["last_name"] == jane_doe["last_name"]
    assert updated_john_doe["phone_number"] == jane_doe["phone_number"]
    assert updated_john_doe["email"] == jane_doe["email"]
    assert updated_john_doe["birth_date"] != jane_doe["birth_date"]


async def test_update_employee_not_found(client: AsyncClient):
    response = await client.patch(f"/employees/{uuid.uuid4()}", json=JANE_DOE_PAYLOAD)

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


async def test_activate_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")

    assert response.status_code == 200
    assert response.json()["active"] is True
    assert response.json()["hire_date"] is not None
    assert response.json()["termination_date"] is None


async def test_activate_employee_hire_date(client: AsyncClient):
    hire_date = "2023-01-01"
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(
        f"/employees/{employee_id}/activate", params={"hire_date": hire_date}
    )

    assert response.status_code == 200
    assert response.json()["active"] is True
    assert response.json()["hire_date"] is not None
    assert response.json()["hire_date"] == hire_date
    assert response.json()["termination_date"] is None


async def test_activate_active_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")
    response = await client.patch(f"/employees/{employee_id}/activate")

    assert response.status_code == 200
    assert response.json()["active"] is True
    assert response.json()["hire_date"] is not None
    assert response.json()["termination_date"] is None


async def test_activate_active_employee_hire_date(client: AsyncClient):
    hire_date = "2023-01-01"
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")
    response = await client.patch(
        f"/employees/{employee_id}/activate", params={"hire_date": hire_date}
    )

    assert response.status_code == 200
    assert response.json()["active"] is True
    assert response.json()["hire_date"] is not None
    assert response.json()["hire_date"] != hire_date
    assert response.json()["termination_date"] is None


async def test_activate_employee_not_found(client: AsyncClient):
    response = await client.patch(f"/employees/{uuid.uuid4()}/activate")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


async def test_deactivate_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")
    response = await client.patch(f"/employees/{employee_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["hire_date"] is not None
    assert response.json()["termination_date"] is not None


async def test_deactivate_inactive_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/deactivate")

    assert response.status_code == 400


async def test_deactivate_employee_not_found(client: AsyncClient):
    response = await client.patch(f"/employees/{uuid.uuid4()}/deactivate")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


async def test_reset_employee_password(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id, employee_old_password = (
        response.json()["id"],
        response.json()["temporary_password"],
    )

    response = await client.post(f"/employees/{employee_id}/reset-password")
    employee_new_password = response.json()["temporary_password"]

    assert response.status_code == 200
    assert employee_new_password != employee_old_password


async def test_reset_employee_password_not_found(client: AsyncClient):
    response = await client.post(f"/employees/{uuid.uuid4()}/reset-password")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


async def test_delete_employee(client: AsyncClient):
    response = await client.post("/employees", json=JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.delete(f"/employees/{employee_id}")
    validation = await client.get(f"/employees/{employee_id}")

    assert response.status_code == 204
    assert validation.status_code == 404
    assert validation.json()["detail"] == "Employee not found"


async def test_delete_employee_not_found(client: AsyncClient):
    response = await client.delete(f"/employees/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"
