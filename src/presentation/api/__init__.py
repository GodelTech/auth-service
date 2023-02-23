from fastapi import APIRouter

from src.presentation.admin_api import admin_router
from src.presentation.api.routes.authorization import auth_router
from src.presentation.api.routes.device_authorization import device_auth_router
from src.presentation.api.routes.endsession import endsession_router
from src.presentation.api.routes.introspection import introspection_router
from src.presentation.api.routes.revoke import revoke_router
from src.presentation.api.routes.third_party_oidc_authorization import (
    auth_oidc_router,
)
from src.presentation.api.routes.tokens import token_router
from src.presentation.api.routes.userinfo import userinfo_router
from src.presentation.api.routes.well_known import well_known_router

router = APIRouter()
router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(device_auth_router)
router.include_router(userinfo_router)
router.include_router(well_known_router)
router.include_router(endsession_router)
router.include_router(token_router)
router.include_router(introspection_router)
router.include_router(revoke_router)
router.include_router(auth_oidc_router)
