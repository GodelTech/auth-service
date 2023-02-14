from sqladmin import ModelView
from src.data_access.postgresql.tables.device import Device


class DeviceAdminController(ModelView, model=Device):
    icon = "fa-solid fa-display"
    column_list = [
        Device.client_id, 
        Device.device_code, 
        Device.user_code,]

