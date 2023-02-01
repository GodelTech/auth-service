from sqlalchemy import select, exists, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.data_access.postgresql.tables.group import Group
from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import User, UserClaim, Role
from src.data_access.postgresql.tables.users import users_roles, users_groups
from src.data_access.postgresql.errors.user import DuplicationError 

class UserRepository(BaseRepository):
    async def exists(self, user_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    [
                        exists().where(
                            User.id == user_id
                        )
                    ]
                )
            )
            result = result.first()
            return result[0]

    async def delete(self, user_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(user_id=user_id):
                user_to_delete = await self.get_user_by_id(user_id=user_id)
                await session.delete(user_to_delete)
                await session.commit()
                return True
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
                    select(User).where(User.id == user_id)
                )
                user = user.first()

                return user[0]
        except:
            raise ValueError

    async def get_hash_password(self, user_name: str) -> tuple:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            user = await session.execute(
                select(User).where(User.username == user_name)
            )
            user = user.first()

            if user is None:
                raise UserNotFoundError(
                    "User you are looking for does not exist")

            user = user[0]
            return user.password_hash, user.id

    async def get_claims(self, id: int) -> dict:
        claims_of_user = await self.request_DB_for_claims(id)
        result = {}

        for claim in claims_of_user:
            result[dict(claim)["UserClaim"].claim_type.code] = dict(claim)[
                "UserClaim"
            ].claim_value

        if not result:
            raise ClaimsNotFoundError(
                "Claims for user you are looking for does not exist"
            )

        return result

    async def request_DB_for_claims(self, id):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            return await session.execute(
                select(UserClaim).where(UserClaim.user_id == id)
            )

    async def get_username_by_id(self, id: int) -> str:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            users = await session.execute(select(User).where(User.id == id))
            result = []
            result = dict(next(users))["User"].username

            return result

    async def get_all_users(self, group_id: int = None, role_id: int = None) -> list[User]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                if group_id is None and role_id is None:
                    quiery = await session.execute(
                        select(User)
                    )
                    quiery = quiery.all()
                    return [user[0] for user in quiery]
                elif group_id is None and role_id is not None:
                    iterator = await session.execute(
                        select(User)
                        .join(
                            Role,
                            User.roles
                        )
                        .where(Role.id == role_id)
                    )
                    return [user[0] for user in iterator.all()]
                elif group_id is not None and role_id is None:
                    iterator = await session.execute(
                        select(User)
                        .join(
                            Group,
                            User.groups
                        )
                        .where(Group.id == group_id)
                    )
                    return [user[0] for user in iterator.all()]
                else:
                    iterator = await session.execute(
                        select(User)
                        .join(Group, User.groups)
                        .join(Role, User.roles)
                        .where(
                            Group.id == group_id,
                            Role.id == role_id
                        )
                    )
                    return [user[0] for user in iterator.all()]
        except:
            raise ValueError

    async def update(self, user_id: int, **kwargs) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                if await self.exists(user_id=user_id):
                    updates = update(User).values(
                        **kwargs).where(User.id == user_id)
                    await session.execute(updates)
                    await session.commit()
                    return True
                else:
                    raise ValueError
        except:
            raise DuplicationError
            
    async def create(self, **kwargs) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess

                await session.execute(
                    insert(User).values(**kwargs)
                )
                await session.commit()
                return True
        except:
            raise DuplicationError

    async def add_group(self, user_id:int, group_id:int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess
                await session.execute(
                    insert(users_groups).values(user_id = user_id, group_id = group_id)
                    )
                await session.commit()
                return True
        except:
            return DuplicationError

    async def add_role(self, user_id:int, role_id:int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess
                await session.execute(
                    insert(users_roles).values(user_id = user_id, role_id = role_id)
                    )
                await session.commit()
                return True
        except:
            return DuplicationError

    async def remove_user_groups(self, user_id:int, group_ids:list) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess

                if len(group_ids) == 0:
                    return False
                elif len(group_ids) == 1:
                    group_ids = group_ids[0]
                else:
                    group_ids = str(group_ids)[1:-1]

                sql = f"DELETE FROM users_groups WHERE user_id = {user_id} AND group_id IN ({group_ids})"
                await session.execute(sql)
                await session.commit()
            return True
        except:
            return ValueError

    async def remove_user_roles(self, user_id:int, role_ids:list) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess

                if len(role_ids) == 0:
                    return False
                elif len(role_ids) == 1:
                    role_ids = role_ids[0]
                else:
                    role_ids = str(role_ids)[1:-1]

                sql = f"DELETE FROM users_roles WHERE user_id = {user_id} AND role_id IN ({role_ids})"
                await session.execute(sql)
                await session.commit()
            return True
        except:
            return False

    async def get_roles(self, user_id:int) -> list[Role]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                iterator = await session.execute(
                        select(Role)
                        .join(
                            User,
                            Role.users
                        )
                        .where(User.id == user_id)
                    )
                return [role[0] for role in iterator.all()]
        except:
            raise ValueError

    async def get_groups(self, user_id:int):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                iterator = await session.execute(
                        select(Group)
                        .join(
                            User,
                            Group.users
                        )
                        .where(User.id == user_id)
                    )
                return [group[0] for group in iterator.all()]
        except:
            raise ValueError

    def __repr__(self) -> str:
        return "User repository"
