import base64

from .interface import SessionManager


class Base64SessionManager(SessionManager):
    def __init__(self, session_key: str = "session_id"):
        self._key_name = session_key

    def key(self) -> str:
        return self._key_name

    def encode_key(self, user_key: str) -> str:
        return base64.b64encode(user_key.encode('utf-8')).decode('utf-8')

    def decode_val(self, session_value: str) -> str:
        return base64.b64decode(session_value.encode('utf-8')).decode('utf-8')
