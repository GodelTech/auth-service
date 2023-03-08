from sqladmin import ModelView, expose
from typing import no_type_check
from src.data_access.postgresql.tables import (
    IdentityClaim,
    IdentityProvider,
    IdentityProviderMapped,
    IdentityResource,
)

class IdentityResourceAdminController(ModelView, model=IdentityResource):
    icon = "fa-solid fa-fingerprint"
    column_list = [
        IdentityResource.id,
        IdentityResource.description,
        IdentityResource.display_name,
        IdentityResource.emphasize,
        IdentityResource.enabled,
        IdentityResource.name,
        IdentityResource.required,
        IdentityResource.show_in_discovery_document,
        IdentityResource.identity_claim,
    ]


class IdentityClaimAdminController(ModelView, model=IdentityClaim):
    icon = "fa-solid fa-fingerprint"
    column_list = [
        IdentityClaim.id,
        IdentityClaim.identity_resource,
    ]


class IdentityProviderMappedAdminController(
    ModelView, model=IdentityProviderMapped
):
    icon = "fa-solid fa-fingerprint"
    name_plural = "Identity Providers Mapped"
    create_template = 'identity_provider_with_copy_uri_button.html'

    column_list = [
        IdentityProviderMapped.id,
        IdentityProviderMapped.identity_provider,
        IdentityProviderMapped.provider_client_id,
        IdentityProviderMapped.enabled,
    ]


class IdentityProviderAdminController(ModelView, model=IdentityProvider):
    icon = "fa-solid fa-fingerprint"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        IdentityProvider.id,
        IdentityProvider.name,
        IdentityProvider.identity_providers_mapped,
    ]
