from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol


class DeviceAuthService:
    ...
