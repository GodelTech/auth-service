import logging

from src.business_logic.dependencies.database import get_repository_no_depends
from src.data_access.postgresql.repositories import PersistentGrantRepository

logger = logging.getLogger(__name__)


class BaseGrantService:
    def __init__(
        self, persistent_grant_repo: PersistentGrantRepository
    ) -> None:
        self.persistent_grant_repo = persistent_grant_repo

    def exists(self) -> bool:
        # logger.info(self.grant_type, self.data)
        return True


class AuthorizationCodeGrantService(BaseGrantService):
    pass
