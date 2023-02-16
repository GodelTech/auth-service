# https://docs.google.com/spreadsheets/d/1zJAcCxaGz2CV9zKlqeBhRE8xfiqyJMy5-XPRH1I8HPg/edit#gid=0
from typing import Any, Dict, List, Optional, Union

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.well_known import WellKnownServies
from src.data_access.postgresql.repositories.groups import GroupRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.data_access.postgresql.repositories.roles import RoleRepository
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.tables.group import Group
from src.data_access.postgresql.tables.users import Role, User


class AdminService:
    def __init__(
        self,
        jwt_service: JWTService,
    ) -> None:
        # self.user_service = AdminUserService()
        # self.group_service = AdminGroupService()
        # self.role_service = AdminRoleService()
        # self.well_known = AdminUriService()
        self.jwt_service = jwt_service

    async def add_swagger_config(self) -> None:
        pass

    async def proxy(self) -> None:
        pass

    async def admin_token(self) -> None:
        pass

    async def get_identity_providers(self) -> None:
        pass


class AdminTokenService:
    def __init__(self, grant_repo: PersistentGrantRepository) -> None:
        self.grant_repo = grant_repo

    async def get_admin_token(self) -> None:
        pass

    async def exchange_authorization_code(self) -> None:
        pass


class AdminRoleService:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    async def get_role(self, role_id: int) -> Role:
        return await self.role_repo.get_role_by_id(role_id=role_id)

    async def get_roles(self, role_ids: str) -> list[Role]:
        new_role_ids = [int(number) for number in role_ids.split(",")]
        return [
            await self.role_repo.get_role_by_id(role_id=role_id)
            for role_id in new_role_ids
        ]

    async def get_all_roles(self) -> list[Role]:
        return await self.role_repo.get_all_roles()

    async def create_role(self, **kwargs: Any) -> None:
        return await self.role_repo.create(**kwargs)

    async def update_role(self, role_id: int, **kwargs: Any) -> None:
        return await self.role_repo.update(role_id=role_id, **kwargs)

    async def delete_role(self, role_id: int) -> bool:
        return await self.role_repo.delete(role_id=role_id)


class AdminGroupService:
    def __init__(self, group_repo: GroupRepository) -> None:
        self.group_repo = group_repo

    async def get_all_groups(self) -> List[Group]:
        return await self.group_repo.get_all_groups()

    async def get_groups(self, group_ids: list[int]) -> list[Group]:
        result = []
        for group_id in group_ids:
            result.append(await self.group_repo.get_by_id(group_id=group_id))
        return result

    async def get_subgroups(self, group_id: int) -> Dict[str, Any]:
        group = await self.group_repo.get_by_id(group_id=group_id)
        result = await self.group_repo.get_all_subgroups(main_group=group)
        return result

    async def update_group(self, group_id: int, **kwargs: Any) -> None:
        await self.group_repo.update(group_id=group_id, **kwargs)

    async def get_group_by_path(self) -> None:
        pass

    async def get_group(self, group_id: int) -> Group:
        return await self.group_repo.get_by_id(group_id=group_id)

    async def create_group(self, **kwargs: Any) -> None:
        await self.group_repo.create(**kwargs)

    async def delete_group(self, group_id: int) -> None:
        return await self.group_repo.delete(group_id=group_id)


class AdminUserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def user_auth_scheme(self) -> None:
        pass

    async def get_current_user(self) -> None:
        pass

    async def current_user(self) -> None:
        pass

    async def add_user_roles(self, user_id: int, role_ids: str) -> None:
        new_role_ids = [int(number) for number in role_ids.split(",")]
        for role_id in new_role_ids:
            await self.user_repo.add_role(user_id=user_id, role_id=role_id)

    async def remove_user_roles(self, user_id: int, role_ids: str) -> bool:
        return await self.user_repo.remove_user_roles(
            user_id=user_id, role_ids=role_ids
        )

    async def get_user_roles(self, user_id: int) -> List[Role]:
        return await self.user_repo.get_roles(user_id=user_id)

    async def add_user_groups(self, user_id: int, group_ids: str) -> None:
        new_group_ids = [int(number) for number in group_ids.split(",")]
        for group_id in new_group_ids:
            await self.user_repo.add_group(user_id=user_id, group_id=group_id)

    async def get_user_groups(self, user_id: int) -> List[Group]:
        return await self.user_repo.get_groups(user_id=user_id)

    async def remove_user_groups(
        self, user_id: int, group_ids: List[int]
    ) -> None:
        return await self.user_repo.remove_user_groups(
            user_id=user_id, group_ids=group_ids
        )

    async def create_user(self, kwargs: Any) -> None:
        kwargs = kwargs | {
            "email_confirmed": False,
            "phone_number_confirmed": False,
            "access_failed_count": 0,
        }
        return await self.user_repo.create(**kwargs)

    async def change_password(self, user_id: int, new_password: str) -> None:
        new_password = PasswordHash.hash_password(password=new_password)
        await self.user_repo.update(user_id=user_id, password_hash=new_password)

    async def send_email_verification(self) -> None:
        pass

    async def get_user(self, user_id: int) -> User:
        return await self.user_repo.get_user_by_id(user_id=user_id)

    async def update_user(self, user_id: int, kwargs: Any) -> None:
        await self.user_repo.update(user_id=user_id, **kwargs)

    async def delete_user(self, user_id: int) -> None:
        await self.user_repo.delete(user_id=user_id)

    async def get_all_users(
        self,
        group_id: Union[int, None] = None,
        role_id: Union[int, None] = None,
    ) -> List[User]:
        return await self.user_repo.get_all_users(
            group_id=group_id, role_id=role_id
        )

    async def user_login(self) -> None:
        pass

    async def admin_request(self) -> None:
        pass


class AdminUriService(WellKnownServies):
    def __init__(self) -> None:
        super().__init__()
        self.open_id_dict = self.get_openid_configuration

    async def login_uri(self) -> None:
        pass

    async def authorization_uri(self) -> Any:
        id_dict = await self.open_id_dict()
        if id_dict is not None:
            return id_dict["authorization_endpoint"]

    async def token_uri(self) -> Any:
        id_dict = await self.open_id_dict()
        if id_dict is not None:
            return id_dict["token_endpoint"]

    async def logout_uri(self) -> Any:
        id_dict = await self.open_id_dict()
        if id_dict is not None:
            return id_dict["endsession_endpoint"]

    async def users_uri(self) -> Any:
        id_dict = await self.open_id_dict()
        if id_dict is not None:
            return id_dict["userinfo_endpoint"]

    # async def roles_uri(self):
    #     pass

    # async def groups_uri(self):
    #     pass

    async def admin_uri(self) -> None:
        pass

    async def providers_uri(self) -> None:
        pass

    async def open_id(self) -> None:
        pass

    async def open_id_configuration(self) -> None:
        pass

    async def public_key(self) -> None:
        pass
