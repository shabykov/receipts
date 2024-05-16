from dotenv import load_dotenv
from pydantic import SecretStr
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
    openai_api_key: SecretStr


def init_settings() -> Settings:
    return Settings()
