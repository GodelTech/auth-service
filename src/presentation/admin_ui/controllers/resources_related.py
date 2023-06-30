from sqladmin import ModelView
from src.data_access.postgresql.tables import (
    ApiClaim, 
    ApiClaimType, 
    ApiResource, 
    ApiScope, 
    ApiScopeClaim, 
    ApiScopeClaimType, 
    ApiSecret, 
    ApiSecretType,  
)

class ApiResourceAdminController(ModelView, model=ApiResource):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiResource.id, 
                   ApiResource.name, 
                   ApiResource.description,
                   ]

class ApiSecretAdminController(ModelView, model=ApiSecret):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiSecret.id, 
                   ApiSecret.api_resources,
                   ApiSecret.description,
                   ApiSecret.secret_type]
    
class ApiSecretTypeAdminController(ModelView, model=ApiSecretType):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiSecretType.id, 
                   ApiSecretType.secret_type,]
    
class ApiClaimAdminController(ModelView, model=ApiClaim):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiClaim.api_resources, 
                   ApiClaim.claim_type,]

class ApiClaimTypeAdminController(ModelView, model=ApiClaimType):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiClaimType.id, 
                   ApiClaimType.claim_type,]
    
class ApiScopeAdminController(ModelView, model=ApiScope):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiScope.id, 
                   ApiScope.api_resources,
                   ApiScope.description,
                   ApiScope.display_name,
                   ApiScope.emphasize,
                   ]
    
class ApiScopeClaimAdminController(ModelView, model=ApiScopeClaim):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiScopeClaim.id, 
                   ApiScopeClaim.api_scopes,
                   ApiScopeClaim.scope_claim_type,
                   ]
    
class ApiScopeClaimTypeAdminController(ModelView, model=ApiScopeClaimType):
    icon = "fa-solid fa-network-wired"
    column_list = [ApiScopeClaimType.id,
                   ApiScopeClaimType.scope_claim, 
                   ApiScopeClaimType.scope_claim_type,
                   ]