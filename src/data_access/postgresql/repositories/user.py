from typing import Any, Dict, Optional, Tuple, Union

from sqlalchemy import (
    exists,
    insert,
    join,
    select,
    text,
    update,
    delete
)
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    DuplicationError,
    NoPasswordError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import (
    IdentityProvider,
    Role,
    User,
    UserClaim,
    UserClaimType,
    UserPassword,
)
from src.data_access.postgresql.tables.group import Group
from src.data_access.postgresql.tables.users import users_groups, users_roles


def params_to_dict(**kwargs: Any) -> Dict[str, Any]:
    result = {}
    for key in kwargs:
        if kwargs[key] is not None:
            result[key] = kwargs[key]
    return result


class UserRepository(BaseRepository):
    async def exists(self, user_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(exists().where(User.id == user_id))
            )
            result = result.first()
            return result[0]

    async def delete(self, user_id: int) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(user_id=user_id):
                user_to_delete = await self.get_user_by_id(user_id=user_id)
                await session.delete(user_to_delete)
                await session.commit()
            else:
                raise ValueError

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                user = await session.execute(
                    select(User)
                    .join(
                        UserPassword,
                        User.password_hash_id == UserPassword.id,
                        isouter=True,
                    )
                    .join(
                        IdentityProvider,
                        User.identity_provider_id == IdentityProvider.id,
                        isouter=True,
                    )
                    .where(User.id == user_id)
                )
                user = user.first()

                return user[0]
        except:
            raise ValueError

    async def get_hash_password(self, user_name: str) -> Tuple[str, int]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            user = await session.execute(
                select(User)
                .join(UserPassword, User.password_hash_id == UserPassword.id)
                .where(User.username == user_name)
            )
            user = user.first()

            if user is None:
                raise UserNotFoundError(
                    "User you are looking for does not exist"
                )

            return user[0].password_hash.value, user[0].id

    async def get_claims(self, id: int) -> Dict[str, Any]:
        claims_of_user = await self.request_DB_for_claims(id)
        result = {}

        for claim in claims_of_user:
            result[claim[0].claim_type.type_of_claim] = claim[0].claim_value

        if not result:
            raise ClaimsNotFoundError(
                "Claims for user you are looking for does not exist"
            )

        return result

    async def request_DB_for_claims(self, sub: int) -> ChunkedIteratorResult:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(UserClaim)
                .where(UserClaim.user_id == sub)
                .join(
                    UserClaimType, UserClaimType.id == UserClaim.claim_type_id
                )
            )
            return result

    async def get_username_by_id(self, id: int) -> str:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            users = await session.execute(select(User).where(User.id == id))
            result = users.first()
            result = result[0].username
            return result

    async def get_user_by_username(self, username: str) -> User:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                user = await session.execute(
                    select(User)
                    .join(
                        UserPassword,
                        User.password_hash_id == UserPassword.id,
                        isouter=True,
                    )
                    .join(
                        IdentityProvider,
                        User.identity_provider_id == IdentityProvider.id,
                        isouter=True,
                    )
                    .where(User.username == username)
                )
                user = user.first()

                return user[0]
        except:
            raise ValueError

    async def get_all_users(
        self, group_id: Optional[int] = None, role_id: Optional[int] = None
    ) -> list[User]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                if group_id is None and role_id is None:
                    query = await session.execute(select(User))
                    query = query.all()
                    return [user[0] for user in query]
                elif group_id is None and role_id is not None:
                    iterator = await session.execute(
                        select(User)
                        .join(Role, User.roles)
                        .where(Role.id == role_id)
                    )
                    return [user[0] for user in iterator.all()]
                elif group_id is not None and role_id is None:
                    iterator = await session.execute(
                        select(User)
                        .join(Group, User.groups)
                        .where(Group.id == group_id)
                    )
                    return [user[0] for user in iterator.all()]
                else:
                    iterator = await session.execute(
                        select(User)
                        .join(Group, User.groups)
                        .join(Role, User.roles)
                        .where(Group.id == group_id, Role.id == role_id)
                    )
                    return [user[0] for user in iterator.all()]
        except:
            raise ValueError

    async def update(
        self,
        user_id: int,
        id: Union[None, str] = None,
        username: Union[None, str] = None,
        security_stamp: Union[None, str] = None,
        email: Union[None, str] = None,
        email_confirmed: Union[None, bool] = None,
        phone_number: Union[None, str] = None,
        phone_number_confirmed: Union[None, bool] = None,
        two_factors_enabled: Union[None, bool] = None,
        lockout_end_date_utc: Union[None, str] = None,
        password_hash: Union[None, str] = None,
        lockout_enabled: Union[None, bool] = False,
        access_failed_count: Union[None, int] = None,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            kwargs = params_to_dict(
                id=id,
                username=username,
                security_stamp=security_stamp,
                email=email,
                email_confirmed=email_confirmed,
                phone_number=phone_number,
                phone_number_confirmed=phone_number_confirmed,
                two_factors_enabled=two_factors_enabled,
                lockout_end_date_utc=lockout_end_date_utc,
                lockout_enabled=lockout_enabled,
                password_hash=password_hash,
                access_failed_count=access_failed_count,
            )
            async with session_factory() as sess:
                session = sess
                if await self.exists(user_id=user_id):
                    updates = (
                        update(User).values(**kwargs).where(User.id == user_id)
                    )
                    await session.execute(updates)
                    await session.commit()
                else:
                    raise ValueError
        except:
            raise DuplicationError

    async def create(
        self,
        id: Union[None, int] = None,
        username: Union[None, str] = None,
        identity_provider_id: Union[None, int] = None,
        security_stamp: Union[None, str] = None,
        email: Union[None, str] = None,
        email_confirmed: Union[None, bool] = None,
        phone_number: Union[None, str] = None,
        phone_number_confirmed: Union[None, bool] = None,
        two_factors_enabled: Union[None, bool] = None,
        lockout_end_date_utc: Union[None, str] = None,
        password_hash_id: Union[None, int] = None,
        lockout_enabled: Union[None, bool] = False,
        access_failed_count: Union[None, int] = 0,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            kwargs = params_to_dict(
                id=id,
                username=username,
                identity_provider_id=identity_provider_id,
                security_stamp=security_stamp,
                email=email,
                email_confirmed=email_confirmed,
                phone_number=phone_number,
                phone_number_confirmed=phone_number_confirmed,
                two_factors_enabled=two_factors_enabled,
                lockout_end_date_utc=lockout_end_date_utc,
                lockout_enabled=lockout_enabled,
                password_hash_id=password_hash_id,
                access_failed_count=access_failed_count,
            )
            async with session_factory() as sess:
                session = sess

                await session.execute(insert(User).values(**kwargs))
                await session.commit()
        except:
            raise DuplicationError

    async def add_group(self, user_id: int, group_id: int) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                flag_one = (
                    await session.execute(
                        select(exists().where(Group.id == group_id))
                    )
                ).first()[0]
                flag_two = (
                    await session.execute(
                        select(exists().where(User.id == user_id))
                    )
                ).first()[0]
                if flag_one and flag_two:
                    await session.execute(
                        insert(users_groups).values(
                            user_id=user_id, group_id=group_id
                        )
                    )
                    await session.commit()
                elif not flag_two or not flag_one:
                    raise ValueError
        except ValueError:
            raise ValueError
        except:
            raise DuplicationError

    async def add_role(self, user_id: int, role_id: int) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                await session.execute(
                    insert(users_roles).values(
                        user_id=user_id, role_id=role_id
                    )
                )
                await session.commit()
        except:
            raise DuplicationError

    async def remove_user_groups(self, user_id: int, group_ids: str) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        # prepare a list of ids for the IN statement
        group_ids_list = list(map(int, group_ids.split(",")))

        try:
            async with session_factory() as session:
                query = (
                    delete(users_groups)
                    .where(users_groups.c.user_id == user_id)
                    .where(users_groups.c.group_id.in_(group_ids_list))
                )

                await session.execute(query)
                await session.commit()
        except:
            raise ValueError

    async def remove_user_roles(self, user_id: int, role_ids: str) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        # prepare a list of ids for the IN statement
        role_ids_list = list(map(int, role_ids.split(",")))

        try:
            async with session_factory() as session:
                query = (
                    delete(users_roles)
                    .where(users_roles.c.user_id == user_id)
                    .where(users_roles.c.role_id.in_(role_ids_list))
                )

                await session.execute(query)
                await session.commit()
        except:
            raise ValueError

    async def get_roles(self, user_id: int) -> list[Role]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                iterator = await session.execute(
                    select(Role)
                    .join(User, Role.users)
                    .where(User.id == user_id)
                )
                result = [role[0] for role in iterator.all()]
                return result
        except:
            raise ValueError

    async def get_groups(self, user_id: int) -> list[Group]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                iterator = await session.execute(
                    select(Group)
                    .join(User, Group.users)
                    .where(User.id == user_id)
                )
                result = [group[0] for group in iterator.all()]
                return result
        except:
            raise ValueError

    async def change_password(
        self, user_id: int, password: Optional[str] = None
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            user = await self.get_user_by_id(user_id=user_id)
            if user:
                if password is None:
                    updates = (
                        update(User)
                        .values(password_hash_id=None)
                        .where(User.id == user_id)
                    )
                    await session.execute(updates)
                    if not user.password_hash_id:
                        password_to_delete = (
                            await session.execute(
                                select(UserPassword).where(
                                    UserPassword.id == user.password_hash_id
                                )
                            )
                        ).first()
                        await session.delete(password_to_delete)
                    await session.commit()
                else:
                    if user.password_hash_id:
                        updates = (
                            update(UserPassword)
                            .values(value=password)
                            .where(UserPassword.id == user.password_hash_id)
                        )
                        await session.execute(updates)
                        await session.commit()
                    else:
                        await session.execute(
                            insert(UserPassword).values(value=password)
                        )
                        password_id = await session.execute(
                            select(UserPassword).where(
                                UserPassword.value == password
                            )
                        )
                        password_id = password_id.first()[0].id
                        updates = (
                            update(User)
                            .values(password_hash_id=password_id)
                            .where(User.id == user_id)
                        )
                        await session.execute(updates)
                        await session.commit()
            else:
                raise ValueError

    async def validate_user_by_username(self, username: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(exists().where(User.username == username))
            )
            result = result.first()
            return result[0]

    def __repr__(self) -> str:  # pragma: no cover
        return "User repository"
