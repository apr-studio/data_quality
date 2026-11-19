-- Table: public.data_quality_issue_log

-- DROP TABLE IF EXISTS public.data_quality_issue_log;

CREATE TABLE IF NOT EXISTS public.data_quality_issue_log
(
    issue_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    order_item_id bigint,
    order_id character varying(20) COLLATE pg_catalog."default",
    issue_type character varying(50) COLLATE pg_catalog."default",
    issue_description text COLLATE pg_catalog."default",
    detected_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT data_quality_issue_log_pkey PRIMARY KEY (issue_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.data_quality_issue_log
    OWNER to elena;
-- Index: uq_issue_item_type

-- DROP INDEX IF EXISTS public.uq_issue_item_type;

CREATE UNIQUE INDEX IF NOT EXISTS uq_issue_item_type
    ON public.data_quality_issue_log USING btree
    (order_item_id ASC NULLS LAST, issue_type COLLATE pg_catalog."default" ASC NULLS LAST)
;