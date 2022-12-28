from fastapi import Depends
from typing import Callable

from src.data_access.postgresql.repositories import PersistentGrantRepository
from src.business_logic.services.grants import BaseGrantService
from src.business_logic.dependencies.database import get_repository


def get_grant_service(service_type: BaseGrantService) -> Callable:
    def _get_grant_service(
        persistent_grant_repo: PersistentGrantRepository = Depends(get_repository(PersistentGrantRepository))
    ):
        return service_type(
                persistent_grant_repo=persistent_grant_repo
            )
    return _get_grant_service
