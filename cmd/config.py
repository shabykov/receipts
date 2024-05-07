from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding='utf-8'
    )
    telegram_bot_token: SecretStr
    openai_api_key: SecretStr


def init_settings() -> Settings:
    return Settings()
