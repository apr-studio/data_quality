-- Table: public.orders

-- DROP TABLE IF EXISTS public.orders;

CREATE TABLE IF NOT EXISTS public.orders
(
    order_item_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    order_id character varying(20) COLLATE pg_catalog."default",
    order_date date,
    customer_id character varying(20) COLLATE pg_catalog."default",
    product_id character varying(20) COLLATE pg_catalog."default",
    product_name character varying(100) COLLATE pg_catalog."default",
    quantity integer,
    unit_price numeric(12,2),
    status character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT orders_pkey PRIMARY KEY (order_item_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.orders
    OWNER to elena;