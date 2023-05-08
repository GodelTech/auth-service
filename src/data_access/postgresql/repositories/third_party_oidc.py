from typing import List, Optional, Tuple

from sqlalchemy import delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.third_party_oidc import (
    ThirdPartyStateDuplicationError,
    ThirdPartyStateNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.identity_resource import (
    IdentityProvider,
    IdentityProviderMapped,
    IdentityProviderState,
)


class ThirdPartyOIDCRepository():

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_row_providers_data(
        self,
    ) -> List[Tuple[str, str, str, str, str, str]]:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        providers = await self.session.execute(
            select(
                IdentityProvider.name,
                IdentityProvider.auth_endpoint_link,
                IdentityProviderMapped.provider_client_id,
                IdentityProvider.internal_redirect_uri,
                IdentityProviderMapped.provider_client_secret,
                IdentityProvider.provider_icon,
            )
            .join(IdentityProvider)
            .where(
                IdentityProviderMapped.enabled == True,
            )
        )
        providers_list = providers.fetchall()
        return providers_list

    async def get_row_provider_credentials_by_name(
        self, name: str
    ) -> Optional[Tuple[str, str, str]]:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        provider_data = await self.session.execute(
            select(
                IdentityProviderMapped.provider_client_id,
                IdentityProviderMapped.provider_client_secret,
                IdentityProvider.internal_redirect_uri,
            )
            .join(IdentityProvider)
            .where(
                IdentityProvider.name == name,
            )
        )
        providers_list = provider_data.fetchall()
        if providers_list:
            return providers_list[0]
        else:
            return None

    async def create_state(self, state: str) -> None:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        if not await self.validate_state(state=state):
            await self.session.execute(
                insert(IdentityProviderState).values(
                    state=state,
                )
            )
            await self.session.commit()
        else:  # TODO ?
            raise ThirdPartyStateDuplicationError(
                "State you are trying to delete for does not exist"
            )

    async def delete_state(self, state: str) -> None:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        if await self.validate_state(state=state):
            await self.session.execute(
                delete(IdentityProviderState).where(
                    IdentityProviderState.state == state,
                )
            )
            await self.session.commit()
        else:
            raise ThirdPartyStateNotFoundError(
                "State you are trying to delete for does not exist"
            )

    async def validate_state(self, state: str) -> bool:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        state_checked = await self.session.execute(
            select(
                exists().where(
                    IdentityProviderState.state == state,
                )
            )
        )
        state_bool = state_checked.first()
        return state_bool[0]

    async def get_provider_external_links(
        self, name: str
    ) -> Optional[Tuple[str, str]]:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        provider_external_links = await self.session.execute(
            select(
                IdentityProvider.token_endpoint_link,
                IdentityProvider.userinfo_link,
            ).where(
                IdentityProvider.name == name,
            )
        )
        link_list = provider_external_links.fetchall()
        if link_list:
            return link_list[0]
        else:
            return None

    async def get_provider_id_by_name(self, name: str) -> Optional[int]:
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
        provider_id = await self.session.execute(
            select(
                IdentityProvider.id,
            ).where(
                IdentityProvider.name == name,
            )
        )
        link_list = provider_id.fetchall()
        if link_list:
            return link_list[0][0]
        else:
            return None
