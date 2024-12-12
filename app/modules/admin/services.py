from app.modules.admin.repositories import AdminRepository
from core.services.BaseService import BaseService


class AdminService(BaseService):
    def __init__(self):
        super().__init__(AdminRepository())
