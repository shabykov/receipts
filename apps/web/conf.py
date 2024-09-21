from dotenv import load_dotenv
from pydantic import (
    Field,
    SecretStr,
    PostgresDsn,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

load_dotenv()


class Settings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding='utf-8'
    )
    telegram_bot_token: SecretStr
    web_port: int = Field(
        default=8080
    )
    web_host: str = Field(
        default="0.0.0.0"
    )
    logging_level: str = Field(
        default="INFO"
    )
    postgresql_url: PostgresDsn


def init_settings() -> Settings:
    return Settings()
