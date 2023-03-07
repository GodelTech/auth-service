from datetime import datetime

from sqlalchemy import select, exists, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from .client import Client
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.device import Device
from src.data_access.postgresql.errors import UserCodeNotFoundError, DeviceCodeNotFoundError


class DeviceRepository(BaseRepository):

    async def create(
        self,
        client_id: str,
        device_code: str,
        user_code: str,
        verification_uri: str,
        verification_uri_complete: str,
        expires_in: int = 600,
        interval: int = 5,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            client_id_int = await self.get_client_id_int(client_id=client_id, session=session)
            device_data = {
                "client_id": client_id_int,
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": verification_uri,
                "verification_uri_complete": verification_uri_complete,
                "expires_in": expires_in,
                "interval": interval,
            }
            await session.execute(
                insert(Device).values(**device_data)
            )
            await session.commit()

    async def delete_by_user_code(self, user_code: str) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.validate_user_code(user_code=user_code):
                await session.execute(
                    delete(Device).where(Device.user_code == user_code)
                )
                await session.commit()

    async def delete_by_device_code(self, device_code: str) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.validate_device_code(device_code=device_code):
                await session.execute(
                    delete(Device).where(Device.device_code == device_code)
                )
                await session.commit()

    async def validate_user_code(self, user_code: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(
                    exists().where(Device.user_code == user_code))
                )
            result = result.first()
            if not result[0]:
                raise UserCodeNotFoundError('Wrong User Code')

            return result[0]

    async def validate_device_code(self, device_code: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(
                    exists().where(Device.device_code == device_code))
                )
            result = result.first()
            # if not result[0]:
            #     raise DeviceCodeNotFoundError('Wrong Device Code')

            return result[0]

    async def get_device_by_user_code(self, user_code: str) -> Device:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.validate_user_code(user_code=user_code):
                device = await session.execute(
                    select(Device).join(Client, Device.client_id == Client.id).where(Device.user_code == user_code)
                )
                return device.first()[0]
            else:
                raise UserCodeNotFoundError

    async def get_expiration_time(self, device_code: str) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            device = await session.execute(
                select(Device).where(Device.device_code == device_code)
            )
            device = device.first()[0]
            created_at = device.created_at
            expires_in = device.expires_in
            time = datetime.timestamp(created_at) + expires_in

            return time

    async def get_client_id_int(self, client_id:str, session: AsyncSession) -> int:
        client_id_int = await session.execute(select(Client)
                .where(
                    Client.client_id == client_id,
                ))
        client_id_int= client_id_int.first()

        if client_id_int is None:
            raise ValueError
        else:
            return client_id_int[0].id