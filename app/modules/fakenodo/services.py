import os
from app.modules.fakenodo.repositories import FakenodoRepository
from core.services.BaseService import BaseService


class FakenodoService(BaseService):
    def get_fakenodo_access_token(self):
        return os.getenv("ZENODO_ACCESS_TOKEN")
    
    def __init__(self):
        super().__init__(FakenodoRepository())
        self.FAKENODO_ACCESS_TOKEN = self.get_fakenodo_access_token()
        # self.FAKENODO_API_URL = self.get_zenodo_url()
        self.headers = {"Content-Type": "application/json"}
        self.params = {"access_token": self.FAKENODO_ACCESS_TOKEN}