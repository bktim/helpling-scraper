-- Table: public.entries

-- DROP TABLE public.entries;

CREATE TABLE public.entries
(
    candidate_id integer,
    postcode integer,
    date date,
    firstname character varying(255) COLLATE pg_catalog."default",
    price_per_hour real,
	avg_rating real,
    shortname character varying(255) COLLATE pg_catalog."default",
    default_profile_image character varying(255) COLLATE pg_catalog."default",
    pets boolean,
    windows boolean,
    ironing boolean,
    ratings_received_count integer,
    verification_level character varying(255) COLLATE pg_catalog."default",
    documents character varying[] COLLATE pg_catalog."default",
    language_skills character varying[] COLLATE pg_catalog."default",
    instabook_enabled boolean,
    performed_cleanings_count integer,
    experience_description character varying COLLATE pg_catalog."default",
    experience_headline character varying COLLATE pg_catalog."default",
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE public.entries
    OWNER to dst;