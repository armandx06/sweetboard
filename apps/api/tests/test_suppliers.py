from uuid import uuid4

from httpx import AsyncClient

from tests.conftest import JOHN_DOE_PAYLOAD

SUPPLIER_JOHN_DOE_PAYLOAD: dict[str, str | bool | int | None] = {
    **JOHN_DOE_PAYLOAD,
    "rfc": "XAXX010101000",
    "company_name": "John Doe Inc.",
    "is_company": True,
    "provide_invoice": True,
    "lead_time_days": 5,
    "minimum_order_value": "100.00",
}


async def test_create_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)

    supplier = response.json()

    assert response.status_code == 201
    assert supplier["first_name"] == "John"
    assert supplier["last_name"] == "Doe"
    assert supplier["phone_number"] == "3312345678"
    assert supplier["email"] == "john.doe@example.com"
    assert supplier["rfc"] == "XAXX010101000"
    assert supplier["company_name"] == "John Doe Inc."
    assert supplier["is_company"] == True
    assert supplier["provide_invoice"] == True
    assert supplier["lead_time_days"] == 5
    assert supplier["minimum_order_value"] == "100.00"
    assert supplier["active"] == False
    assert supplier["activated_at"] is None
    assert supplier["deactivated_at"] is None
    assert supplier["created_at"] is not None
    assert supplier["updated_at"] is None


async def test_create_supplier_normalizes_input(client: AsyncClient):
    response = await client.post(
        "/suppliers",
        json={
            **SUPPLIER_JOHN_DOE_PAYLOAD,
            "first_name": "  John  ",
            "last_name": "  Doe  ",
            "phone_number": "  3312345678  ",
            "email": "  john.doe@example.com  ",
            "rfc": "  Xaxx010101000  ",
            "company_name": "  John Doe Inc.  ",
        },
    )
    supplier = response.json()

    assert response.status_code == 201
    assert supplier["first_name"] == "John"
    assert supplier["last_name"] == "Doe"
    assert supplier["phone_number"] == "3312345678"
    assert supplier["email"] == "john.doe@example.com"
    assert supplier["rfc"] == "XAXX010101000"
    assert supplier["company_name"] == "John Doe Inc."


async def test_get_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.get(f"/suppliers/{supplier_id}")

    assert response.status_code == 200
    assert response.json()["id"] == supplier_id


async def test_get_supplier_not_found(client: AsyncClient):
    response = await client.get(f"/suppliers/{uuid4()}")

    assert response.status_code == 404


async def test_list_suppliers(client: AsyncClient):
    response = await client.get("/suppliers")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_list_suppliers_excludes_inactive_by_default(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.get("/suppliers")
    assert supplier_id not in [s["id"] for s in response.json()]

    response = await client.get("/suppliers", params={"include_inactive": True})
    assert supplier_id in [s["id"] for s in response.json()]

    response = await client.patch(f"/suppliers/{supplier_id}/activate")
    assert response.json()["active"] == True

    response = await client.get("/suppliers")
    assert supplier_id in [s["id"] for s in response.json()]


async def test_update_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "3387654321",
            "email": "jane.smith@example.com",
            "rfc": "XEXX010101000",
            "company_name": None,
            "is_company": False,
            "provide_invoice": False,
            "lead_time_days": 0,
            "minimum_order_value": "50.00",
        },
    )

    supplier = response.json()

    assert response.status_code == 200
    assert supplier["first_name"] == "Jane"
    assert supplier["last_name"] == "Smith"
    assert supplier["phone_number"] == "3387654321"
    assert supplier["email"] == "jane.smith@example.com"
    assert supplier["rfc"] == "XEXX010101000"
    assert supplier["company_name"] is None
    assert supplier["is_company"] is False
    assert supplier["provide_invoice"] is False
    assert supplier["lead_time_days"] == 0
    assert supplier["minimum_order_value"] == "50.00"


async def test_update_supplier_normalizes_input(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}",
        json={
            "first_name": "  JoHN  ",
            "last_name": "  Doe  ",
            "phone_number": "  3312345678  ",
            "email": "  John.doe@example.com  ",
            "rfc": "  Xaxx010101000  ",
            "company_name": "  John Doe Inc.  ",
        },
    )

    supplier = response.json()

    assert response.status_code == 200
    assert supplier["first_name"] == "John"
    assert supplier["last_name"] == "Doe"
    assert supplier["phone_number"] == "3312345678"
    assert supplier["email"] == "john.doe@example.com"
    assert supplier["rfc"] == "XAXX010101000"
    assert supplier["company_name"] == "John Doe Inc."


async def test_update_supplier_remove_company(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}",
        json={"company_name": None, "is_company": False},
    )

    supplier = response.json()

    assert response.status_code == 200
    assert supplier["first_name"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("first_name")
    assert supplier["last_name"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("last_name")
    assert supplier["phone_number"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("phone_number")
    assert supplier["email"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("email")
    assert supplier["company_name"] is None
    assert supplier["is_company"] is False


async def test_update_supplier_add_company(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}",
        json={"company_name": "John Doe Inc.", "is_company": True},
    )

    supplier = response.json()

    assert response.status_code == 200
    assert supplier["first_name"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("first_name")
    assert supplier["last_name"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("last_name")
    assert supplier["phone_number"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("phone_number")
    assert supplier["email"] == SUPPLIER_JOHN_DOE_PAYLOAD.get("email")
    assert supplier["company_name"] == "John Doe Inc."
    assert supplier["is_company"] is True


async def test_update_invalid_rfc(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}",
        json={"rfc": "Invalid RFC"},
    )

    assert response.status_code == 422


async def test_update_supplier_negative_lead_time(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}", json={"lead_time_days": -1}
    )

    assert response.status_code == 422


async def test_update_supplier_not_found(client: AsyncClient):
    response = await client.patch(
        f"/suppliers/{uuid4()}", json=SUPPLIER_JOHN_DOE_PAYLOAD
    )
    assert response.status_code == 404


async def test_activate_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(f"/suppliers/{supplier_id}/activate")

    supplier = response.json()

    assert response.status_code == 200
    assert supplier["active"] is True
    assert supplier["activated_at"] is not None
    assert supplier["deactivated_at"] is None


async def test_activate_supplier_activated_at(client: AsyncClient):
    activated_at = "2023-01-01"
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}/activate", params={"activated_at": activated_at}
    )

    supplier = response.json()

    assert response.status_code == 200
    assert supplier["active"] is True
    assert supplier["activated_at"] is not None
    assert supplier["activated_at"] == activated_at
    assert supplier["deactivated_at"] is None


async def test_activate_active_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(f"/suppliers/{supplier_id}/activate")
    assert response.status_code == 200

    response = await client.patch(f"/suppliers/{supplier_id}/activate")
    assert response.status_code == 400


async def test_activate_supplier_not_found(client: AsyncClient):
    response = await client.patch(f"/suppliers/{uuid4()}/activate")

    assert response.status_code == 404


async def test_deactivate_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(f"/suppliers/{supplier_id}/activate")
    response = await client.patch(f"/suppliers/{supplier_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["deactivated_at"] is not None
    assert response.json()["activated_at"] is not None


async def test_deactivate_supplier_deactivate_at(client: AsyncClient):
    deactivated_at = "2023-01-01"
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(f"/suppliers/{supplier_id}/activate")
    response = await client.patch(
        f"/suppliers/{supplier_id}/deactivate",
        params={"deactivated_at": deactivated_at},
    )

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["activated_at"] is not None
    assert response.json()["deactivated_at"] is not None
    assert response.json()["deactivated_at"] == deactivated_at


async def test_deactivate_inactive_customer(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(f"/suppliers/{supplier_id}/deactivate")

    assert response.status_code == 400


async def test_deactivate_customer_not_found(client: AsyncClient):
    response = await client.patch(f"/suppliers/{uuid4()}/deactivate")

    assert response.status_code == 404


async def test_delete_supplier(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.delete(f"/suppliers/{supplier_id}")
    validation = await client.get(f"/suppliers/{supplier_id}")

    assert response.status_code == 204
    assert validation.status_code == 404


async def test_delete_customer_not_found(client: AsyncClient):
    response = await client.delete(f"/suppliers/{uuid4()}")

    assert response.status_code == 404
