from fastapi import APIRouter

from src.presentation.api.routes.authorization import auth_router
from src.presentation.api.routes.tokens import token_router
from src.presentation.api.routes.userinfo import userinfo_router
from src.presentation.api.routes.well_known import well_known_router
<<<<<<< src/presentation/api/__init__.py
from src.presentation.api.routes.revoke import revoke_router
=======
from src.presentation.api.routes.introspection import introspection_router
>>>>>>> src/presentation/api/__init__.py

router = APIRouter()
router.include_router(auth_router)
router.include_router(userinfo_router)
router.include_router(well_known_router)
router.include_router(token_router)
<<<<<<< src/presentation/api/__init__.py
router.include_router(revoke_router)
=======
router.include_router(introspection_router)
>>>>>>> src/presentation/api/__init__.py