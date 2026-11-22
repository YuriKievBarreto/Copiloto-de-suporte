from sqlalchemy import text
from psycopg import sql

from app.infra.database.relational_database import get_engine
from app.core.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM pg_roles
                    WHERE rolname = 'agent_ro'
                ) THEN
                    CREATE ROLE agent_ro
                    LOGIN
                    CONNECTION LIMIT 5;
                END IF;
            END
            $$;
        """))

        password = settings.agent_ro_password.get_secret_value()

        raw_conn = conn.connection.driver_connection

        raw_conn.execute(
            sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                sql.Identifier("agent_ro"),
                sql.Literal(password),
            )
        )

        conn.execute(text("""
            GRANT USAGE
            ON SCHEMA public
            TO agent_ro;
        """))

        conn.execute(text("""
            GRANT SELECT
            ON TABLE
                public.agentes,
                public.clientes,
                public.comentarios,
                public.tickets
            TO agent_ro;
        """))