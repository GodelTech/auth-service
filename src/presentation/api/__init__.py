from fastapi import APIRouter
from src.presentation.api.routes.well_known import well_known_router
from src.presentation.api.routes.authorization import auth_router
from src.presentation.api.routes.userinfo import userinfo_router
from src.presentation.api.routes.tokens import token_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(userinfo_router)
router.include_router(well_known_router)
router.include_router(token_router)
