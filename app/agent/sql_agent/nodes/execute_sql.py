from app.agent.sql_agent.state import SQLAgentState, MAX_ATTEMPTS
from sqlalchemy import inspect
from app.infra.database.relational_database import get_agent_engine
from sqlalchemy import text
from sqlmodel import Session
from typing import Any
from langchain_core.tools import tool
import re
import json
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

MAX_ROWS = 50



def execute_sql(state: SQLAgentState) -> dict:
    attempts = state["attempts"] + 1
    try:
        result = run_query(state["sql"])
        return {"result": result, "error": None, "attempts": attempts}
    except ValueError as e:
        return {"result": None, "error": str(e), "attempts": attempts}
    except DBAPIError as e:
        return {"result": None, "error": f"Erro SQL: {e.orig}", "attempts": attempts}



def run_query(sql: str) -> list[dict]:
    query = sql.strip().rstrip(";").strip()

    if ";" in query or not re.match(r"(?is)^(select|with)\b", query):
        raise ValueError(
            "Envie uma única consulta SELECT (WITH ... SELECT também é aceito), "
            "sem ponto e vírgula no meio."
        )

    engine = get_agent_engine()
    with Session(engine) as session:
        if engine.dialect.name == "postgresql":
            session.exec(text("SET TRANSACTION READ ONLY"))
            session.exec(text("SET LOCAL statement_timeout = '10s'"))
        result = session.exec(text(f"SELECT * FROM ({query}) AS t LIMIT {MAX_ROWS}"))
        return [dict(row) for row in result.mappings().all()]


