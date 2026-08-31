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
-- Foreign key constraints
-- Schema: public
ALTER TABLE "public"."tax_system_cfdi_uses"
ADD CONSTRAINT "fk_tax_system_cfdi_uses_tax_system_code_tax_systems_sat_code" FOREIGN KEY("tax_system_code") REFERENCES "public"."tax_systems"("sat_code");
ALTER TABLE "public"."tax_system_cfdi_uses"
ADD CONSTRAINT "fk_tax_system_cfdi_uses_cfdi_use_code_cfdi_uses_sat_code" FOREIGN KEY("cfdi_use_code") REFERENCES "public"."cfdi_uses"("sat_code");