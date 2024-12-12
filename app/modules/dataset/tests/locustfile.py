import os
import shutil
from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
import random


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()
        self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234"
        })
        temp_folder = os.path.join("uploads", "temp", "user_1")
        os.makedirs(temp_folder, exist_ok=True)
        source_file = "app/modules/dataset/uvl_examples/file1.uvl"
        dest_file = os.path.join(temp_folder, "file1.uvl")
        shutil.copyfile(source_file, dest_file)

    @task(9)
    def upload_dataset_zenodo(self):
        random_number = random.randint(1000, 9999)
        form_data = {
            "title": f"uploaded zenodo dataset {random_number}",
            "desc": "uploaded zenodo dataset",
            "publication_type": "none",
            "publication_doi": "",
            "dataset_doi": "",
            "tags": "",
            "authors-0-name": "Updated Author Name",
            "authors-0-affiliation": "Updated Author Affiliation",
            "authors-0-orcid": "0000-0001-2345-6789",
            "feature_models-0-uvl_filename": "file1.uvl",
            "feature_models-0-title": "Updated Feature Model Title",
            "feature_models-0-desc": "Updated Feature Model Description",
            "feature_models-0-publication_type": "none",
            "feature_models-0-publication_doi": "",
            "feature_models-0-tags": "",
            "feature_models-0-version": "1.0",
            "feature_models-0-authors-0-name": "Updated FM Author Name",
            "feature_models-0-authors-0-affiliation": "Updated FM Author Affiliation",
            "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
        }
        response = self.client.post("/dataset/upload", data=form_data)
        if response.status_code == 200:
            print("Dataset uploaded to Zenodo successfully")
        else:
            print(f"Failed to upload dataset to Zenodo: {response.status_code}")

    @task(8)
    def upload_dataset_zenodo_from_staging(self):
        random_number = random.randint(1000, 9999)
        form_data = {
            "title": f"uploaded zenodo dataset {random_number}",
            "desc": "uploaded zenodo dataset",
            "publication_type": "none",
            "publication_doi": "",
            "dataset_doi": "",
            "tags": "",
            "authors-0-name": "Updated Author Name",
            "authors-0-affiliation": "Updated Author Affiliation",
            "authors-0-orcid": "0000-0001-2345-6789",
            "feature_models-0-uvl_filename": "file1.uvl",
            "feature_models-0-title": "Updated Feature Model Title",
            "feature_models-0-desc": "Updated Feature Model Description",
            "feature_models-0-publication_type": "none",
            "feature_models-0-publication_doi": "",
            "feature_models-0-tags": "",
            "feature_models-0-version": "1.0",
            "feature_models-0-authors-0-name": "Updated FM Author Name",
            "feature_models-0-authors-0-affiliation": "Updated FM Author Affiliation",
            "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
        }
        response = self.client.post("/dataset/upload/5", data=form_data)
        if response.status_code == 200:
            print("Staging dataset uploaded to zenodo successfully")
        else:
            print(f"Failed to update staging dataset: {response.status_code}")

    @task(7)
    def update_staging_area_dataset(self):
        # Continuar con el update del dataset
        random_number = random.randint(1000, 9999)
        form_data = {
            "title": f"updated staging dataset {random_number}",
            "desc": "updated staging description",
            "publication_type": "none",
            "publication_doi": "",
            "dataset_doi": "",
            "tags": "",
            "authors-0-name": "Updated Author Name",
            "authors-0-affiliation": "Updated Author Affiliation",
            "authors-0-orcid": "0000-0001-2345-6789",
            "feature_models-0-uvl_filename": "file1.uvl",
            "feature_models-0-title": "Updated Feature Model Title",
            "feature_models-0-desc": "Updated Feature Model Description",
            "feature_models-0-publication_type": "none",
            "feature_models-0-publication_doi": "",
            "feature_models-0-tags": "",
            "feature_models-0-version": "1.0",
            "feature_models-0-authors-0-name": "Updated FM Author Name",
            "feature_models-0-authors-0-affiliation": "Updated FM Author Affiliation",
            "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
        }

        response = self.client.post("/dataset/staging-area/5", data=form_data)
        if response.status_code == 200:
            print("Staging dataset updated successfully")
        else:
            print(f"Failed to update staging dataset: {response.status_code}")

    @task(6)
    def get_staging_area_dataset(self):
        response = self.client.get("/dataset/staging-area/5")
        if response.status_code == 200:
            print("Staging dataset retrieved successfully")
        else:
            print(f"Failed to retrieve staging dataset: {response.status_code}")
            return

    @task(5)
    def create_dataset(self):
        form_data = {
            "title": "test dataset",
            "desc": "test description",
            "publication_type": "none",
            "publication_doi": "",
            "dataset_doi": "",
            "tags": "",
            "authors-0-name": "Author Name",
            "authors-0-affiliation": "Author Affiliation",
            "authors-0-orcid": "0000-0001-2345-6789",
            "feature_models-0-uvl_filename": "file1.uvl",
            "feature_models-0-title": "Feature Model Title",
            "feature_models-0-desc": "Feature Model Description",
            "feature_models-0-publication_type": "none",
            "feature_models-0-publication_doi": "",
            "feature_models-0-tags": "",
            "feature_models-0-version": "1.0",
            "feature_models-0-authors-0-name": "FM Author Name",
            "feature_models-0-authors-0-affiliation": "FM Author Affiliation",
            "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
        }

        response = self.client.post("/dataset/create", data=form_data)
        if response.status_code == 200:
            print("Dataset created successfully")
        else:
            print(f"Failed to create dataset: {response.status_code}")

    @task(4)
    def rate_dataset(self):
        """Simula el envío de una calificación a un dataset."""
        dataset_id = random.randint(1, 4)
        rating_value = random.randint(0, 5)
        response = self.client.post(f"/datasets/{dataset_id}/rate", json={"rating": rating_value})

        if response.status_code == 200:
            print(f"Calificación enviada correctamente para dataset {dataset_id} con rating {rating_value}")
        elif response.status_code == 400:
            print(f"Error al enviar calificación: {response.json()}")
        elif response.status_code == 401:
            print("Usuario no autenticado.")

    @task(3)
    def get_dataset_average_rating(self):
        """Simula obtener el promedio de calificaciones de un dataset."""
        dataset_id = random.randint(1, 4)
        response = self.client.get(f"/datasets/{dataset_id}/average-rating")

        if response.status_code == 200:
            average_rating = response.json().get("average_rating")
            print(f"Promedio de calificaciones para dataset {dataset_id}: {average_rating}")
        elif response.status_code == 404:
            print(f"Dataset {dataset_id} no encontrado.")
        else:
            print(f"Error inesperado: {response.status_code}")

    @task(2)
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)

    @task(1)
    def create_empty_dataset(self):
        for i in range(10):
            feature_model_id = i
            self.client.post(f"/dataset/build_empty/{feature_model_id}",)


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
