from abc import ABC, abstractmethod
from functools import wraps

from flask import request, redirect, url_for


class SessionManager(ABC):
    @abstractmethod
    def key(self) -> str:
        raise NotImplementedError('method .key() must be implemented')

    @abstractmethod
    def encode(self, user_key: str) -> str:
        raise NotImplementedError('method .encode() must be implemented')

    @abstractmethod
    def decode(self, session_value) -> str:
        raise NotImplementedError('method .decode() must be implemented')


class check_session:
    def __init__(self, session_manager: SessionManager):
        self._manager = session_manager

    def __call__(self, func):
        self.func = func

        @wraps(func)
        def _wrapp(*args, **kwargs):
            session_val = request.cookies.get(self._manager.key())
            if not session_val:
                return redirect(url_for('login', error="empty session"))

            user_key = self._manager.decode(session_val)
            request.data["user_id"] = user_key
            return func(*args, **kwargs)

        return _wrapp
