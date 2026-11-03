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

SUPPLIER_ADDRESS_PAYLOAD: dict[str, str] = {
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


async def test_create_supplier_address(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json=SUPPLIER_ADDRESS_PAYLOAD,
        params={"is_default": True, "is_billing": True},
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
    assert address["address_notes"] == SUPPLIER_ADDRESS_PAYLOAD["address_notes"]
    assert address["active"] is True
    assert address["activated_at"] is not None
    assert address["deactivated_at"] is None
    assert address["is_default"] is True
    assert address["is_billing"] is True
    assert address["created_at"] is not None


async def test_create_supplier_address_flags_default_to_false(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.post(
        f"/suppliers/{supplier_id}/addresses", json=SUPPLIER_ADDRESS_PAYLOAD
    )

    assert response.status_code == 201
    assert response.json()["is_default"] is False
    assert response.json()["is_billing"] is False


async def test_create_supplier_address_not_found(client: AsyncClient):
    response = await client.post(
        f"/suppliers/{uuid4()}/addresses", json=SUPPLIER_ADDRESS_PAYLOAD
    )

    assert response.status_code == 404


async def test_get_supplier_includes_addresses(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]
    response = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json=SUPPLIER_ADDRESS_PAYLOAD,
        params={"is_default": True, "is_billing": True},
    )
    address_id = response.json()["id"]

    response = await client.get(f"/suppliers/{supplier_id}")

    addresses = response.json()["addresses"]

    assert response.status_code == 200
    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["street"] == "Av. Reforma"
    assert addresses[0]["is_default"] is True
    assert addresses[0]["is_billing"] is True


async def test_list_supplier_addresses(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    first = await client.post(
        f"/suppliers/{supplier_id}/addresses", json=SUPPLIER_ADDRESS_PAYLOAD
    )
    second = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json={**SUPPLIER_ADDRESS_PAYLOAD, "street": "Calle 2"},
    )

    response = await client.get(f"/suppliers/{supplier_id}/addresses")

    addresses = response.json()
    address_ids = [address["id"] for address in addresses]

    assert response.status_code == 200
    assert len(addresses) == 2
    assert first.json()["id"] in address_ids
    assert second.json()["id"] in address_ids


async def test_list_supplier_addresses_not_found(client: AsyncClient):
    response = await client.get(f"/suppliers/{uuid4()}/addresses")

    assert response.status_code == 404


async def test_list_suppliers_includes_addresses(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]
    response = await client.post(
        f"/suppliers/{supplier_id}/addresses", json=SUPPLIER_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.get("/suppliers", params={"include_inactive": True})

    supplier = next(s for s in response.json() if s["id"] == supplier_id)

    assert len(supplier["addresses"]) == 1
    assert supplier["addresses"][0]["id"] == address_id


async def test_update_supplier_keeps_addresses(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]
    response = await client.post(
        f"/suppliers/{supplier_id}/addresses", json=SUPPLIER_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}", json={"first_name": "Jane"}
    )

    assert response.status_code == 200
    assert response.json()["addresses"][0]["id"] == address_id


async def test_create_supplier_address_replaces_default(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    first = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json=SUPPLIER_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    second = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json={**SUPPLIER_ADDRESS_PAYLOAD, "street": "Calle 2"},
        params={"is_default": True},
    )

    response = await client.get(f"/suppliers/{supplier_id}/addresses")

    addresses = response.json()
    defaults = [address for address in addresses if address["is_default"]]

    assert len(defaults) == 1
    assert defaults[0]["id"] == second.json()["id"]
    assert defaults[0]["id"] != first.json()["id"]


async def test_update_supplier_address(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]
    response = await client.post(
        f"/suppliers/{supplier_id}/addresses", json=SUPPLIER_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}/addresses/{address_id}",
        json={
            "street": "Calle 3",
            "address_notes": None,
            "is_default": True,
            "is_billing": True,
        },
    )

    address = response.json()

    assert response.status_code == 200
    assert address["id"] == address_id
    assert address["street"] == "Calle 3"
    assert address["address_notes"] is None
    assert address["is_default"] is True
    assert address["is_billing"] is True
    assert address["updated_at"] is not None


async def test_update_supplier_address_replaces_default(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]
    first = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json=SUPPLIER_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    second = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json={**SUPPLIER_ADDRESS_PAYLOAD, "street": "Calle 2"},
    )

    response = await client.patch(
        f"/suppliers/{supplier_id}/addresses/{second.json()['id']}",
        json={"is_default": True},
    )

    assert response.status_code == 200
    assert response.json()["is_default"] is True

    response = await client.get(f"/suppliers/{supplier_id}/addresses")

    defaults = [address for address in response.json() if address["is_default"]]

    assert len(defaults) == 1
    assert defaults[0]["id"] == second.json()["id"]
    assert defaults[0]["id"] != first.json()["id"]


async def test_update_supplier_address_not_found(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.patch(
        f"/suppliers/{supplier_id}/addresses/{uuid4()}",
        json={"street": "Calle 3"},
    )

    assert response.status_code == 404


async def test_delete_supplier_address_deactivates(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]
    response = await client.post(
        f"/suppliers/{supplier_id}/addresses",
        json=SUPPLIER_ADDRESS_PAYLOAD,
        params={"is_default": True, "is_billing": True},
    )
    address_id = response.json()["id"]

    response = await client.delete(
        f"/suppliers/{supplier_id}/addresses/{address_id}"
    )

    assert response.status_code == 204

    response = await client.get(f"/suppliers/{supplier_id}/addresses")

    addresses = response.json()

    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["active"] is False
    assert addresses[0]["deactivated_at"] is not None
    assert addresses[0]["is_default"] is False
    assert addresses[0]["is_billing"] is False


async def test_delete_supplier_address_not_found(client: AsyncClient):
    response = await client.post("/suppliers", json=SUPPLIER_JOHN_DOE_PAYLOAD)
    supplier_id = response.json()["id"]

    response = await client.delete(
        f"/suppliers/{supplier_id}/addresses/{uuid4()}"
    )

    assert response.status_code == 404
