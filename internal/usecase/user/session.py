import typing as t

from flask import session

from internal.domain.user import User
from internal.domain.user.id import UserId
from internal.usecase.interface import IUserReadUC, IUserSessionUC


class UserSessionUseCase(IUserSessionUC):
    def __init__(self, user_uc: IUserReadUC):
        self.user_uc = user_uc

    def check(self) -> t.Optional[User]:
        user_id = session.get("user_id")
        if not user_id:
            return

        user = self.user_uc.get_by_id(
            UserId(user_id)
        )
        if not user:
            return

        return user
