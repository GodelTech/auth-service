from typing import Callable

from fastapi import Depends

from src.business_logic.dependencies.database import get_repository
from src.business_logic.services.grants import BaseGrantService
from src.data_access.postgresql.repositories import PersistentGrantRepository


def get_grant_service(service_type: BaseGrantService) -> Callable:
    def _get_grant_service(
        persistent_grant_repo: PersistentGrantRepository = Depends(
            get_repository(PersistentGrantRepository)
        ),
    ) -> BaseGrantService:
        return service_type(persistent_grant_repo=persistent_grant_repo)

    return _get_grant_service
