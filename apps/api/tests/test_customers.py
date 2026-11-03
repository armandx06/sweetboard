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

CUSTOMER_ADDRESS_PAYLOAD: dict[str, str] = {
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
    response = await client.post("/customers", json=CUSTOMER_JANE_DOE_PAYLOAD)
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


async def test_create_customer_address(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.post(
        f"/customers/{customer_id}/addresses",
        json=CUSTOMER_ADDRESS_PAYLOAD,
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
    assert address["address_notes"] == CUSTOMER_ADDRESS_PAYLOAD["address_notes"]
    assert address["active"] is True
    assert address["activated_at"] is not None
    assert address["deactivated_at"] is None
    assert address["is_default"] is True
    assert address["is_billing"] is True
    assert address["created_at"] is not None


async def test_create_customer_address_flags_default_to_false(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.post(
        f"/customers/{customer_id}/addresses", json=CUSTOMER_ADDRESS_PAYLOAD
    )

    assert response.status_code == 201
    assert response.json()["is_default"] is False
    assert response.json()["is_billing"] is False


async def test_create_customer_address_not_found(client: AsyncClient):
    response = await client.post(
        f"/customers/{uuid.uuid4()}/addresses", json=CUSTOMER_ADDRESS_PAYLOAD
    )

    assert response.status_code == 404


async def test_get_customer_includes_addresses(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]
    response = await client.post(
        f"/customers/{customer_id}/addresses",
        json=CUSTOMER_ADDRESS_PAYLOAD,
        params={"is_default": True, "is_billing": True},
    )
    address_id = response.json()["id"]

    response = await client.get(f"/customers/{customer_id}")

    addresses = response.json()["addresses"]

    assert response.status_code == 200
    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["street"] == "Av. Reforma"
    assert addresses[0]["is_default"] is True
    assert addresses[0]["is_billing"] is True


async def test_list_customer_addresses(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    first = await client.post(
        f"/customers/{customer_id}/addresses", json=CUSTOMER_ADDRESS_PAYLOAD
    )
    second = await client.post(
        f"/customers/{customer_id}/addresses",
        json={**CUSTOMER_ADDRESS_PAYLOAD, "street": "Calle 2"},
    )

    response = await client.get(f"/customers/{customer_id}/addresses")

    addresses = response.json()
    address_ids = [address["id"] for address in addresses]

    assert response.status_code == 200
    assert len(addresses) == 2
    assert first.json()["id"] in address_ids
    assert second.json()["id"] in address_ids


async def test_list_customer_addresses_not_found(client: AsyncClient):
    response = await client.get(f"/customers/{uuid.uuid4()}/addresses")

    assert response.status_code == 404


async def test_list_customers_includes_addresses(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]
    response = await client.post(
        f"/customers/{customer_id}/addresses", json=CUSTOMER_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.get("/customers", params={"include_inactive": True})

    customer = next(c for c in response.json() if c["id"] == customer_id)

    assert len(customer["addresses"]) == 1
    assert customer["addresses"][0]["id"] == address_id


async def test_update_customer_keeps_addresses(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]
    response = await client.post(
        f"/customers/{customer_id}/addresses", json=CUSTOMER_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}", json={"first_name": "Jane"}
    )

    assert response.status_code == 200
    assert response.json()["addresses"][0]["id"] == address_id


async def test_create_customer_address_replaces_default(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    first = await client.post(
        f"/customers/{customer_id}/addresses",
        json=CUSTOMER_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    second = await client.post(
        f"/customers/{customer_id}/addresses",
        json={**CUSTOMER_ADDRESS_PAYLOAD, "street": "Calle 2"},
        params={"is_default": True},
    )

    response = await client.get(f"/customers/{customer_id}/addresses")

    addresses = response.json()
    defaults = [address for address in addresses if address["is_default"]]

    assert len(defaults) == 1
    assert defaults[0]["id"] == second.json()["id"]
    assert defaults[0]["id"] != first.json()["id"]


async def test_update_customer_address(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]
    response = await client.post(
        f"/customers/{customer_id}/addresses", json=CUSTOMER_ADDRESS_PAYLOAD
    )
    address_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}/addresses/{address_id}",
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


async def test_update_customer_address_replaces_default(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]
    first = await client.post(
        f"/customers/{customer_id}/addresses",
        json=CUSTOMER_ADDRESS_PAYLOAD,
        params={"is_default": True},
    )
    second = await client.post(
        f"/customers/{customer_id}/addresses",
        json={**CUSTOMER_ADDRESS_PAYLOAD, "street": "Calle 2"},
    )

    response = await client.patch(
        f"/customers/{customer_id}/addresses/{second.json()['id']}",
        json={"is_default": True},
    )

    assert response.status_code == 200
    assert response.json()["is_default"] is True

    response = await client.get(f"/customers/{customer_id}/addresses")

    defaults = [address for address in response.json() if address["is_default"]]

    assert len(defaults) == 1
    assert defaults[0]["id"] == second.json()["id"]
    assert defaults[0]["id"] != first.json()["id"]


async def test_update_customer_address_not_found(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.patch(
        f"/customers/{customer_id}/addresses/{uuid.uuid4()}",
        json={"street": "Calle 3"},
    )

    assert response.status_code == 404


async def test_delete_customer_address_deactivates(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]
    response = await client.post(
        f"/customers/{customer_id}/addresses",
        json=CUSTOMER_ADDRESS_PAYLOAD,
        params={"is_default": True, "is_billing": True},
    )
    address_id = response.json()["id"]

    response = await client.delete(
        f"/customers/{customer_id}/addresses/{address_id}"
    )

    assert response.status_code == 204

    response = await client.get(f"/customers/{customer_id}/addresses")

    addresses = response.json()

    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["active"] is False
    assert addresses[0]["deactivated_at"] is not None
    assert addresses[0]["is_default"] is False
    assert addresses[0]["is_billing"] is False


async def test_delete_customer_address_not_found(client: AsyncClient):
    response = await client.post("/customers", json=CUSTOMER_JOHN_DOE_PAYLOAD)
    customer_id = response.json()["id"]

    response = await client.delete(
        f"/customers/{customer_id}/addresses/{uuid.uuid4()}"
    )

    assert response.status_code == 404
