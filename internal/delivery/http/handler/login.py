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


class LoginHandler:
    def __init__(
            self,
            auth: TelegramAuth,
            user_uc: IUserReadUC,
    ):
        self.auth = auth
        self.user_uc = user_uc

    def login(self, request: Request) -> t.Any:
        return render_template(
            'login.html',
            receipt_uuid=request.args.get("receipt_uuid"),
            success_message=request.args.get("success"),
            error_message=request.args.get("error")
        )

    def telegram_login_callback(self, request: Request) -> t.Any:
        try:
            data = AuthData.model_validate(request.args.to_dict())
        except ValidationError as err:
            return redirect(
                url_for(
                    endpoint='login',
                    error=str(err),
                    receipt_uuid=request.args.get("receipt_uuid"),
                )
            )

        if self.auth.authenticate(data):
            # create user
            user = self.user_uc.get_or_create(
                new(data.id, data.username)
            )

            # set cookie
            session["user_id"] = user.user_id

            if request.args.get("receipt_uuid"):
                return redirect(
                    location=url_for(
                        endpoint="show",
                        receipt_uuid=request.args.get("receipt_uuid")
                    )
                )

            return redirect(
                location=url_for(
                    'login',
                    success="authentication is successful",
                    receipt_uuid=request.args.get("receipt_uuid")
                ),
            )

        return redirect(
            url_for(
                'login',
                error="authentication is failed",
                receipt_uuid=request.args.get("receipt_uuid")
            )
        )
