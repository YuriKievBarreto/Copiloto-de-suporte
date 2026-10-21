from app.agent.sql_agent.state import SQLAgentState
from app.agent.llm import getLLM
from app.core.database.relational_database import get_agent_engine
from app.agent.sql_agent.prompts.generate_sql import SQL_SYSTEM_PROMPT
from datetime import date
from sqlalchemy import inspect

llm = getLLM()
def generate_sql_node(state: SQLAgentState):
    system = SQL_SYSTEM_PROMPT.format(
        data_atual=date.today().isoformat(),
        schema=get_schema()
    )


    user = state["question"]
    if state["error"]: 
        user +=  f"\n\nSua tentativa anterior falhou.\nSQL: {state['sql']}\nErro: {state['error']}\nCorrija o SQL."

    resposta = getLLM().invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    return {"sql": clean_sql(resposta.content)}







def get_schema() -> str:
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


import re

def clean_sql(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r"^```(?:sql)?\s*", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\s*```$", "", texto)
    return texto.strip()