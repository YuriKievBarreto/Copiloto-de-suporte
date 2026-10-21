from sqlalchemy import inspect
from app.core.database.relational_database import get_agent_engine
from sqlalchemy import text
from sqlmodel import Session
from typing import Any
from langchain_core.tools import tool


@tool
def get_schema() -> str:
    """
    This tool returns all table names and its collumn names
    Use this tool when you need to understand what information from database you must have to answer the user's question

    Returns:
    This tool returns all table names and its collumn names
    Use this tool when you need to understand what information from database you must have to answer the user's question

    example: 
        Table: customers
        - id: CHAR(32)
        - name: VARCHAR
        - email: VARCHAR
        - city: VARCHAR
        - state: VARCHAR
        - created_at: DATETIME
        - customer_type: VARCHAR(10)

        Table: order_items
        - id: CHAR(32)
        - order_id: CHAR(32)
        - product_id: CHAR(32)
        - quantity: INTEGER
        - unit_price: NUMERIC
        - FK: order_id → orders.id
        - FK: product_id → products.id
    """

    schema = []
    inspector = inspect(get_agent_engine())

    for table_name in inspector.get_table_names():
        schema.append(f"Table: {table_name}")

        columns = inspector.get_columns(table_name)

        for column in columns:
            tipo = column["type"]
            valores = getattr(tipo, "enums", None)
            if valores:
                schema.append(
                    f"  - {column['name']}: {tipo} (valores permitidos: {', '.join(valores)})"
                )
            else:
                schema.append(f"  - {column['name']}: {tipo}")

        foreign_keys = inspector.get_foreign_keys(table_name)

        for fk in foreign_keys:
            constrained_columns = fk["constrained_columns"]
            referred_table = fk["referred_table"]
            referred_columns = fk["referred_columns"]

            for column, referred_column in zip(
                constrained_columns,
                referred_columns
            ):
                schema.append(
                    f"  - FK: {column} → {referred_table}.{referred_column}"
                )

        schema.append("")

    return "\n".join(schema)



import json
import re

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

MAX_ROWS = 50


@tool
def execute_sql(sql: str) -> str:
    """
    Execute one read-only SQL query (PostgreSQL dialect) against the tickets database.
    Use this tool when you must retrieve information from the database to answer the user's question.
    If you don't know the table names and their columns, execute first the 'get_schema' tool.

    Rules:
    - Send a single SELECT statement (WITH ... SELECT is accepted), without semicolons.
    - In queries with more than one table, qualify columns with table aliases and check
      each column in the schema before using it.
    - Columns listed with "valores permitidos" are enums: compare with = or IN, using exactly
      the listed values. Do not use LIKE or ILIKE on them.
    - At most 50 rows are returned.

    Returns:
        A JSON list of rows, or a message starting with 'Erro' if the query failed.
        If it failed, read the message, fix the query and try again.
        example:
        using the following query:
            'SELECT status, COUNT(*) AS total FROM tickets GROUP BY status'
        the result follows this structure:
            '[{"status": "ABERTO", "total": 12}, {"status": "FECHADO", "total": 40}]'
    """
    query = sql.strip().rstrip(";").strip()

    if ";" in query or not re.match(r"(?is)^(select|with)\b", query):
        return ("Erro: envie uma única consulta SELECT (WITH ... SELECT também é aceito), "
                "sem ponto e vírgula no meio.")

    engine = get_agent_engine()
    try:
        with Session(engine) as session:
            if engine.dialect.name == "postgresql":
                session.exec(text("SET TRANSACTION READ ONLY"))
                session.exec(text("SET LOCAL statement_timeout = '10s'"))
            result = session.exec(text(f"SELECT * FROM ({query}) AS t LIMIT {MAX_ROWS}"))
            rows = [dict(row) for row in result.mappings().all()]
    except DBAPIError as e:
        msg = f"Erro SQL: {e.orig}"
        if "invalid input value for enum" in msg:
            msg += "\nDica: chame get_schema e use exatamente os valores permitidos da coluna."
        return msg

    return json.dumps(rows, default=str, ensure_ascii=False)