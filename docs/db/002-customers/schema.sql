CREATE SCHEMA IF NOT EXISTS "public";
CREATE TYPE "sat_method" AS ENUM ('''PUE''', '''PDD''');
CREATE TABLE "public"."payment_methods" (
    "sat_code" text NOT NULL,
    "sat_method" sat_method NOT NULL,
    "description" text NOT NULL,
    "requires_reference" boolean NOT NULL DEFAULT false,
    PRIMARY KEY ("sat_code")
);
CREATE TABLE "public"."cfdi_uses" (
    "sat_code" text NOT NULL,
    "description" text NOT NULL,
    "applies_to_individual" boolean NOT NULL DEFAULT true,
    "applies_to_company" boolean NOT NULL DEFAULT true,
    PRIMARY KEY ("sat_code")
);
CREATE TABLE "public"."tax_systems" (
    "sat_code" text NOT NULL,
    "description" text NOT NULL,
    "applies_to_individual" boolean NOT NULL DEFAULT true,
    "applies_to_company" boolean NOT NULL DEFAULT true,
    PRIMARY KEY ("sat_code")
);
CREATE TABLE "public"."tax_system_cfdi_uses" (
    "tax_system_code" text NOT NULL,
    "cfdi_use_code" text NOT NULL,
    PRIMARY KEY ("tax_system_code", "cfdi_use_code")
);
CREATE TABLE "public"."sat_product_codes" (
    "sat_code" text NOT NULL,
    "type" text NOT NULL,
    "description" text NOT NULL,
    PRIMARY KEY ("sat_code")
);
CREATE TABLE "public"."customers" (
    "id" uuid NOT NULL DEFAULT 'gen_random_uuid()',
    "first_name" text NOT NULL,
    "last_name" text NOT NULL,
    "company_name" text,
    "is_company" boolean NOT NULL DEFAULT true,
    "rfc" text,
    "tax_system_code" text,
    "default_cfdi_use" text,
    "requires_invoice" boolean NOT NULL DEFAULT false,
    "phone_number" text NOT NULL,
    "email" text,
    "active" boolean NOT NULL DEFAULT false,
    "activated_at" date,
    "deactivated_at" date,
    "created_at" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamptz,
    PRIMARY KEY ("id"),
    CHECK (first_name > 1),
    CHECK (last_name > 1),
    CHECK (length(rfc) in (12, 13)),
    CHECK (phone_number >= 10)
);
-- [REQUIREMENT]: Apply partial unique indexes on 'customer_id' filtered by 'is_default = true' and 'is_billing = true' respectively. Implement via SQLAlchemy __table_args__ using 'postgresql_where' to prevent multiple default/billing addresses per customer.
CREATE TABLE "public"."addresses" (
    "id" uuid NOT NULL DEFAULT 'gen_random_uuid()',
    "customer_id" uuid NOT NULL,
    "street" text NOT NULL,
    "exterior_number" text NOT NULL,
    "interior_number" text,
    "neighborhood" text NOT NULL,
    "city" text NOT NULL,
    "state" text NOT NULL,
    "postal_code" text NOT NULL,
    "country" text NOT NULL,
    "address_notes" text,
    "latitude" numeric(10, 8),
    "longitude" numeric(11, 8),
    "is_default" boolean NOT NULL DEFAULT false,
    "is_billing" boolean NOT NULL DEFAULT false,
    PRIMARY KEY ("id"),
    CHECK (length(postal_code) = 5)
);
COMMENT ON TABLE "public"."addresses" IS '[REQUIREMENT]: Apply partial unique indexes on ''customer_id'' filtered by ''is_default = true'' and ''is_billing = true'' respectively. Implement via SQLAlchemy __table_args__ using ''postgresql_where'' to prevent multiple default/billing addresses per customer.';
-- Foreign key constraints
-- Schema: public
ALTER TABLE "public"."tax_system_cfdi_uses"
ADD CONSTRAINT "fk_tax_system_cfdi_uses_tax_system_code_tax_systems_sat_code" FOREIGN KEY("tax_system_code") REFERENCES "public"."tax_systems"("sat_code");
ALTER TABLE "public"."tax_system_cfdi_uses"
ADD CONSTRAINT "fk_tax_system_cfdi_uses_cfdi_use_code_cfdi_uses_sat_code" FOREIGN KEY("cfdi_use_code") REFERENCES "public"."cfdi_uses"("sat_code");
ALTER TABLE "public"."customers"
ADD CONSTRAINT "fk_customers_tax_system_code_tax_systems_sat_code" FOREIGN KEY("tax_system_code") REFERENCES "public"."tax_systems"("sat_code");
ALTER TABLE "public"."customers"
ADD CONSTRAINT "fk_customers_default_cfdi_use_cfdi_uses_sat_code" FOREIGN KEY("default_cfdi_use") REFERENCES "public"."cfdi_uses"("sat_code");
ALTER TABLE "public"."addresses"
ADD CONSTRAINT "fk_addresses_customer_id_customers_id" FOREIGN KEY("customer_id") REFERENCES "public"."customers"("id");