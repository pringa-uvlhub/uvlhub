from app.modules.fakenodo.repositories import FakenodoRepository
from core.services.BaseService import BaseService

from app.modules.dataset.models import DataSet
import random


class FakenodoService(BaseService):
    def __init__(self):
        super().__init__(FakenodoRepository())

    def create_new_deposition(self, dataset: DataSet) -> dict:
        """
        Create a new deposition in Fakenodo.

        Args:
            dataset (DataSet): The DataSet object containing the metadata of the deposition.

        Returns:
            dict: A dictionary containing the doi and a status code 201.
        """

        random_numbers1 = ''.join([str(random.randint(0, 9)) for _ in range(2)])
        random_numbers2 = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        fakenodo_doi = f"{random_numbers1}.{random_numbers2}/{dataset.ds_meta_data.title}"
        # Construir el diccionario de respuesta
        response = {
            "fakenodo_doi": fakenodo_doi,
            "status_code": 201
        }

        return response
