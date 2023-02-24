from sqladmin import ModelView
from sqladmin.forms import get_model_form
from typing import Type, no_type_check
from src.data_access.postgresql.tables import (
    User,
    UserClaim,
    UserClaimType,
    UserLogin,
    UserPassword,
)
from wtforms import Form

class UserAdminController(
    ModelView,
    model=User,
):
    icon = "fa-solid fa-user"
    # column_labels = {User.username: "username"}
    column_list = [User.id, User.username, User.claims]
    create_excluded_columns = [
        User.groups,
        User.claims,
        User.roles,
        User.grants,
        User.lockout_enabled,
        User.created_at,
        User.updated_at,
        User.lockout_enabled,
        User.lockout_end_date_utc,
        User.access_failed_count,
        User.password_hash,
        User.identity_provider,
        User.email,
        User.email_confirmed,
        User.phone_number,
        User.security_stamp,
        User.two_factors_enabled,
        User.phone_number_confirmed,
    ]
    
    @no_type_check
    async def scaffold_form(self, task=None) -> Type[Form]:
        if self.form is not None:
            return self.form

        exclude = []

        if task is None:
            exclude = None
        elif task == "create":
            exclude = [i.key for i in self.create_excluded_columns]
        else:
            raise AttributeError(f"{task} is not defined")

        return await get_model_form(
            model=self.model,
            engine=self.engine,
            exclude=exclude,
            only=[i[1].key or i[1].name for i in self._form_attrs],
            column_labels={k.key: v for k, v in self._column_labels.items()},
            form_args=self.form_args,
            form_widget_args=self.form_widget_args,
            form_class=self.form_base_class,
            form_overrides=self.form_overrides,
            form_ajax_refs=self._form_ajax_refs,
            form_include_pk=self.form_include_pk,
        )


class UserClaimAdminController(ModelView, model=UserClaim):
    icon = "fa-solid fa-user"

    column_list = [UserClaim.claim_type, UserClaim.claim_value, UserClaim.user]


class TypesUserClaimAdminController(ModelView, model=UserClaimType):
    icon = "fa-solid fa-user"
    column_list = [
        UserClaimType.id,
        UserClaimType.type_of_claim,
    ]

class PasswordAdminController(ModelView, model=UserPassword):
    icon = "fa-solid fa-user"
    name = "Password"
    form_excluded_columns = [UserPassword.created_at, UserPassword.updated_at]
    column_list = [
        UserPassword.user,
        UserPassword.value,
    ]