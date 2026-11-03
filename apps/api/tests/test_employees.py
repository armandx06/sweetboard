import asyncio
import uuid
from datetime import date

from httpx import AsyncClient

from tests.conftest import JANE_DOE_PAYLOAD, JOHN_DOE_PAYLOAD

EMPLOYEE_JOHN_DOE_PAYLOAD: dict[str, str] = {
    **JOHN_DOE_PAYLOAD,
    "birth_date": "1990-01-01",
}

EMPLOYEE_JANE_DOE_PAYLOAD: dict[str, str] = {
    **JANE_DOE_PAYLOAD,
    "birth_date": "1990-01-02",
}

EMPLOYEE_ADDRESS_PAYLOAD: dict[str, str] = {
    "street": "Av. Reforma",
    "exterior_number": "123",
    "interior_number": "4B",
    "neighborhood": "Centro",
    "city": "CDMX",
    "state": "CDMX",
    "country": "Mexico",
    "postal_code": "06000",
    "address_notes": "Tocar el timbre",
    "latitude": "19.43260800",
    "longitude": "-99.13320900",
}


async def test_create_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)

    employee = response.json()

    assert response.status_code == 201
    assert employee["first_name"] == "John"
    assert employee["last_name"] == "Doe"
    assert employee["birth_date"] == "1990-01-01"
    assert employee["phone_number"] == "3312345678"
    assert employee["username"].startswith("JODO90")
    assert employee["email"] == "john.doe@example.com"
    assert employee["hire_date"] is None
    assert employee["termination_date"] is None
    assert employee["active"] is False
    assert employee["last_login_at"] is None
    assert employee["created_at"] is not None
    assert employee["updated_at"] is None
    assert employee["temporary_password"] is not None


async def test_create_employee_normalizes_input(client: AsyncClient):
    response = await client.post(
        "/employees",
        json={
            "first_name": "  jOHN ",
            "last_name": "doe",
            "birth_date": "1990-01-01",
            "phone_number": " 3312345678 ",
            "email": "  John.Doe@Example.COM ",
        },
    )
    employee = response.json()

    assert employee["first_name"] == "John"
    assert employee["last_name"] == "Doe"
    assert employee["birth_date"] == "1990-01-01"
    assert employee["phone_number"] == "3312345678"
    assert employee["email"] == "john.doe@example.com"


async def test_create_employee_race_condition(concurrent_client: AsyncClient):
    results = await asyncio.gather(
        concurrent_client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD),
        concurrent_client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD),
    )

    status_codes = [result.status_code for result in results]

    assert any(status == 201 for status in status_codes)
    assert any(status == 409 for status in status_codes)


async def test_create_employee_does_not_leak_password_hash(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)

    assert "password" not in response.json()


async def test_create_employee_sequential_username(client: AsyncClient):
    first = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    second = await client.post(
        "/employees", json={**EMPLOYEE_JOHN_DOE_PAYLOAD, "email": "john2@example.com"}
    )

    assert first.json()["username"] != second.json()["username"]
    assert second.json()["username"].endswith("02")


async def test_get_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.get(f"/employees/{employee_id}")

    assert response.status_code == 200
    assert response.json()["id"] == employee_id


async def test_get_employee_not_found(client: AsyncClient):
    response = await client.get(f"/employees/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_employee_does_not_leak_password_hash(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.get(f"/employees/{employee_id}")

    assert response.status_code == 200
    assert "password" not in response.json()


async def test_list_employees(client: AsyncClient):
    await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    await client.post("/employees", json=EMPLOYEE_JANE_DOE_PAYLOAD)
    response = await client.get("/employees")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_list_employees_excludes_inactive_by_default(client: AsyncClient):
    created = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = created.json()["id"]

    response = await client.get("/employees")
    assert employee_id not in [e["id"] for e in response.json()]

    response = await client.get("/employees", params={"include_inactive": True})
    assert employee_id in [e["id"] for e in response.json()]


async def test_list_employees_does_not_leak_password_hash(client: AsyncClient):
    await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    await client.post("/employees", json=EMPLOYEE_JANE_DOE_PAYLOAD)
    response = await client.get("/employees")

    assert response.status_code == 200
    for employee in response.json():
        assert "password" not in employee


async def test_update_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(
        f"/employees/{employee_id}", json=EMPLOYEE_JANE_DOE_PAYLOAD
    )

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


async def test_update_employee_normalizes_input(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JANE_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(
        f"/employees/{employee_id}",
        json={
            "first_name": "  jOHN ",
            "last_name": "doe",
            "phone_number": " 3312345678 ",
            "email": "  John.Doe@Example.COM ",
        },
    )
    employee = response.json()

    assert response.status_code == 200
    assert employee["first_name"] == "John"
    assert employee["last_name"] == "Doe"
    assert employee["phone_number"] == "3312345678"
    assert employee["email"] == "john.doe@example.com"


async def test_update_employee_integrity(client: AsyncClient):
    john_doe = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    jane_doe = await client.post("/employees", json=EMPLOYEE_JANE_DOE_PAYLOAD)

    john_doe, jane_doe = john_doe.json(), jane_doe.json()

    employee_id = john_doe["id"]

    response = await client.patch(
        f"/employees/{employee_id}", json=EMPLOYEE_JANE_DOE_PAYLOAD
    )

    updated_john_doe = response.json()

    assert response.status_code == 200
    assert updated_john_doe["username"] != john_doe["username"]
    assert updated_john_doe["username"] != jane_doe["username"]
    assert updated_john_doe["first_name"] == jane_doe["first_name"]
    assert updated_john_doe["last_name"] == jane_doe["last_name"]
    assert updated_john_doe["phone_number"] == jane_doe["phone_number"]
    assert updated_john_doe["email"] == jane_doe["email"]


async def test_update_employee_not_found(client: AsyncClient):
    response = await client.patch(
        f"/employees/{uuid.uuid4()}", json=EMPLOYEE_JANE_DOE_PAYLOAD
    )

    assert response.status_code == 404


async def test_activate_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")

    assert response.status_code == 200
    assert response.json()["active"] is True
    assert response.json()["hire_date"] is not None
    assert response.json()["termination_date"] is None


async def test_activate_employee_hire_date(client: AsyncClient):
    hire_date = "2023-01-01"
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
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
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")
    assert response.status_code == 200

    response = await client.patch(f"/employees/{employee_id}/activate")
    assert response.status_code == 400


async def test_activate_employee_not_found(client: AsyncClient):
    response = await client.patch(f"/employees/{uuid.uuid4()}/activate")

    assert response.status_code == 404


async def test_deactivate_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")
    response = await client.patch(f"/employees/{employee_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["hire_date"] is not None
    assert response.json()["termination_date"] is not None


async def test_deactivate_employee_termination_date(client: AsyncClient):
    termination_date = "2023-01-01"
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/activate")
    response = await client.patch(
        f"/employees/{employee_id}/deactivate",
        params={"termination_date": termination_date},
    )

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["hire_date"] is not None
    assert response.json()["termination_date"] is not None
    assert response.json()["termination_date"] == termination_date


async def test_deactivate_inactive_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(f"/employees/{employee_id}/deactivate")

    assert response.status_code == 400


async def test_deactivate_employee_not_found(client: AsyncClient):
    response = await client.patch(f"/employees/{uuid.uuid4()}/deactivate")

    assert response.status_code == 404


async def test_reset_employee_password(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
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


async def test_delete_employee(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.delete(f"/employees/{employee_id}")
    validation = await client.get(f"/employees/{employee_id}")

    assert response.status_code == 204
    assert validation.status_code == 404


async def test_delete_employee_not_found(client: AsyncClient):
    response = await client.delete(f"/employees/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_create_employee_address(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.post(
        f"/employees/{employee_id}/addresses",
        json=EMPLOYEE_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )

    address = response.json()

    assert response.status_code == 201
    assert address["id"] is not None
    assert address["street"] == "Av. Reforma"
    assert address["exterior_number"] == "123"
    assert address["interior_number"] == "4B"
    assert address["neighborhood"] == "Centro"
    assert address["city"] == "CDMX"
    assert address["state"] == "CDMX"
    assert address["country"] == "Mexico"
    assert address["postal_code"] == "06000"
    assert address["address_notes"] == EMPLOYEE_ADDRESS_PAYLOAD["address_notes"]
    assert address["active"] is True
    assert address["activated_at"] is not None
    assert address["deactivated_at"] is None
    assert address["is_default"] is True
    assert "is_billing" not in address
    assert address["created_at"] is not None


async def test_create_employee_address_defaults_to_false(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.post(
        f"/employees/{employee_id}/addresses", json=EMPLOYEE_ADDRESS_PAYLOAD
    )

    assert response.status_code == 201
    assert response.json()["is_default"] is False
    assert "is_billing" not in response.json()


async def test_create_employee_address_not_found(client: AsyncClient):
    response = await client.post(
        f"/employees/{uuid.uuid4()}/addresses", json=EMPLOYEE_ADDRESS_PAYLOAD
    )

    assert response.status_code == 404


async def test_get_employee_includes_addresses(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]
    response = await client.post(
        f"/employees/{employee_id}/addresses",
        json=EMPLOYEE_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    address_id = response.json()["id"]

    response = await client.get(f"/employees/{employee_id}")

    addresses = response.json()["addresses"]

    assert response.status_code == 200
    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["street"] == "Av. Reforma"
    assert addresses[0]["is_default"] is True
    assert "is_billing" not in addresses[0]


async def test_list_employee_addresses(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    first = await client.post(
        f"/employees/{employee_id}/addresses", json=EMPLOYEE_ADDRESS_PAYLOAD
    )
    second = await client.post(
        f"/employees/{employee_id}/addresses",
        json={**EMPLOYEE_ADDRESS_PAYLOAD, "street": "Calle 2"},
    )

    response = await client.get(f"/employees/{employee_id}/addresses")

    addresses = response.json()
    address_ids = [address["id"] for address in addresses]

    assert response.status_code == 200
    assert len(addresses) == 2
    assert first.json()["id"] in address_ids
    assert second.json()["id"] in address_ids


async def test_list_employee_addresses_not_found(client: AsyncClient):
    response = await client.get(f"/employees/{uuid.uuid4()}/addresses")

    assert response.status_code == 404


async def test_list_employees_includes_addresses(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]
    response = await client.post(
        f"/employees/{employee_id}/addresses", json=EMPLOYEE_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.get("/employees", params={"include_inactive": True})

    employee = next(e for e in response.json() if e["id"] == employee_id)

    assert len(employee["addresses"]) == 1
    assert employee["addresses"][0]["id"] == address_id


async def test_update_employee_keeps_addresses(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]
    response = await client.post(
        f"/employees/{employee_id}/addresses", json=EMPLOYEE_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.patch(
        f"/employees/{employee_id}", json={"first_name": "Jane"}
    )

    assert response.status_code == 200
    assert response.json()["addresses"][0]["id"] == address_id


async def test_create_employee_address_replaces_default(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    first = await client.post(
        f"/employees/{employee_id}/addresses",
        json=EMPLOYEE_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    second = await client.post(
        f"/employees/{employee_id}/addresses",
        json={**EMPLOYEE_ADDRESS_PAYLOAD, "street": "Calle 2"},
        params={"is_default": True},
    )

    response = await client.get(f"/employees/{employee_id}/addresses")

    addresses = response.json()
    defaults = [address for address in addresses if address["is_default"]]

    assert len(defaults) == 1
    assert defaults[0]["id"] == second.json()["id"]
    assert defaults[0]["id"] != first.json()["id"]


async def test_update_employee_address(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]
    response = await client.post(
        f"/employees/{employee_id}/addresses", json=EMPLOYEE_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.patch(
        f"/employees/{employee_id}/addresses/{address_id}",
        json={
            "street": "Calle 3",
            "address_notes": None,
            "is_default": True,
        },
    )

    address = response.json()

    assert response.status_code == 200
    assert address["id"] == address_id
    assert address["street"] == "Calle 3"
    assert address["address_notes"] is None
    assert address["is_default"] is True
    assert "is_billing" not in address
    assert address["updated_at"] is not None


async def test_update_employee_address_replaces_default(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]
    first = await client.post(
        f"/employees/{employee_id}/addresses",
        json=EMPLOYEE_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    second = await client.post(
        f"/employees/{employee_id}/addresses",
        json={**EMPLOYEE_ADDRESS_PAYLOAD, "street": "Calle 2"},
    )

    response = await client.patch(
        f"/employees/{employee_id}/addresses/{second.json()['id']}",
        json={"is_default": True},
    )

    assert response.status_code == 200
    assert response.json()["is_default"] is True

    response = await client.get(f"/employees/{employee_id}/addresses")

    defaults = [address for address in response.json() if address["is_default"]]

    assert len(defaults) == 1
    assert defaults[0]["id"] == second.json()["id"]
    assert defaults[0]["id"] != first.json()["id"]


async def test_update_employee_address_not_found(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.patch(
        f"/employees/{employee_id}/addresses/{uuid.uuid4()}",
        json={"street": "Calle 3"},
    )

    assert response.status_code == 404


async def test_delete_employee_address_deactivates(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]
    response = await client.post(
        f"/employees/{employee_id}/addresses",
        json=EMPLOYEE_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    address_id = response.json()["id"]

    response = await client.delete(
        f"/employees/{employee_id}/addresses/{address_id}"
    )

    assert response.status_code == 204

    response = await client.get(f"/employees/{employee_id}/addresses")

    addresses = response.json()

    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["active"] is False
    assert addresses[0]["deactivated_at"] is not None
    assert addresses[0]["is_default"] is False
    assert "is_billing" not in addresses[0]


async def test_delete_employee_address_not_found(client: AsyncClient):
    response = await client.post("/employees", json=EMPLOYEE_JOHN_DOE_PAYLOAD)
    employee_id = response.json()["id"]

    response = await client.delete(
        f"/employees/{employee_id}/addresses/{uuid.uuid4()}"
    )

    assert response.status_code == 404
