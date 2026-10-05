-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler version: 1.0.5
-- PostgreSQL version: 15.0
-- Project Site: pgmodeler.io
-- Model Author: ---
-- -- object: pg_database_owner | type: ROLE --
-- -- DROP ROLE IF EXISTS pg_database_owner;
-- CREATE ROLE pg_database_owner WITH 
-- 	INHERIT
-- 	 PASSWORD '********';
-- -- ddl-end --
-- 

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: my_project | type: DATABASE --
-- DROP DATABASE IF EXISTS my_project;
CREATE DATABASE my_project
	ENCODING = 'UTF8'
	LC_COLLATE = 'Greek_Greece.1252'
	LC_CTYPE = 'Greek_Greece.1252'
	TABLESPACE = pg_default
	OWNER = postgres;
-- ddl-end --


-- object: public.book | type: TABLE --
-- DROP TABLE IF EXISTS public.book CASCADE;
CREATE TABLE public.book (
	book_id integer NOT NULL,
	title character varying(200),
	authors text,
	genres text,
	publisher_name character varying(150),
	publisher_address character varying(200),
	publisher_city character varying(100),
	is_available boolean,
	CONSTRAINT book_pk PRIMARY KEY (book_id)
);
-- ddl-end --
ALTER TABLE public.book OWNER TO postgres;
-- ddl-end --

-- object: public.email_address | type: DOMAIN --
-- DROP DOMAIN IF EXISTS public.email_address CASCADE;
CREATE DOMAIN public.email_address AS varchar(255)
	CONSTRAINT email_format CHECK (VALUE ~ '^[^@]+@[^@]+\.[^@]+$');
-- ddl-end --
ALTER DOMAIN public.email_address OWNER TO postgres;
-- ddl-end --

-- object: public.loan | type: TABLE --
-- DROP TABLE IF EXISTS public.loan CASCADE;
CREATE TABLE public.loan (
	loan_id integer NOT NULL,
	book_id integer NOT NULL,
	member_id integer NOT NULL,
	loan_date date,
	return_date date,
	is_returned boolean DEFAULT false,
	librarian_id_librarian integer NOT NULL,
	CONSTRAINT loan_pk PRIMARY KEY (loan_id)
);
-- ddl-end --
ALTER TABLE public.loan OWNER TO postgres;
-- ddl-end --

-- object: public.member_card | type: TABLE --
-- DROP TABLE IF EXISTS public.member_card CASCADE;
CREATE TABLE public.member_card (
	card_id integer NOT NULL,
	issue_date date,
	expiry_date date,
	member_id_member integer NOT NULL,
	CONSTRAINT member_card_pk PRIMARY KEY (card_id)
);
-- ddl-end --
ALTER TABLE public.member_card OWNER TO postgres;
-- ddl-end --

-- object: public.phone_number | type: DOMAIN --
-- DROP DOMAIN IF EXISTS public.phone_number CASCADE;
CREATE DOMAIN public.phone_number AS varchar(20)
	CONSTRAINT phone_format CHECK (VALUE ~ '^[0-9+() -]+$');
-- ddl-end --
ALTER DOMAIN public.phone_number OWNER TO postgres;
-- ddl-end --

-- object: public.member | type: TABLE --
-- DROP TABLE IF EXISTS public.member CASCADE;
CREATE TABLE public.member (
	member_id integer NOT NULL,
	full_name character varying(150),
	address character varying(200),
	city character varying(100),
	country character varying(100),
	penalty_days integer DEFAULT 0,
	phone public.phone_number,
	email public.email_address,
	CONSTRAINT member_pk PRIMARY KEY (member_id)
);
-- ddl-end --
ALTER TABLE public.member OWNER TO postgres;
-- ddl-end --

-- object: public.current_loans | type: VIEW --
-- DROP VIEW IF EXISTS public.current_loans CASCADE;
CREATE VIEW public.current_loans
AS 

SELECT l.loan_id, m.full_name, b.title, l.loan_date
FROM loan l
JOIN member m ON l.member_id = m.member_id
JOIN book b ON l.book_id = b.book_id
WHERE l.is_returned = false;
-- ddl-end --
ALTER VIEW public.current_loans OWNER TO postgres;
-- ddl-end --

-- object: public.overdue_loans | type: VIEW --
-- DROP VIEW IF EXISTS public.overdue_loans CASCADE;
CREATE VIEW public.overdue_loans
AS 

SELECT l.loan_id, m.full_name, b.title, l.loan_date
FROM loan l
JOIN member m ON l.member_id = m.member_id
JOIN book b ON l.book_id = b.book_id
WHERE l.is_returned = false
  AND l.loan_date + INTERVAL '15 days' < CURRENT_DATE;
-- ddl-end --
ALTER VIEW public.overdue_loans OWNER TO postgres;
-- ddl-end --

-- object: public.reservation | type: TABLE --
-- DROP TABLE IF EXISTS public.reservation CASCADE;
CREATE TABLE public.reservation (
	reservation_id integer NOT NULL,
	book_id integer,
	member_id integer,
	reservation_date date,
	is_fulfilled boolean,
	CONSTRAINT reservation_pk PRIMARY KEY (reservation_id)
);
-- ddl-end --
ALTER TABLE public.reservation OWNER TO postgres;
-- ddl-end --

-- object: public.pending_reservations | type: VIEW --
-- DROP VIEW IF EXISTS public.pending_reservations CASCADE;
CREATE VIEW public.pending_reservations
AS 

SELECT r.reservation_id, m.full_name, b.title, r.reservation_date
FROM reservation r
JOIN member m ON r.member_id = m.member_id
JOIN book b ON r.book_id = b.book_id
WHERE r.is_fulfilled = false;
-- ddl-end --
ALTER VIEW public.pending_reservations OWNER TO postgres;
-- ddl-end --

-- object: idx_book_title | type: INDEX --
-- DROP INDEX IF EXISTS public.idx_book_title CASCADE;
CREATE INDEX idx_book_title ON public.book
USING btree
(
	title
);
-- ddl-end --

-- object: member_fk | type: CONSTRAINT --
-- ALTER TABLE public.member_card DROP CONSTRAINT IF EXISTS member_fk CASCADE;
ALTER TABLE public.member_card ADD CONSTRAINT member_fk FOREIGN KEY (member_id_member)
REFERENCES public.member (member_id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: member_card_uq | type: CONSTRAINT --
-- ALTER TABLE public.member_card DROP CONSTRAINT IF EXISTS member_card_uq CASCADE;
ALTER TABLE public.member_card ADD CONSTRAINT member_card_uq UNIQUE (member_id_member);
-- ddl-end --

-- object: public.librarian | type: TABLE --
-- DROP TABLE IF EXISTS public.librarian CASCADE;
CREATE TABLE public.librarian (
	librarian_id integer NOT NULL,
	full_name varchar,
	hire_date date,
	is_manager boolean,
	CONSTRAINT librarian_pk PRIMARY KEY (librarian_id)
);
-- ddl-end --
ALTER TABLE public.librarian OWNER TO postgres;
-- ddl-end --

-- object: public.book_copy | type: TABLE --
-- DROP TABLE IF EXISTS public.book_copy CASCADE;
CREATE TABLE public.book_copy (
	copy_id integer NOT NULL,
	acquisition_date date,
	condition varchar,
	book_id_book integer NOT NULL,
	CONSTRAINT book_copy_pk PRIMARY KEY (copy_id)
);
-- ddl-end --
ALTER TABLE public.book_copy OWNER TO postgres;
-- ddl-end --

-- object: book_fk | type: CONSTRAINT --
-- ALTER TABLE public.book_copy DROP CONSTRAINT IF EXISTS book_fk CASCADE;
ALTER TABLE public.book_copy ADD CONSTRAINT book_fk FOREIGN KEY (book_id_book)
REFERENCES public.book (book_id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: librarian_fk | type: CONSTRAINT --
-- ALTER TABLE public.loan DROP CONSTRAINT IF EXISTS librarian_fk CASCADE;
ALTER TABLE public.loan ADD CONSTRAINT librarian_fk FOREIGN KEY (librarian_id_librarian)
REFERENCES public.librarian (librarian_id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: loan_book_fk | type: CONSTRAINT --
-- ALTER TABLE public.loan DROP CONSTRAINT IF EXISTS loan_book_fk CASCADE;
ALTER TABLE public.loan ADD CONSTRAINT loan_book_fk FOREIGN KEY (book_id)
REFERENCES public.book (book_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: loan_member_fk | type: CONSTRAINT --
-- ALTER TABLE public.loan DROP CONSTRAINT IF EXISTS loan_member_fk CASCADE;
ALTER TABLE public.loan ADD CONSTRAINT loan_member_fk FOREIGN KEY (member_id)
REFERENCES public.member (member_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: book_id | type: CONSTRAINT --
-- ALTER TABLE public.reservation DROP CONSTRAINT IF EXISTS book_id CASCADE;
ALTER TABLE public.reservation ADD CONSTRAINT book_id FOREIGN KEY (book_id)
REFERENCES public.book (book_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: member_id | type: CONSTRAINT --
-- ALTER TABLE public.reservation DROP CONSTRAINT IF EXISTS member_id CASCADE;
ALTER TABLE public.reservation ADD CONSTRAINT member_id FOREIGN KEY (member_id)
REFERENCES public.member (member_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "grant_CU_26541e8cda" | type: PERMISSION --
GRANT CREATE,USAGE
   ON SCHEMA public
   TO pg_database_owner;
-- ddl-end --

-- object: "grant_U_cd8e46e7b6" | type: PERMISSION --
GRANT USAGE
   ON SCHEMA public
   TO PUBLIC;
-- ddl-end --


