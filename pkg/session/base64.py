import base64

from .interface import SessionManager


class Base64SessionManager(SessionManager):
    def __init__(self, session_key: str = "user_id"):
        self._key_name = session_key

    def key(self) -> str:
        return self._key_name

    def encode(self, user_id: str) -> str:
        return base64.b64encode(user_id.encode('utf-8')).decode('utf-8')

    def decode(self, session_value: str) -> str:
        return base64.b64decode(session_value.encode('utf-8')).decode('utf-8')
