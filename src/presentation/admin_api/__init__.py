from fastapi import APIRouter

from src.presentation.admin_api.routes.user import admin_user_router
from src.presentation.admin_api.routes.group import admin_group_router
from src.presentation.admin_api.routes.role import admin_role_router 

admin_router = APIRouter(prefix="/administration")
admin_router.include_router(admin_user_router)
admin_router.include_router(admin_group_router)
admin_router.include_router(admin_role_router)