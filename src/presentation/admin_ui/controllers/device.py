from sqladmin import ModelView
from src.data_access.postgresql.tables.device import Device


class DeviceAdminController(ModelView, model=Device):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        Device.device_code, 
        Device.user_code,
        ]

