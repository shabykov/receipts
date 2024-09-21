import typing as t

from flask import (
    url_for,
    Request,
    session,
    redirect,
    render_template,
)
from pydantic import ValidationError

from internal.domain.user import new
from internal.usecase.interface import IUserReadUC
from pkg.auth.telegram import TelegramAuth, AuthData
from pkg.session import SessionManager


class LoginHandler:
    def __init__(
            self,
            auth: TelegramAuth,
            session_manager: SessionManager,
            user_uc: IUserReadUC,
    ):
        self.auth = auth
        self.session_manager = session_manager
        self.user_uc = user_uc

    def login(self, request: Request) -> t.Any:
        return render_template(
            'login.html',
            success_message=request.args.get("success"),
            error_message=request.args.get("error")
        )

    def telegram_login_callback(self, request: Request) -> t.Any:
        try:
            data = AuthData.model_validate(request.args.to_dict())
        except ValidationError as err:
            return redirect(url_for('login', error=str(err)))

        if self.auth.authenticate(data):
            # create user
            user = self.user_uc.get_or_create(
                new(data.id, data.username)
            )

            # set cookie
            session["user_id"] = user.user_id
            return redirect(
                location=url_for(
                    'login',
                    success="authentication is successful"
                ),
            )

        return redirect(
            url_for(
                'login',
                error="authentication is failed"
            )
        )