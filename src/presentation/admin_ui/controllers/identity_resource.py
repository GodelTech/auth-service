from sqladmin import ModelView
from src.data_access.postgresql.tables import IdentityClaim, IdentityResource, IdentityProviderMapped


class IdentityResourceAdminController(ModelView, model=IdentityResource):
    icon = "fa-solid fa-fingerprint"
    column_list = [ IdentityResource.id, 
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
    column_list = [IdentityClaim.id, 
                   IdentityClaim.identity_resource, 
                   ]

class IdentityProviderMappedAdminController(ModelView, model = IdentityProviderMapped):
    icon = "fa-solid fa-fingerprint"
    name_plural = "Identity Providers"
    column_list  = [
        IdentityProviderMapped.id,
        IdentityProviderMapped.identity_provider,
        IdentityProviderMapped.provider_client_id,
        IdentityProviderMapped.enabled,
    ]