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
            schema.append(
                f"  - {column['name']}: {column['type']}"
            )

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



@tool
def execute_sql(sql: str) -> list[dict[str, Any]]:
    """
    Execute the provided SQL against the database.
    Use this tool when you must retrieve information from database to answer the user's question.
    If you don't know the table names and its columns, execute first the 'get_schema' tool to understand the database architecture
    

    Returns:
        this tool returns a list of dicts containing the query results
        example:
        using the following query:
            'SELECT name, city FROM customers LIMIT 10;'
            the result follows this structure:
            [{'name': 'Henrique Silva', 'city': 'Uberlândia'}, {'name': 'Gabriela Freitas', 'city': 'Guarulhos'}]
    """
    engine = get_agent_engine()
    with Session(engine) as session:
        normalized = sql.strip().lower()

        if not normalized.startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")
        
        result = session.exec(text(sql))
        return [dict(row) for row in result.mappings().all()]

