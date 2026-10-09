import uuid

from httpx import AsyncClient

from tests.conftest import JANE_DOE_PAYLOAD, JOHN_DOE_PAYLOAD

CUSTOMER_JOHN_DOE_PAYLOAD: dict[str, str | bool] = {
    **JOHN_DOE_PAYLOAD,
    "is_company": True,
    "company_name": "John Doe Inc.",
}

CUSTOMER_JANE_DOE_PAYLOAD: dict[str, str | bool] = {
    **JANE_DOE_PAYLOAD,
    "is_company": False,
}


async def test_create_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)

    customer = response.json()

    assert response.status_code == 201
    assert customer["first_name"] == "John"
    assert customer["last_name"] == "Doe"
    assert customer["phone_number"] == "3312345678"
    assert customer["email"] == "john.doe@example.com"
    assert customer["company_name"] == "John Doe Inc."
    assert customer["is_company"] is True
    assert customer["active"] is False
    assert customer["activated_at"] is None
    assert customer["deactivated_at"] is None
    assert customer["created_at"] is not None
    assert customer["updated_at"] is None


async def test_create_customer_normalizes_input(client: AsyncClient):
    response = await client.post(
        "/customers",
        json={
            "first_name": "  jOHN ",
            "last_name": "doe",
            "phone_number": " 3312345678 ",
            "email": "  John.Doe@Example.COM ",
            "company_name": "  ABC Foods  ",
        },
    )
    customer = response.json()

    assert customer["first_name"] == "John"
    assert customer["last_name"] == "Doe"
    assert customer["phone_number"] == "3312345678"
    assert customer["email"] == "john.doe@example.com"
    assert customer["company_name"] == "ABC Foods"


async def test_get_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.get(f"/customers/{customer_id}")

    assert response.status_code == 200
    assert response.json()["id"] == customer_id


async def test_get_customer_not_found(client: AsyncClient):
    response = await client.get(f"/customers/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_list_customers(client: AsyncClient):
    response = await client.get("/customers")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_list_customers_excludes_inactive_by_default(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.get("/customers")
    assert customer_id not in [c["id"] for c in response.json()]

    response = await client.get("/customers", params={"include_inactive": True})
    assert customer_id in [c["id"] for c in response.json()]

    response = await client.patch(f"/customers/{customer_id}/activate")
    assert response.json()["active"] is True

    response = await client.get("/customers")
    assert customer_id in [c["id"] for c in response.json()]


async def test_update_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "3387654321",
            "email": "jane.smith@example.com",
            "company_name": "Jane Smith Inc.",
            "is_company": True,
        },
    )

    customer = response.json()

    assert response.status_code == 200
    assert customer["first_name"] == "Jane"
    assert customer["last_name"] == "Smith"
    assert customer["phone_number"] == "3387654321"
    assert customer["email"] == "jane.smith@example.com"
    assert customer["company_name"] == "Jane Smith Inc."
    assert customer["is_company"] is True


async def test_update_customer_normalizes_input(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}",
        json={
            "first_name": "  jOHN ",
            "last_name": "doe",
            "phone_number": " 3312345678 ",
            "email": "  John.Doe@Example.COM ",
            "company_name": "  ABC Foods  ",
        },
    )
    customer = response.json()

    assert response.status_code == 200
    assert customer["first_name"] == "John"
    assert customer["last_name"] == "Doe"
    assert customer["phone_number"] == "3312345678"
    assert customer["email"] == "john.doe@example.com"
    assert customer["company_name"] == "ABC Foods"


async def test_update_customer_remove_company(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}",
        json={
            "company_name": None,
            "is_company": False,
        },
    )

    customer = response.json()

    assert response.status_code == 200
    assert customer["first_name"] == CUSTOMER_JOHN_DOE_PAYLOAD.get("first_name")
    assert customer["last_name"] == CUSTOMER_JOHN_DOE_PAYLOAD.get("last_name")
    assert customer["phone_number"] == CUSTOMER_JOHN_DOE_PAYLOAD.get("phone_number")
    assert customer["email"] == CUSTOMER_JOHN_DOE_PAYLOAD.get("email")
    assert customer["company_name"] is None
    assert customer["is_company"] is False


async def test_update_customer_add_company(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JANE_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}",
        json={
            "company_name": "Jane Doe Inc.",
            "is_company": True,
        },
    )

    customer = response.json()

    assert response.status_code == 200
    assert customer["first_name"] == CUSTOMER_JANE_DOE_PAYLOAD.get("first_name")
    assert customer["last_name"] == CUSTOMER_JANE_DOE_PAYLOAD.get("last_name")
    assert customer["phone_number"] == CUSTOMER_JANE_DOE_PAYLOAD.get("phone_number")
    assert customer["email"] == CUSTOMER_JANE_DOE_PAYLOAD.get("email")
    assert customer["company_name"] == "Jane Doe Inc."
    assert customer["is_company"] is True


async def test_update_customer_not_found(client: AsyncClient):
    response = await client.patch(
        f"/customers/{uuid.uuid4()}", json=CUSTOMER_JOHN_DOE_PAYLOAD
    )
    assert response.status_code == 404


async def test_activate_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(f"/customers/{customer_id}/activate")

    customer = response.json()

    assert response.status_code == 200
    assert customer["active"] is True
    assert customer["activated_at"] is not None
    assert customer["deactivated_at"] is None


async def test_activate_customer_activated_at(client: AsyncClient):
    activated_at = "2023-01-01"
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}/activate", params={"activated_at": activated_at}
    )

    customer = response.json()

    assert response.status_code == 200
    assert customer["active"] is True
    assert customer["activated_at"] is not None
    assert customer["activated_at"] == activated_at
    assert customer["deactivated_at"] is None


async def test_activate_active_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(f"/customers/{customer_id}/activate")
    assert response.status_code == 200

    response = await client.patch(f"/customers/{customer_id}/activate")
    assert response.status_code == 400


async def test_activate_customer_not_found(client: AsyncClient):
    response = await client.patch(f"/customers/{uuid.uuid4()}/activate")

    assert response.status_code == 404


async def test_deactivate_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(f"/customers/{customer_id}/activate")
    response = await client.patch(f"/customers/{customer_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["activated_at"] is not None
    assert response.json()["deactivated_at"] is not None


async def test_deactivate_customer_deactivate_at(client: AsyncClient):
    deactivated_at = "2023-01-01"
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(f"/customers/{customer_id}/activate")
    response = await client.patch(
        f"/customers/{customer_id}/deactivate",
        params={"deactivated_at": deactivated_at},
    )

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["activated_at"] is not None
    assert response.json()["deactivated_at"] is not None
    assert response.json()["deactivated_at"] == deactivated_at


async def test_deactivate_inactive_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(f"/customers/{customer_id}/deactivate")

    assert response.status_code == 400


async def test_deactivate_customer_not_found(client: AsyncClient):
    response = await client.patch(f"/customers/{uuid.uuid4()}/deactivate")

    assert response.status_code == 404


async def test_delete_customer(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.delete(f"/customers/{customer_id}")
    validation = await client.get(f"/customers/{customer_id}")

    assert response.status_code == 204
    assert validation.status_code == 404


async def test_delete_customer_not_found(client: AsyncClient):
    response = await client.delete(f"/customers/{uuid.uuid4()}")

    assert response.status_code == 404
