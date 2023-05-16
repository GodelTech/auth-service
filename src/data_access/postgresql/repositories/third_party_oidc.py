from typing import List, Optional, Tuple

from sqlalchemy import delete, exists, insert, select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.identity_resource import (
    IdentityProvider,
    IdentityProviderMapped,
    IdentityProviderState,
)


class ThirdPartyOIDCRepository(BaseRepository):
    async def get_row_providers_data(
        self,
    ) -> List[Tuple[str, str, str, str, str, str]]:
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

    async def create_state(self, state: str) -> None:
        if not await self.validate_state(state=state):
            await self.session.execute(
                insert(IdentityProviderState).values(
                    state=state,
                )
            )
            await self.session.commit()

    async def delete_state(self, state: str) -> None:
        if await self.validate_state(state=state):
            await self.session.execute(
                delete(IdentityProviderState).where(
                    IdentityProviderState.state == state,
                )
            )
            await self.session.commit()

    async def get_external_links_by_provider_name(
        self, name: str
    ) -> tuple[str, str]:
        result = await self.session.execute(
            select(
                IdentityProvider.token_endpoint_link,
                IdentityProvider.userinfo_link,
            ).where(IdentityProvider.name == name)
        )
        row = result.fetchone()
        return row.token_endpoint_link, row.userinfo_link

    async def is_state(self, state: str) -> bool:
        result = await self.session.execute(
            select(IdentityProviderState.state)
            .where(IdentityProviderState.state == state)
            .exists()
            .select()
        )
        return result.scalar()

    async def get_credentials_by_provider_name(
        self, name: str
    ) -> Tuple[str, str, str]:
        result = await self.session.execute(
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
        row = result.fetchone()
        return (
            row.provider_client_id,
            row.provider_client_secret,
            row.internal_redirect_uri,
        )

    async def get_id_by_provider_name(self, name: str) -> Optional[int]:
        result = await self.session.execute(
            select(
                IdentityProvider.id,
            ).where(
                IdentityProvider.name == name,
            )
        )
        return result.scalar()

    async def get_provider_id_by_name(  # TODO depracated - delete it after whole refactoring
        self, name: str
    ) -> Optional[int]:
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

    async def get_provider_external_links(  # TODO depracated - delete it after whole refactoring
        self, name: str
    ) -> Optional[Tuple[str, str]]:
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

    async def get_row_provider_credentials_by_name(  # TODO depracated - delete it after whole refactoring
        self, name: str
    ) -> Optional[Tuple[str, str, str]]:
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

    async def validate_state(  # TODO replace it's all calls with refactored version - is_state
        self, state: str
    ) -> bool:
        state_checked = await self.session.execute(
            select(
                exists().where(
                    IdentityProviderState.state == state,
                )
            )
        )
        state_bool = state_checked.first()
        return state_bool[0]
