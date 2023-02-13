from dataclasses import dataclass

from fastapi import Form


@dataclass
class DeviceRequestModel:
    client_id: str = Form(...)
    scope: str = Form(None)


@dataclass
class DeviceUserCodeModel:
    user_code: str = Form(...)


@dataclass
class DeviceCancelModel:
    client_id: str = Form(...)
    scope: str = Form(...)
