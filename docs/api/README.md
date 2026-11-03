# SWEETBOARD API REFERENCE

HTTP reference for the Sweetboard API as currently implemented. The live OpenAPI contract is always available at <http://localhost:8000/openapi.json> and rendered at <http://localhost:8000/docs>.

- No authentication is required yet.
- There is no version prefix: routes are mounted at the root.
- The API manages employees, customers, suppliers, and shared addresses.
- Schema and domain decisions are documented in [`docs/adr/`](../adr/) and [`docs/db/README.md`](../db/README.md).

## Base URL and formats

| Item            | Value                                        |
| --------------- | -------------------------------------------- |
| Base URL        | `http://localhost:8000`                      |
| Content type    | `application/json`                           |
| Dates           | ISO 8601 (`YYYY-MM-DD`)                      |
| Date-times      | ISO 8601 with timezone                       |
| Identifiers     | UUID strings                                 |
| Decimals        | JSON strings or numbers accepted by Pydantic |
| Empty responses | `204 No Content`, no body                    |

## Health

| Method | Path      | Description                               | Success |
| ------ | --------- | ----------------------------------------- | ------- |
| `GET`  | `/health` | Check the API and its database connection | `200`   |

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "db_result": 1
}
```

## Conventions

### Normalization

The API normalizes input before persisting it:

- `first_name`, `last_name`: trimmed and title-cased.
- `phone_number`: trimmed.
- `email`: trimmed and lower-cased; an empty value becomes `null`.
- `company_name`: trimmed; an empty value becomes `null`.
- `rfc`: trimmed and upper-cased.
- `street`, `exterior_number`, `interior_number`, `neighborhood`, `city`, `state`, `country`, `postal_code`, `address_notes`: stored as received; trim them in the client if needed.

### Listing and soft deletes

- `GET /employees`, `GET /customers`, and `GET /suppliers` return only active records by default.
- Pass `include_inactive=true` to include deactivated records.
- `PATCH /{resource}/{id}/deactivate` deactivates a record and records its termination/deactivation date.
- `DELETE /{resource}/{id}` is a real, physical deletion. For employees it is intended only for records that were never hired, but the guard described in [ADR 0007](../adr/0007-employee-identity-credentials-and-lifecycle.md) is **not implemented yet**: the current endpoint deletes any existing employee.

### Address semantics

Addresses are shared rows. The link tables store role-specific flags.

- `POST /{resource}/{id}/addresses` always creates a **new** `addresses` row and links it. It does not reuse an existing physical address.
- `PATCH /{resource}/{id}/addresses/{address_id}` edits the shared `addresses` row and the link flags. The change affects every customer, supplier, or employee linked to that address.
- To move one subject to a different physical location, create a new address and link it instead of editing the shared row.
- `DELETE /{resource}/{id}/addresses/{address_id}` is a **soft delete of the link**, not of the address. It sets `active = false`, `deactivated_at = today`, and clears `is_default`; customer and supplier links also clear `is_billing`. The `addresses` row remains.
- Address lists return every link, including inactive ones. Check the `active` field.
- At most one link per subject can have `is_default = true`. Setting a new default clears the previous one.
- `is_billing` exists only on customer and supplier links. Employee addresses have `is_default` but no `is_billing`.

### Error responses

Domain errors return:

```json
{
  "detail": "Customer not found"
}
```

Validation errors (`422`) use FastAPI's standard shape instead: `detail` is an array of field-level errors.

| Status | Meaning                      | Sources                                                                                                                                     |
| ------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `400`  | Invalid lifecycle transition | `ActiveEmployee`, `InactiveEmployee`, `ActiveCustomer`, `InactiveCustomer`, `ActiveSupplier`, `InactiveSupplier`                            |
| `404`  | Resource or link not found   | `EmployeeNotFound`, `EmployeeAddressNotFound`, `CustomerNotFound`, `CustomerAddressNotFound`, `SupplierNotFound`, `SupplierAddressNotFound` |
| `409`  | Database integrity conflict  | `IntegrityError`, e.g. a username race or invalid data that reaches the database                                                            |
| `422`  | Request validation failed    | Pydantic/FastAPI validation                                                                                                                 |
| `500`  | Unexpected server error      | Unhandled exception fallback                                                                                                                |

Common `400` messages:

- `Employee is already active`
- `Employee is inactive or has not yet been hired.`
- `Customer is already active`
- `Customer is inactive`
- `Supplier is already active`
- `Supplier is inactive`

Common `404` messages:

- `Employee not found`
- `Employee address not found`
- `Customer not found`
- `Customer address not found`
- `Supplier not found`
- `Supplier address not found`

`409` returns a generic message: `An unexpected error has occurred, please try again.`

## Employees

Base path: `/employees`

| Method   | Path                                              | Description                               | Success |
| -------- | ------------------------------------------------- | ----------------------------------------- | ------- |
| `POST`   | `/employees`                                      | Create an employee                        | `201`   |
| `GET`    | `/employees`                                      | List employees (`include_inactive` query) | `200`   |
| `GET`    | `/employees/{employee_id}`                        | Get one employee                          | `200`   |
| `PATCH`  | `/employees/{employee_id}`                        | Update contact details                    | `200`   |
| `PATCH`  | `/employees/{employee_id}/activate`               | Activate an inactive employee             | `200`   |
| `PATCH`  | `/employees/{employee_id}/deactivate`             | Deactivate an active employee             | `200`   |
| `POST`   | `/employees/{employee_id}/reset-password`         | Generate a new temporary password         | `200`   |
| `DELETE` | `/employees/{employee_id}`                        | Permanently delete an employee            | `204`   |
| `POST`   | `/employees/{employee_id}/addresses`              | Create and link an address                | `201`   |
| `GET`    | `/employees/{employee_id}/addresses`              | List linked addresses                     | `200`   |
| `PATCH`  | `/employees/{employee_id}/addresses/{address_id}` | Update an address and its link flags      | `200`   |
| `DELETE` | `/employees/{employee_id}/addresses/{address_id}` | Soft-delete the address link              | `204`   |

### Employee create body

| Field          | Type           | Required | Notes                   |
| -------------- | -------------- | -------- | ----------------------- |
| `first_name`   | string         | yes      | Trimmed and title-cased |
| `last_name`    | string         | yes      | Trimmed and title-cased |
| `birth_date`   | date           | yes      | `YYYY-MM-DD`            |
| `phone_number` | string         | yes      | Trimmed                 |
| `email`        | string \| null | no       | Trimmed and lower-cased |

The server generates `username` and `password`. The username combines the first two letters of the first name, the first two letters of the last name, the two-digit birth year, and a two-digit sequence (for example `JODO9001`). The temporary password is 12 characters long and mixes letters, digits, and punctuation. The plaintext password is returned **only** in the create response as `temporary_password`. The stored hash is never returned.

New employees start with `active = false`, `hire_date = null`, and `termination_date = null`.

### Employee read fields

| Field                     | Type             | Notes                       |
| ------------------------- | ---------------- | --------------------------- |
| `id`                      | UUID             |                             |
| `first_name`, `last_name` | string           |                             |
| `birth_date`              | date             |                             |
| `phone_number`            | string           |                             |
| `email`                   | string \| null   |                             |
| `username`                | string           | Server-generated, unique    |
| `addresses`               | array            | `EmployeeAddressRead[]`     |
| `hire_date`               | date \| null     | Set by activation           |
| `termination_date`        | date \| null     | Set by deactivation         |
| `active`                  | boolean          | Soft-delete/lifecycle state |
| `last_login_at`           | datetime \| null |                             |
| `last_password_change_at` | datetime \| null |                             |
| `created_at`              | datetime         |                             |
| `updated_at`              | datetime \| null |                             |

The create response adds `temporary_password: string`.

### Employee update body

Only contact fields are accepted:

| Field          | Type           | Required |
| -------------- | -------------- | -------- |
| `first_name`   | string \| null | no       |
| `last_name`    | string \| null | no       |
| `phone_number` | string \| null | no       |
| `email`        | string \| null | no       |

Changing `first_name` or `last_name` regenerates the username.

### Employee lifecycle query parameters

| Endpoint               | Parameter          | Type | Default | Behavior                                                          |
| ---------------------- | ------------------ | ---- | ------- | ----------------------------------------------------------------- |
| `PATCH .../activate`   | `hire_date`        | date | today   | Sets `active = true`, sets `hire_date`, clears `termination_date` |
| `PATCH .../deactivate` | `termination_date` | date | today   | Sets `active = false`, sets `termination_date`                    |

Activating an already active employee returns `400`. Deactivating an inactive employee returns `400`.

### Employee address bodies

`POST` body is `AddressCreateBody` with the query parameter `is_default` (boolean, default `false`). `PATCH` body is `EmployeeAddressUpdateBody`, which accepts address fields plus `is_default`. See [Address contract](#address-contract).

## Customers

Base path: `/customers`

| Method   | Path                                              | Description                               | Success |
| -------- | ------------------------------------------------- | ----------------------------------------- | ------- |
| `POST`   | `/customers`                                      | Create a customer                         | `201`   |
| `GET`    | `/customers`                                      | List customers (`include_inactive` query) | `200`   |
| `GET`    | `/customers/{customer_id}`                        | Get one customer                          | `200`   |
| `PATCH`  | `/customers/{customer_id}`                        | Update a customer                         | `200`   |
| `PATCH`  | `/customers/{customer_id}/activate`               | Activate an inactive customer             | `200`   |
| `PATCH`  | `/customers/{customer_id}/deactivate`             | Deactivate an active customer             | `200`   |
| `DELETE` | `/customers/{customer_id}`                        | Permanently delete a customer             | `204`   |
| `POST`   | `/customers/{customer_id}/addresses`              | Create and link an address                | `201`   |
| `GET`    | `/customers/{customer_id}/addresses`              | List linked addresses                     | `200`   |
| `PATCH`  | `/customers/{customer_id}/addresses/{address_id}` | Update an address and its link flags      | `200`   |
| `DELETE` | `/customers/{customer_id}/addresses/{address_id}` | Soft-delete the address link              | `204`   |

### Customer create body

| Field          | Type           | Required | Default | Notes                   |
| -------------- | -------------- | -------- | ------- | ----------------------- |
| `first_name`   | string         | yes      |         | Trimmed and title-cased |
| `last_name`    | string         | yes      |         | Trimmed and title-cased |
| `phone_number` | string         | yes      |         | Trimmed                 |
| `email`        | string \| null | no       | `null`  | Lower-cased             |
| `company_name` | string \| null | no       | `null`  | Trimmed                 |
| `is_company`   | boolean        | no       | `false` |                         |

### Customer read fields

`id`, `first_name`, `last_name`, `phone_number`, `email`, `addresses`, `company_name`, `is_company`, `active`, `activated_at`, `deactivated_at`, `created_at`, `updated_at`.

New customers start with `active = false`, `activated_at = null`, and `deactivated_at = null`.

### Customer update body

All fields are optional: `first_name`, `last_name`, `phone_number`, `email`, `company_name`, `is_company`. Send `company_name: null` and `is_company: false` to remove company data.

### Customer lifecycle query parameters

| Endpoint               | Parameter        | Type | Default | Behavior                                                           |
| ---------------------- | ---------------- | ---- | ------- | ------------------------------------------------------------------ |
| `PATCH .../activate`   | `activated_at`   | date | today   | Sets `active = true`, sets `activated_at`, clears `deactivated_at` |
| `PATCH .../deactivate` | `deactivated_at` | date | today   | Sets `active = false`, sets `deactivated_at`                       |

Activating an already active customer returns `400`. Deactivating an inactive customer returns `400`.

### Customer address bodies

`POST` body is `AddressCreateBody` with query parameters `is_default` and `is_billing` (both boolean, default `false`). `PATCH` body is `CustomerSupplierAddressUpdateBody`, which accepts address fields plus `is_default` and `is_billing`.

## Suppliers

Base path: `/suppliers`

| Method   | Path                                              | Description                               | Success |
| -------- | ------------------------------------------------- | ----------------------------------------- | ------- |
| `POST`   | `/suppliers`                                      | Create a supplier                         | `201`   |
| `GET`    | `/suppliers`                                      | List suppliers (`include_inactive` query) | `200`   |
| `GET`    | `/suppliers/{supplier_id}`                        | Get one supplier                          | `200`   |
| `PATCH`  | `/suppliers/{supplier_id}`                        | Update a supplier                         | `200`   |
| `PATCH`  | `/suppliers/{supplier_id}/activate`               | Activate an inactive supplier             | `200`   |
| `PATCH`  | `/suppliers/{supplier_id}/deactivate`             | Deactivate an active supplier             | `200`   |
| `DELETE` | `/suppliers/{supplier_id}`                        | Permanently delete a supplier             | `204`   |
| `POST`   | `/suppliers/{supplier_id}/addresses`              | Create and link an address                | `201`   |
| `GET`    | `/suppliers/{supplier_id}/addresses`              | List linked addresses                     | `200`   |
| `PATCH`  | `/suppliers/{supplier_id}/addresses/{address_id}` | Update an address and its link flags      | `200`   |
| `DELETE` | `/suppliers/{supplier_id}/addresses/{address_id}` | Soft-delete the address link              | `204`   |

### Supplier create body

| Field                 | Type           | Required | Default | Notes                                      |
| --------------------- | -------------- | -------- | ------- | ------------------------------------------ |
| `first_name`          | string         | yes      |         | Trimmed and title-cased                    |
| `last_name`           | string         | yes      |         | Trimmed and title-cased                    |
| `phone_number`        | string         | yes      |         | Trimmed                                    |
| `email`               | string \| null | no       | `null`  | Lower-cased                                |
| `rfc`                 | string \| null | no       | `null`  | Trimmed, upper-cased, validated by pattern |
| `company_name`        | string \| null | no       | `null`  | Trimmed                                    |
| `is_company`          | boolean        | no       | `false` |                                            |
| `provide_invoice`     | boolean        | no       | `false` |                                            |
| `lead_time_days`      | integer        | no       | `0`     | Must be `>= 0`                             |
| `minimum_order_value` | decimal        | no       | `0.0`   | Must be `>= 0`                             |

RFC pattern: `^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$` (12 or 13 characters). Values are normalized to uppercase before validation. The examples in the tests use `XAXX010101000`.

### Supplier read fields

`id`, `first_name`, `last_name`, `phone_number`, `email`, `addresses`, `rfc`, `company_name`, `is_company`, `provide_invoice`, `lead_time_days`, `minimum_order_value`, `active`, `activated_at`, `deactivated_at`, `created_at`, `updated_at`.

New suppliers start with `active = false`, `activated_at = null`, and `deactivated_at = null`.

### Supplier update body

All create fields are optional on update, including `rfc`, `company_name`, `is_company`, `provide_invoice`, `lead_time_days`, and `minimum_order_value`. Use `company_name: null` and `is_company: false` to remove company data.

### Supplier lifecycle query parameters

| Endpoint               | Parameter        | Type | Default | Behavior                                                           |
| ---------------------- | ---------------- | ---- | ------- | ------------------------------------------------------------------ |
| `PATCH .../activate`   | `activated_at`   | date | today   | Sets `active = true`, sets `activated_at`, clears `deactivated_at` |
| `PATCH .../deactivate` | `deactivated_at` | date | today   | Sets `active = false`, sets `deactivated_at`                       |

Activating an already active supplier returns `400`. Deactivating an inactive supplier returns `400`.

### Supplier address bodies

`POST` body is `AddressCreateBody` with query parameters `is_default` and `is_billing` (both boolean, default `false`). `PATCH` body is `CustomerSupplierAddressUpdateBody`, which accepts address fields plus `is_default` and `is_billing`.

## Address contract

All three roles share the same physical `addresses` rows and the same create/read payload shape. The link-specific fields differ by role.

### `AddressCreateBody`

| Field             | Type            | Required | Notes                     |
| ----------------- | --------------- | -------- | ------------------------- |
| `street`          | string          | yes      |                           |
| `exterior_number` | string          | yes      |                           |
| `interior_number` | string \| null  | no       |                           |
| `neighborhood`    | string          | yes      |                           |
| `city`            | string          | yes      |                           |
| `state`           | string          | yes      |                           |
| `country`         | string          | yes      |                           |
| `postal_code`     | string          | yes      |                           |
| `address_notes`   | string \| null  | no       |                           |
| `latitude`        | decimal \| null | no       | Stored as `numeric(10,8)` |
| `longitude`       | decimal \| null | no       | Stored as `numeric(11,8)` |

### `AddressRead`

`AddressRead` adds `id` (UUID), `created_at` (datetime), and `updated_at` (datetime | null) to the create fields.

### `CustomerSupplierAddressRead`

Extends `AddressRead` with:

| Field            | Type         | Notes                             |
| ---------------- | ------------ | --------------------------------- |
| `is_default`     | boolean      | At most one per customer/supplier |
| `is_billing`     | boolean      | Customer and supplier links only  |
| `active`         | boolean      | Link lifecycle state              |
| `activated_at`   | date \| null | Set when the link is created      |
| `deactivated_at` | date \| null | Set when the link is soft-deleted |

### `EmployeeAddressRead`

Extends `AddressRead` with `is_default`, `active`, `activated_at`, and `deactivated_at`. It has **no** `is_billing`.

### Update bodies

`AddressUpdateBody` accepts every address field optionally. `CustomerSupplierAddressUpdateBody` adds optional `is_default` and `is_billing`; `EmployeeAddressUpdateBody` adds optional `is_default` only.

Send only the fields that should change. Nullable fields can be cleared with `null`, but do not send `null` for required database columns such as `street`, `city`, or `postal_code`; that reaches the database and produces a `409`.

### Listing addresses

`GET /{role}/{id}/addresses` returns every link for the subject, including links with `active = false`. Clients should filter by `active` when they only need current addresses. A missing subject returns `404`; a missing link on `PATCH` or `DELETE` returns the role-specific address `404`.

## Examples

### Create an employee

```bash
curl -X POST http://localhost:8000/employees \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-01-01",
    "phone_number": "3312345678",
    "email": "john.doe@example.com"
  }'
```

```json
{
  "id": "4f4f0f0e-2e6b-4b8a-9a3e-1b2c3d4e5f60",
  "first_name": "John",
  "last_name": "Doe",
  "birth_date": "1990-01-01",
  "phone_number": "3312345678",
  "username": "JODO9001",
  "email": "john.doe@example.com",
  "addresses": [],
  "hire_date": null,
  "termination_date": null,
  "active": false,
  "last_login_at": null,
  "last_password_change_at": null,
  "created_at": "2026-11-03T18:00:00Z",
  "updated_at": null,
  "temporary_password": "A1b2C3d4E5f6"
}
```

### Create a customer address

```bash
curl -X POST 'http://localhost:8000/customers/8d3b1f7a-3c2d-4e5f-8a9b-0c1d2e3f4a5b/addresses?is_default=true&is_billing=true' \
  -H 'Content-Type: application/json' \
  -d '{
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
    "longitude": "-99.13320900"
  }'
```

```json
{
  "id": "0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
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
  "created_at": "2026-11-03T18:05:00Z",
  "updated_at": null,
  "is_default": true,
  "is_billing": true,
  "active": true,
  "activated_at": "2026-11-03",
  "deactivated_at": null
}
```

### Update an address and promote it to default

```bash
curl -X PATCH http://localhost:8000/suppliers/1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d/addresses/9f8e7d6c-5b4a-4c3d-8e2f-1a0b9c8d7e6f \
  -H 'Content-Type: application/json' \
  -d '{
    "street": "Av. Insurgentes Sur 1234",
    "is_default": true,
    "is_billing": false
  }'
```

The response is the updated `CustomerSupplierAddressRead`. If another supplier address was the default, it is cleared first.

### Deactivate an employee

```bash
curl -X PATCH 'http://localhost:8000/employees/4f4f0f0e-2e6b-4b8a-9a3e-1b2c3d4e5f60/deactivate?termination_date=2026-11-03'
```

The response is the updated `EmployeeRead` with `active = false` and `termination_date = "2026-11-03"`.

---

See [`apps/api/README.md`](../../apps/api/README.md) for local setup, tests, and migrations. See [`README.md`](../../README.md) for the full stack and Docker workflow.
