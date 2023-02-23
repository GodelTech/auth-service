from sqladmin import ModelView
from sqladmin.forms import get_model_form

from src.data_access.postgresql.tables.client import *


class ClientAdminController(ModelView, model=Client):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        Client.client_id,
        Client.client_name,
        Client.client_uri,
        Client.created_at,
    ]
    create_excluded_columns = [
        Client.grants,
        Client.created_at,
        Client.updated_at,
        Client.absolute_refresh_token_lifetime,
        Client.access_token_lifetime,
        Client.allow_access_token_via_browser,
        Client.allow_offline_access,
        Client.allow_plain_text_pkce,
        Client.allow_remember_consent,
        Client.always_send_client_claims,
        Client.client_uri,
        Client.enable_local_login,
        Client.enabled,
        Client.identity_token_lifetime,
        Client.include_jwt_id,
        Client.logo_uri,
        Client.logout_session_required,
        Client.prefix_client_claims,
        Client.require_client_secret,
        Client.require_consent,
        Client.require_pkce,
        Client.sliding_refresh_token_lifetime,
        Client.update_access_token_claims_on_refresh,
        Client.authorisation_code_lifetime,
        Client.logout_uri,
        Client.always_include_user_claims_id_token,
        Client.redirect_uris,
        Client.secrets,
        Client.devices,
        Client.post_logout_redirect_uris,
        Client.grant_types,
        Client.claims,
        Client.scopes,
        Client.cors_origins,
        Client.id_restrictions,
    ]

    async def scaffold_form(self, task=None):  # -> Type[Form]:
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


class AccessTokenTypeAdminController(ModelView, model=AccessTokenType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        AccessTokenType.id,
        AccessTokenType.type,
    ]


class ProtocolTypeController(ModelView, model=ProtocolType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ProtocolType.id, ProtocolType.type]


class RefreshTokenUsageTypeController(ModelView, model=RefreshTokenUsageType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [RefreshTokenUsageType.id, RefreshTokenUsageType.type]


class RefreshTokenExpirationTypeController(
    ModelView, model=RefreshTokenExpirationType
):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        RefreshTokenExpirationType.id,
        RefreshTokenExpirationType.type,
    ]


class ClientIdRestrictionController(ModelView, model=ClientIdRestriction):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientIdRestriction.id, ClientIdRestriction.provider]


class ClientClaimController(ModelView, model=ClientClaim):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientClaim.id, ClientClaim.type, ClientClaim.value]


class ClientPostLogoutRedirectUriController(
    ModelView, model=ClientPostLogoutRedirectUri
):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        ClientPostLogoutRedirectUri.id,
        ClientPostLogoutRedirectUri.post_logout_redirect_uri,
        ClientPostLogoutRedirectUri.client,
    ]


class ClientCorsOriginController(ModelView, model=ClientCorsOrigin):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientCorsOrigin.id, ClientCorsOrigin.origin]


class ClientRedirectUriController(ModelView, model=ClientRedirectUri):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientRedirectUri.id, ClientRedirectUri.redirect_uri]


class ClientGrantTypeController(ModelView, model=ClientGrantType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientGrantType.id, ClientGrantType.grant_type]


class ClientSecretController(ModelView, model=ClientSecret):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        ClientSecret.id,
        ClientSecret.type,
        ClientSecret.description,
        ClientSecret.expiration,
        ClientSecret.type,
        ClientSecret.value,
    ]
