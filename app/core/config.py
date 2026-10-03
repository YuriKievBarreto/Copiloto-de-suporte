from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr
from urllib.parse import quote_plus



RAIZ = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=RAIZ / ".env",
        env_file_encoding="utf-8",
        extra="ignore", 
    )

    postgres_user: str = "helpdesk"
    postgres_password: SecretStr
    postgres_db: str = "helpdesk"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432



    ## QDRANT
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: SecretStr | None = None
    qdrant_collection: str = "helpdesk_docs"


    hf_token: SecretStr  # obrigatório
    embedding_model: str = "BAAI/bge-m3"

    def _url(self, usuario: str, senha: SecretStr) -> str:
        senha_codificada = quote_plus(senha.get_secret_value())
        return (
            f"postgresql://{usuario}:{senha_codificada}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


    @property
    def database_url(self) -> str:
        return self._url(self.postgres_user, self.postgres_password)

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
 