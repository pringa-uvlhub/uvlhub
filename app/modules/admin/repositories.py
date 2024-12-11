from app.modules.admin.models import Admin
from core.repositories.BaseRepository import BaseRepository


class AdminRepository(BaseRepository):
    def __init__(self):
        super().__init__(Admin)
