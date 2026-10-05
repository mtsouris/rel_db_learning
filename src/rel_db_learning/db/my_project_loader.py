"""Installer and data helpers for the student's my_project PostgreSQL database.

:func:`install_my_project` creates the empty database once from the setup
notebook.

:func:`reset_my_project_data` restores the original Library seed dataset
without touching the schema. Call it from any Module 04 notebook after
UPDATE or DELETE experiments to get a clean slate.

:func:`reset_my_project_data_full` reloads the richer Stage 6 dataset
covering all seven tables. Use it once the full Stage 6 schema exists
(after notebook 13) for plenty of data to experiment with transactions
and for the final review notebook.

:func:`rebuild_messy_library` is the heavier "factory reset" for Module 05:
it drops every object and recreates the full messy Stage 6 schema from the
bundled ``stage_6_schema.sql`` before reloading the same full seed. Use it to
restart the normalization module from a clean, un-normalized state after the
migrations have dropped columns (which would break
:func:`reset_my_project_data_full`, since it inserts into columns that no
longer exist).
"""

from __future__ import annotations

import importlib.resources

import psycopg2
from psycopg2 import sql

from rel_db_learning import config
from rel_db_learning.db.connection import _get_admin_connection

# Empty the public schema without dropping or recreating it, so the schema's
# owner and access privileges stay exactly as they were. A DROP SCHEMA / CREATE
# SCHEMA would reset that ACL (and a later pgModeler Diff would then try to
# re-add default grants, including one to the pg_database_owner system role,
# which breaks its next import). Instead, iterate the catalog and drop every
# object inside public: tables first (CASCADE removes dependent views, foreign
# keys, and owned sequences), then any leftover views, then the domains, then
# any leftover sequences. quote_ident plus string concatenation is used rather
# than format() so the SQL contains no '%' for psycopg2 to read as a parameter
# placeholder. The IF EXISTS / dynamic iteration makes this safe from any prior
# state, whether messy Stage 6 or partially or fully normalized.
_DROP_PUBLIC_OBJECTS_SQL = """
DO $$
DECLARE
    obj record;
BEGIN
    FOR obj IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.'
            || quote_ident(obj.tablename) || ' CASCADE';
    END LOOP;

    FOR obj IN
        SELECT viewname FROM pg_views WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP VIEW IF EXISTS public.'
            || quote_ident(obj.viewname) || ' CASCADE';
    END LOOP;

    FOR obj IN
        SELECT t.typname AS name
        FROM pg_type t
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public' AND t.typtype = 'd'
    LOOP
        EXECUTE 'DROP DOMAIN IF EXISTS public.'
            || quote_ident(obj.name) || ' CASCADE';
    END LOOP;

    FOR obj IN
        SELECT sequencename FROM pg_sequences WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS public.'
            || quote_ident(obj.sequencename) || ' CASCADE';
    END LOOP;
END $$;
"""


def install_my_project(force: bool = False) -> None:
    """Create the empty ``my_project`` database.

    Reads the target database name from the saved config. Connects to the
    default ``postgres`` database (via :func:`_get_admin_connection`) to
    issue DDL, then connects to the new database to run the bundled SQL
    script (which initialises server settings but contains no tables yet).

    Parameters
    ----------
    force : bool, optional
        When ``True``, drop and re-create the database if it already exists.
        Defaults to ``False``.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet.
    psycopg2.Error
        On any database error during creation; an English message is
        printed before re-raising.
    """
    cfg = config.get_config()
    dbname = cfg["project_db"]

    admin_conn = _get_admin_connection()
    admin_conn.autocommit = True
    try:
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
            )
            exists = cur.fetchone() is not None

        if exists and not force:
            print(
                f"Database '{dbname}' already exists. "
                "Use install_my_project(force=True) to reinstall."
            )
            return

        if exists:
            with admin_conn.cursor() as cur:
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = %s AND pid <> pg_backend_pid()",
                    (dbname,),
                )
            with admin_conn.cursor() as cur:
                cur.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(dbname))
                )

        print("Creating database...")
        with admin_conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname))
            )
    finally:
        admin_conn.close()

    sql_text = (
        importlib.resources.files("rel_db_learning.data.my_project")
        .joinpath("my_project_postgres.sql")
        .read_text(encoding="utf-8")
    )

    db_conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=dbname,
    )
    try:
        with db_conn.cursor() as cur:
            cur.execute(sql_text)
        db_conn.commit()
    except Exception:
        db_conn.rollback()
        print(f"Error while loading database '{dbname}'.")
        raise
    finally:
        db_conn.close()

    print(
        f"✓ Database '{dbname}' installed. "
        "(Empty, ready for module 04)"
    )


def reset_my_project_data() -> None:
    """Restore the Library seed data in my_project without changing the schema.

    Truncates the four core tables (loan, member_card, book, member) and
    re-inserts the original seed dataset. Useful after UPDATE or DELETE
    experiments in Module 04 notebooks when you want a clean slate.

    Columns added by later stage DDL (for example ``book.is_available`` from
    Stage 3) are not specified in the seed INSERT statements and therefore
    keep their column defaults.

    Prints a short row-count summary on success. On error, prints a clean
    English message without a raw traceback.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet. Run ``setup_connection()`` first.
    """
    cfg = config.get_config()

    seed_sql = (
        importlib.resources.files("rel_db_learning.data.my_project")
        .joinpath("seed_data.sql")
        .read_text(encoding="utf-8")
    )

    db_conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["project_db"],
    )
    try:
        with db_conn.cursor() as cur:
            # TRUNCATE in FK-safe order; CASCADE handles remaining dependencies.
            cur.execute(
                "TRUNCATE loan, member_card, book, member RESTART IDENTITY CASCADE;"
            )
            cur.execute(seed_sql)
        db_conn.commit()

        counts: dict[str, int] = {}
        for table in ("book", "member", "loan", "member_card"):
            with db_conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    )
                )
                counts[table] = cur.fetchone()[0]

        print(
            f"Reset complete: "
            f"{counts['book']} books, "
            f"{counts['member']} members, "
            f"{counts['loan']} loans, "
            f"{counts['member_card']} member cards."
        )
    except Exception as exc:
        db_conn.rollback()
        print(f"Error resetting data: {exc}")
    finally:
        db_conn.close()


def reset_my_project_data_full() -> None:
    """Truncate all seven tables and reload the full Stage 6 seed.

    Use this at Stage 6 (after notebook 13) for rich data to experiment
    with transactions and for the final review. Requires the full Stage 6
    schema to exist.

    Truncates the seven Library tables (book, member, loan, member_card,
    reservation, librarian, book_copy) and reloads the richer
    ``seed_data_final.sql`` dataset: about 75 books, 48 members, 110 loans,
    plus librarians, book copies, member cards, and reservations. The seed
    keeps the intentional 1NF/2NF/3NF anomalies for Module 05 and is
    internally consistent (every foreign key resolves, ``book.is_available``
    is false exactly for books with an active loan, and contact details
    satisfy the email_address and phone_number domains).

    Prints a short row-count summary on success. On error, prints a clean
    English message without a raw traceback.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet. Run ``setup_connection()`` first.
    """
    cfg = config.get_config()

    seed_sql = (
        importlib.resources.files("rel_db_learning.data.my_project")
        .joinpath("seed_data_final.sql")
        .read_text(encoding="utf-8")
    )

    db_conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["project_db"],
    )
    try:
        with db_conn.cursor() as cur:
            # TRUNCATE all seven tables; CASCADE clears dependent rows safely.
            cur.execute(
                "TRUNCATE book, member, loan, member_card, reservation, "
                "librarian, book_copy RESTART IDENTITY CASCADE;"
            )
            cur.execute(seed_sql)
        db_conn.commit()

        counts: dict[str, int] = {}
        for table in (
            "book", "member", "loan", "member_card",
            "reservation", "librarian", "book_copy",
        ):
            with db_conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    )
                )
                counts[table] = cur.fetchone()[0]

        print(
            f"Full reset complete: "
            f"{counts['book']} books, "
            f"{counts['member']} members, "
            f"{counts['loan']} loans, "
            f"{counts['member_card']} member cards, "
            f"{counts['reservation']} reservations, "
            f"{counts['librarian']} librarians, "
            f"{counts['book_copy']} book copies."
        )
    except Exception as exc:
        db_conn.rollback()
        print(f"Error resetting data: {exc}")
    finally:
        db_conn.close()


def rebuild_messy_library() -> None:
    """Drop everything and rebuild the messy Stage 6 schema, then reload the
    full seed. Use this to restart Module 05 from a clean, un-normalized
    state. Works regardless of the current schema state.

    The normalization notebooks migrate the schema by *dropping* columns
    (``book.authors`` and ``book.genres`` in notebook 02, the ``publisher_*``
    columns and ``member.country`` in notebook 04). Once that has happened,
    :func:`reset_my_project_data_full` can no longer reload the seed, because
    it inserts into columns that no longer exist. This helper is the heavier
    reset: it rebuilds the original messy schema before reloading the data, so
    it works whether the database is still at messy Stage 6 or has been
    partially or fully normalized.

    Steps:

    1. Empty the ``public`` schema by dropping every object inside it
       (tables, then any leftover views, then domains, then any leftover
       sequences) so the rebuild succeeds from any prior state. The schema
       itself is **not** dropped or recreated, so its owner and access
       privileges are left untouched. (A ``DROP SCHEMA`` / ``CREATE SCHEMA``
       would reset that ACL, after which a pgModeler Diff would try to re-add
       default grants and break its next import.)
    2. Run the bundled ``stage_6_schema.sql`` to recreate the two domains,
       the seven tables (with their primary and foreign keys), the
       ``idx_book_title`` index, and the three views.
    3. Load ``seed_data_final.sql`` into the freshly created, empty tables
       (no TRUNCATE needed on a fresh schema).

    Prints a short English row-count summary on success. On error, rolls
    back, prints a clean English message, and does not raise.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet. Run ``setup_connection()`` first.
    """
    cfg = config.get_config()

    data_dir = importlib.resources.files("rel_db_learning.data.my_project")
    schema_sql = data_dir.joinpath("stage_6_schema.sql").read_text(
        encoding="utf-8"
    )
    seed_sql = data_dir.joinpath("seed_data_final.sql").read_text(
        encoding="utf-8"
    )

    db_conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["project_db"],
    )
    try:
        with db_conn.cursor() as cur:
            # Empty the public schema from any prior state (messy Stage 6, or
            # partially/fully normalized) by dropping the objects inside it,
            # leaving the schema's owner and ACL untouched.
            cur.execute(_DROP_PUBLIC_OBJECTS_SQL)
            # Recreate the messy Stage 6 schema, then load the full seed into
            # the now-empty tables.
            cur.execute(schema_sql)
            cur.execute(seed_sql)
        db_conn.commit()

        counts: dict[str, int] = {}
        for table in (
            "book", "member", "loan", "member_card",
            "reservation", "librarian", "book_copy",
        ):
            with db_conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    )
                )
                counts[table] = cur.fetchone()[0]

        print(
            f"Messy Stage 6 library rebuilt: "
            f"{counts['book']} books, "
            f"{counts['member']} members, "
            f"{counts['loan']} loans, "
            f"{counts['member_card']} member cards, "
            f"{counts['reservation']} reservations, "
            f"{counts['librarian']} librarians, "
            f"{counts['book_copy']} book copies."
        )
    except Exception as exc:
        db_conn.rollback()
        print(f"Error rebuilding the library: {exc}")
    finally:
        db_conn.close()
