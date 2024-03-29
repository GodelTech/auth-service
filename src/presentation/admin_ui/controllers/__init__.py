import uuid
from sqladmin.authentication import  login_required
from fastapi import HTTPException, Request, status
from sqladmin import Admin, BaseView, ModelView, expose
from sqlalchemy import Boolean, Column
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from src.business_logic.services.password import PasswordHash
from src.dyna_config import IS_DEVELOPMENT

from .auth import AdminAuthController
from .clients import (
    AccessTokenTypeAdminController,
    ClientAdminController,
    ClientClaimController,
    ClientCorsOriginController,
    ClientIdRestrictionController,
    ClientPostLogoutRedirectUriController,
    ClientRedirectUriController,
    ClientSecretController,
    ProtocolTypeController,
    RefreshTokenExpirationTypeController,
    RefreshTokenUsageTypeController,
    ClientScopeController,
    ResponseTypeAdminController,
)
from .device import DeviceAdminController
from .group import GroupAdminController, PermissionAdminController
from .identity_resource import (
    IdentityClaimAdminController,
    IdentityProviderAdminController,
    IdentityProviderMappedAdminController,
    IdentityResourceAdminController,
)
from .persistent_grants import (
    PersistentGrantAdminController,
    PersistentGrantTypeAdminController,
)
from .resources_related import (
    ApiClaimAdminController,
    ApiClaimTypeAdminController,
    ApiResourceAdminController,
    ApiScopeAdminController,
    ApiScopeClaimAdminController,
    ApiScopeClaimTypeAdminController,
    ApiSecretAdminController,
    ApiSecretTypeAdminController,
)
from .roles import RoleAdminController
from .users import (
    TypesUserClaimAdminController,
    UserAdminController,
    UserClaimAdminController,
    PasswordAdminController,
)

from typing import no_type_check

Base = declarative_base()


class SeparationLine(BaseView):
    name = " "

    # icon = "fa-solid fa-chart-line"
    @no_type_check
    @expose("/", methods=["GET"])
    def test_page(self, request) -> None:
        return None


class CustomAdmin(Admin):
    @no_type_check
    @login_required
    async def create(self, request: Request) -> _TemplateResponse:
        # Create model endpoint.
        try:
            await self._create(request)
            identity = request.path_params["identity"]
            model_view = self._find_model_view(identity)
            Form = ...
            if getattr(model_view, "create_excluded_columns", False):
                Form = await model_view.scaffold_form(task="create")
            elif getattr(model_view, "update_excluded_columns", False):
                Form = await model_view.scaffold_form(task="update")
            else:
                Form = await model_view.scaffold_form()
            form_data = await request.form()

            form = Form(form_data)
            if identity == "client-secret":
                value = str(uuid.uuid4())
                form._fields["value"].default = value
                form._fields["value"].data = value

            context = {
                "request": request,
                "model_view": model_view,
                "form": form,
            }

            if request.method == "GET":
                return self.templates.TemplateResponse(
                    model_view.create_template, context
                )

            if not form.validate():
                return self.templates.TemplateResponse(
                    model_view.create_template, context, status_code=400
                )
            obj = ...
            try:
                if identity == "user":
                    dict_form_data = dict(form_data)
                    for key in dict_form_data.keys():
                        if dict_form_data[key] == "False":
                            dict_form_data[key] = False
                        elif dict_form_data[key] == "True":
                            dict_form_data[key] = True
                    obj = await model_view.insert_model(dict_form_data)

                elif identity == "user-password":
                    dict_form_data = dict(form_data)
                    dict_form_data["value"] = PasswordHash.hash_password(
                        dict_form_data["value"]
                    )

                    obj = await model_view.insert_model(dict_form_data)
                else:
                    obj = await model_view.insert_model(form.data)
            except Exception as e:
                context["error"] = str(e)
                return self.templates.TemplateResponse(
                    model_view.create_template, context, status_code=400
                )

            url = self.get_save_redirect_url(
                request=request,
                form=form_data,
                obj=obj,
                model_view=model_view,
            )
            return RedirectResponse(url=url, status_code=302)
        except NoInspectionAvailable as e:
            identity = request.path_params["identity"]
            model_view = self._find_model_view(identity)
            Form = ...
            if getattr(model_view, "create_excluded_columns", False):
                Form = await model_view.scaffold_form(task="create")
            elif getattr(model_view, "update_excluded_columns", False):
                Form = await model_view.scaffold_form(task="update")
            else:
                Form = await model_view.scaffold_form()
            form = Form()

            await self._create(request)
            context = {
                "request": request,
                "model_view": model_view,
                "form": form,
            }
            context["error"] = "Duplication in Foreign Key Column"

            return self.templates.TemplateResponse(
                model_view.create_template, context, status_code=409
            )
