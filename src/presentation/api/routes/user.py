import logging
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.presentation.api.models.user import (
    RequestUserModel,
    RequestAddInfoUserModel,
)
from src.business_logic.services import AdminUserService
from src.dyna_config import DOMAIN_NAME
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from src.data_access.postgresql.repositories import UserRepository
from src.di.providers import provide_async_session_stub


logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=["User"])

templates = Jinja2Templates(directory="src/presentation/api/templates/")


@user_router.get("/add_info/{username}", response_class=HTMLResponse)
async def add_info(
    username: str,
    scope: str,
    request: Request,
    session: AsyncSession = Depends(provide_async_session_stub),
) -> _TemplateResponse:
    user_service = AdminUserService(
        session=session, user_repo=UserRepository(session)
    )
    user_id = (await user_service.user_repo.get_user_by_username(username)).id
    claim_types = (await user_service.user_repo.get_claims(id=user_id)).keys()
    all_fields = []
    if "email" in scope:
        all_fields += ["email"]
    if "profile" in scope:
        all_fields += [
            "name",
            "given_name",
            "family_name",
            "middle_name",
            "preferred_username",
            "last_name",
            "profile",
            "picture",
            "website",
            "gender",
            "phone_number",
            "birthdate",
            "zoneinfo",
            "address",
        ]
    fields = []
    for field in all_fields:
        if field not in claim_types:
            fields.append(field)
    if len(fields) == 0:
        return JSONResponse(status_code=400, content="All data already exists")

    action_url = f"/user/add_info/{username}?scope={scope}"
    return templates.TemplateResponse(
        "user_registration.html",
        {"request": request, "fields": fields, "action_url": action_url},
    )


@user_router.post("/add_info/{username}", status_code=200)
async def add_info(
    username: str,
    request: Request,
    request_body: RequestAddInfoUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub),
) -> None:
    user_service = AdminUserService(
        session=session, user_repo=UserRepository(session)
    )
    new_claims = request_body.__dict__
    await user_service.add_user_info(data=new_claims, username=username)
    await session.commit()
    return templates.TemplateResponse(
        "user_registration_success.html", {"request": request}
    )


@user_router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    request_body: RequestUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub),
) -> _TemplateResponse:
    user_service = AdminUserService(
        session=session, user_repo=UserRepository(session)
    )
    kwargs = request_body.__dict__
    if await user_service.user_repo.validate_user_by_email(
        email=kwargs["email"]
    ):
        return JSONResponse(status_code=400, content="email_duplication")
    if await user_service.user_repo.validate_user_by_username(
        username=kwargs["username"]
    ):
        return JSONResponse(status_code=400, content="username_duplication")
    if kwargs["phone_number"]:
        if await user_service.user_repo.validate_user_by_phone_number(
            phone_number=kwargs["phone_number"]
        ):
            return JSONResponse(
                status_code=400, content="phone_number_duplication"
            )
    await user_service.registration(kwargs)
    await session.commit()
    return templates.TemplateResponse(
        "user_registration_success.html", {"request": request}
    )


@user_router.get("/register/{scope}", response_class=HTMLResponse)
def register(
    scope: str,
    request: Request,
) -> _TemplateResponse:
    fields = [
        "email",
        "username",
        "password",
    ]
    if scope == "profile":
        fields += [
            "name",
            "given_name",
            "family_name",
            "middle_name",
            "preferred_username",
            "last_name",
            "profile",
            "picture",
            "website",
            "gender",
            "phone_number",
            "birthdate",
            "zoneinfo",
            "address",
        ]
    action_url = "/user/register"
    return templates.TemplateResponse(
        "user_registration.html",
        {"request": request, "fields": fields, "action_url": action_url},
    )
