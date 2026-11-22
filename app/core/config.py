from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus
from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


RAIZ = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=RAIZ / ".env.production",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enviroment: str = Field(
        default="dev",
        validation_alias=AliasChoices("enviroment", "ENVIROMENT", "environment", "ENVIRONMENT"),
    )

    # Postgres (individual config / local & dev)
    agent_postgres_user: str = "agent_ro"
    agent_ro_password: SecretStr = SecretStr("")
    postgres_user: str = "helpdesk"
    postgres_password: SecretStr = SecretStr("")
    postgres_db: str = "helpdesk"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432

    

    # Postgres connection string direta (usada em produção / Neon, etc.)
    postgres_conn_string: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("postgres_conn_string", "POSTGRES_CONN_STRING"),
    )

    # Qdrant
    qdrant_url: str = Field(
        default="http://127.0.0.1:6333",
        validation_alias=AliasChoices("qdrant_url", "QDRANT_URL"),
    )
    cluster_endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices("cluster_endpoint", "CLUSTER_ENDPOINT"),
    )
    qdrant_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("qdrant_api_key", "QDRANT_API_KEY", "qdrant_api_kley", "QDRANT_API_KLEY"),
    )
    qdrant_collection: str = "manuais"

    hf_token: SecretStr
    embedding_model: str = "BAAI/bge-m3"

    @property
    def is_production(self) -> bool:
        return self.enviroment.strip().lower() in ("prod", "production")

    @property
    def effective_qdrant_url(self) -> str:
        if self.is_production and self.cluster_endpoint:
            return self.cluster_endpoint
        return self.qdrant_url

    def _url(self, usuario: str, senha: SecretStr) -> str:
        senha_codificada = quote_plus(senha.get_secret_value())
        return (
            f"postgresql://{usuario}:{senha_codificada}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def agent_url(self, usuario_agent: str, senha_agent: SecretStr) -> str:
        senha_codificada = quote_plus(senha_agent.get_secret_value())
        return (
            f"postgresql://{usuario_agent}:{senha_codificada}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url(self) -> str:
        if self.is_production and self.postgres_conn_string:
            return self.postgres_conn_string.get_secret_value()
        return self._url(self.postgres_user, self.postgres_password)

    @property
    def agent_database_url(self) -> str:
        # Se estiver em produção e houver string de conexão, podemos usá-la ou continuar usando agent_url
        if self.is_production and self.postgres_conn_string:
            return self.postgres_conn_string.get_secret_value()
        return self._url(self.agent_postgres_user, self.agent_ro_password)

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def agent_sqlalchemy_url(self) -> str:
        url = self.agent_database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print("ambiente carregado: ", settings.enviroment)
    return settings
