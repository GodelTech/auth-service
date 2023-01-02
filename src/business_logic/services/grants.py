import logging

from src.data_access.postgresql.repositories import PersistentGrantRepository

logger = logging.getLogger('is_app')

class BaseGrantService:
    def __init__(
        self,
        persistent_grant_repo: PersistentGrantRepository
    ) -> None:
        self.persistent_grant_repo = persistent_grant_repo

    def exists(self):
        logger.info(self.grant_type, self.data)
        return True


class AuthorizationCodeGrantService(BaseGrantService):
    pass
