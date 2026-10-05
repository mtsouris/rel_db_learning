-- Messy Stage 6 Library schema (the Module 05 starting point).
--
-- Recreates the full, un-normalized Stage 6 schema: two domains, seven tables
-- (with their primary and foreign keys), the idx_book_title index, and three
-- views. This is the schema the normalization notebooks begin from, before
-- First Normal Form takes the authors and genres columns out of book and later
-- notebooks drop the publisher columns and member.country.
--
-- Cleaned from the pgModeler export of stage_6_design.dbm and kept faithful to
-- that model, so a pgModeler Diff against it shows nothing spurious (no domain
-- re-creation, no index recreation, no permission changes). Removed only the
-- non-schema noise: database-creation, connection, server-configuration,
-- ownership, and privilege statements, plus the pgModeler header and per-object
-- comment lines. The file never creates or drops the public schema; it runs on
-- the existing, already-emptied schema (rebuild_messy_library drops the objects
-- inside public dynamically), leaving the schema's owner and access privileges
-- untouched.
--
-- The single deviation from the export is loan.librarian_id_librarian, made
-- nullable here to match the live my_project schema (the loan to librarian
-- relationship was added as optional on the already-populated table, and the
-- seed leaves it NULL).
--
-- Runnable as one script on an emptied schema. Objects are ordered by
-- dependency: domains, then tables, then the index, then foreign keys, then
-- views.


-- Domains ---------------------------------------------------------------------

CREATE DOMAIN public.email_address AS varchar(255)
    CONSTRAINT email_format CHECK (VALUE ~ '^[^@]+@[^@]+\.[^@]+$');

CREATE DOMAIN public.phone_number AS varchar(20)
    CONSTRAINT phone_format CHECK (VALUE ~ '^[0-9+() -]+$');


-- Tables ----------------------------------------------------------------------

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

CREATE TABLE public.loan (
    loan_id integer NOT NULL,
    book_id integer NOT NULL,
    member_id integer NOT NULL,
    loan_date date,
    return_date date,
    is_returned boolean DEFAULT false,
    librarian_id_librarian integer,
    CONSTRAINT loan_pk PRIMARY KEY (loan_id)
);

CREATE TABLE public.member_card (
    card_id integer NOT NULL,
    issue_date date,
    expiry_date date,
    member_id_member integer NOT NULL,
    CONSTRAINT member_card_pk PRIMARY KEY (card_id)
);

CREATE TABLE public.reservation (
    reservation_id integer NOT NULL,
    book_id integer,
    member_id integer,
    reservation_date date,
    is_fulfilled boolean,
    CONSTRAINT reservation_pk PRIMARY KEY (reservation_id)
);

CREATE TABLE public.librarian (
    librarian_id integer NOT NULL,
    full_name varchar,
    hire_date date,
    is_manager boolean,
    CONSTRAINT librarian_pk PRIMARY KEY (librarian_id)
);

CREATE TABLE public.book_copy (
    copy_id integer NOT NULL,
    acquisition_date date,
    condition varchar,
    book_id_book integer NOT NULL,
    CONSTRAINT book_copy_pk PRIMARY KEY (copy_id)
);


-- Index -----------------------------------------------------------------------

CREATE INDEX idx_book_title ON public.book
USING btree
(
    title
);


-- Foreign keys (and the UNIQUE that makes member_card to member 1:1) ----------

ALTER TABLE public.member_card ADD CONSTRAINT member_fk FOREIGN KEY (member_id_member)
REFERENCES public.member (member_id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE public.member_card ADD CONSTRAINT member_card_uq UNIQUE (member_id_member);

ALTER TABLE public.book_copy ADD CONSTRAINT book_fk FOREIGN KEY (book_id_book)
REFERENCES public.book (book_id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE public.loan ADD CONSTRAINT librarian_fk FOREIGN KEY (librarian_id_librarian)
REFERENCES public.librarian (librarian_id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE public.loan ADD CONSTRAINT loan_book_fk FOREIGN KEY (book_id)
REFERENCES public.book (book_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE public.loan ADD CONSTRAINT loan_member_fk FOREIGN KEY (member_id)
REFERENCES public.member (member_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE public.reservation ADD CONSTRAINT book_id FOREIGN KEY (book_id)
REFERENCES public.book (book_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE public.reservation ADD CONSTRAINT member_id FOREIGN KEY (member_id)
REFERENCES public.member (member_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;


-- Views -----------------------------------------------------------------------

CREATE VIEW public.current_loans AS
SELECT l.loan_id, m.full_name, b.title, l.loan_date
FROM loan l
JOIN member m ON l.member_id = m.member_id
JOIN book b ON l.book_id = b.book_id
WHERE l.is_returned = false;

CREATE VIEW public.overdue_loans AS
SELECT l.loan_id, m.full_name, b.title, l.loan_date
FROM loan l
JOIN member m ON l.member_id = m.member_id
JOIN book b ON l.book_id = b.book_id
WHERE l.is_returned = false
  AND l.loan_date + INTERVAL '15 days' < CURRENT_DATE;

CREATE VIEW public.pending_reservations AS
SELECT r.reservation_id, m.full_name, b.title, r.reservation_date
FROM reservation r
JOIN member m ON r.member_id = m.member_id
JOIN book b ON r.book_id = b.book_id
WHERE r.is_fulfilled = false;
