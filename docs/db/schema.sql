-- Sweetboard database schema snapshot.
-- Generated from the development database with pg_dump (schema only).
-- Alembic revision at generation time: c4f8a1d2b6e3 (head).
--
-- Regenerate from the repository root:
--   docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
--     --project-directory . exec -T db sh -c \
--     'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --schema-only --no-owner --no-privileges --no-tablespaces' \
--     | sed '/^\\restrict /d; /^\\unrestrict /d' > docs/db/schema.sql
--
-- This file describes the implemented application schema. See README.md for
-- business rules, relationships, and the migration history.

--
-- PostgreSQL database dump
--


-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_table_access_method = heap;

--
-- Name: addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.addresses (
    street character varying NOT NULL,
    exterior_number character varying NOT NULL,
    interior_number character varying,
    neighborhood character varying NOT NULL,
    city character varying NOT NULL,
    state character varying NOT NULL,
    country character varying NOT NULL,
    postal_code character varying NOT NULL,
    address_notes character varying,
    latitude numeric(10,8),
    longitude numeric(11,8),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: customer_addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customer_addresses (
    customer_id uuid NOT NULL,
    address_id uuid NOT NULL,
    is_default boolean NOT NULL,
    is_billing boolean NOT NULL,
    active boolean DEFAULT true NOT NULL,
    activated_at date,
    deactivated_at date
);


--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    company_name character varying,
    is_company boolean NOT NULL,
    active boolean NOT NULL,
    activated_at date,
    deactivated_at date,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    phone_number character varying NOT NULL,
    email character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


--
-- Name: employee_addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_addresses (
    employee_id uuid NOT NULL,
    address_id uuid NOT NULL,
    is_default boolean NOT NULL,
    active boolean DEFAULT true NOT NULL,
    activated_at date,
    deactivated_at date
);


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    birth_date date NOT NULL,
    phone_number character varying NOT NULL,
    email character varying,
    hire_date date,
    termination_date date,
    active boolean NOT NULL,
    last_login_at timestamp with time zone,
    last_password_change_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


--
-- Name: supplier_addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supplier_addresses (
    supplier_id uuid NOT NULL,
    address_id uuid NOT NULL,
    is_default boolean NOT NULL,
    is_billing boolean NOT NULL,
    active boolean DEFAULT true NOT NULL,
    activated_at date,
    deactivated_at date
);


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suppliers (
    rfc character varying,
    company_name character varying,
    is_company boolean NOT NULL,
    provide_invoice boolean NOT NULL,
    lead_time_days integer NOT NULL,
    minimum_order_value numeric(10,2) NOT NULL,
    active boolean NOT NULL,
    activated_at date,
    deactivated_at date,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    phone_number character varying NOT NULL,
    email character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    CONSTRAINT ck_suppliers_lead_time_days_non_negative CHECK ((lead_time_days >= 0)),
    CONSTRAINT ck_suppliers_min_order_value_non_negative CHECK ((minimum_order_value >= (0)::numeric)),
    CONSTRAINT ck_suppliers_rfc_length CHECK (((length((rfc)::text) >= 12) AND (length((rfc)::text) <= 13)))
);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: addresses pk_addresses; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT pk_addresses PRIMARY KEY (id);


--
-- Name: customer_addresses pk_customer_addresses; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_addresses
    ADD CONSTRAINT pk_customer_addresses PRIMARY KEY (customer_id, address_id);


--
-- Name: customers pk_customers; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT pk_customers PRIMARY KEY (id);


--
-- Name: employee_addresses pk_employee_addresses; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_addresses
    ADD CONSTRAINT pk_employee_addresses PRIMARY KEY (employee_id, address_id);


--
-- Name: employees pk_employees; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT pk_employees PRIMARY KEY (id);


--
-- Name: supplier_addresses pk_supplier_addresses; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_addresses
    ADD CONSTRAINT pk_supplier_addresses PRIMARY KEY (supplier_id, address_id);


--
-- Name: suppliers pk_suppliers; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT pk_suppliers PRIMARY KEY (id);


--
-- Name: employees uq_employees_username; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT uq_employees_username UNIQUE (username);


--
-- Name: ix_customer_addresses_address_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customer_addresses_address_id ON public.customer_addresses USING btree (address_id);


--
-- Name: ix_employee_addresses_address_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employee_addresses_address_id ON public.employee_addresses USING btree (address_id);


--
-- Name: ix_supplier_addresses_address_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_supplier_addresses_address_id ON public.supplier_addresses USING btree (address_id);


--
-- Name: uq_customer_addresses_one_default; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_customer_addresses_one_default ON public.customer_addresses USING btree (customer_id) WHERE (is_default = true);


--
-- Name: uq_employee_addresses_one_default; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_employee_addresses_one_default ON public.employee_addresses USING btree (employee_id) WHERE (is_default = true);


--
-- Name: uq_supplier_addresses_one_default; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_supplier_addresses_one_default ON public.supplier_addresses USING btree (supplier_id) WHERE (is_default = true);


--
-- Name: customer_addresses fk_customer_addresses_address_id_addresses; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_addresses
    ADD CONSTRAINT fk_customer_addresses_address_id_addresses FOREIGN KEY (address_id) REFERENCES public.addresses(id) ON DELETE RESTRICT;


--
-- Name: customer_addresses fk_customer_addresses_customer_id_customers; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_addresses
    ADD CONSTRAINT fk_customer_addresses_customer_id_customers FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE CASCADE;


--
-- Name: employee_addresses fk_employee_addresses_address_id_addresses; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_addresses
    ADD CONSTRAINT fk_employee_addresses_address_id_addresses FOREIGN KEY (address_id) REFERENCES public.addresses(id) ON DELETE RESTRICT;


--
-- Name: employee_addresses fk_employee_addresses_employee_id_employees; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_addresses
    ADD CONSTRAINT fk_employee_addresses_employee_id_employees FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: supplier_addresses fk_supplier_addresses_address_id_addresses; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_addresses
    ADD CONSTRAINT fk_supplier_addresses_address_id_addresses FOREIGN KEY (address_id) REFERENCES public.addresses(id) ON DELETE RESTRICT;


--
-- Name: supplier_addresses fk_supplier_addresses_supplier_id_suppliers; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_addresses
    ADD CONSTRAINT fk_supplier_addresses_supplier_id_suppliers FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


