import hashlib
import hmac
import typing as t
from pydantic import BaseModel, SecretStr, Field

KEY_STRING = (
    "auth_date={auth_date}\n"
    "first_name={first_name}\n"
    "id={id}\n"
    "last_name={last_name}\n"
    "photo_url={photo_url}\n"
    "username={username}"
)


class AuthData(BaseModel):
    id: int
    username: str
    first_name: t.Optional[str] = Field(
        default=""
    )
    last_name: t.Optional[str] = Field(
        default=""
    )
    photo_url: t.Optional[str] = Field(
        default=""
    )
    auth_date: str
    hash: str

    def __str__(self):
        return KEY_STRING.format(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            photo_url=self.photo_url,
            auth_date=self.auth_date
        )


class TelegramAuth:
    def __init__(self, bot_token: SecretStr):
        self._token = bot_token

    def authenticate(self, data: AuthData) -> bool:

        secret_key = hashlib.sha256(self._token.get_secret_value().encode('utf-8')).digest()

        check_data = str(data)

        hmac_string = hmac.new(secret_key, check_data.encode('utf-8'), hashlib.sha256).hexdigest()

        return data.hash == hmac_string
