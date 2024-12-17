import os
import secrets
import shutil
from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class FeaturemodelBehavior(TaskSet):
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

    @task
    def index(self):
        response = self.client.get("/featuremodel")

        if response.status_code != 200:
            print(f"Featuremodel index failed: {response.status_code}")

    @task(3)
    def rate_featuremodel(self):
        """Simula el envío de una calificación a un feature model."""
        featuremodel_id = secrets.randbelow(11) + 1
        rating_value = secrets.randbelow(6)
        response = self.client.post(f"/feature-models/{featuremodel_id}/rate", json={"rating": rating_value})

        if response.status_code == 200:
            print(f"Calificación enviada correctamente para dataset {featuremodel_id} con rating {rating_value}")
        elif response.status_code == 400:
            print(f"Error al enviar calificación: {response.json()}")
        elif response.status_code == 401:
            print("Usuario no autenticado.")

    @task(2)
    def get_dataset_average_rating(self):
        """Simula obtener el promedio de calificaciones de un feature model."""
        featuremodel_id = secrets.randbelow(11) + 1
        response = self.client.get(f"/feature-models/{featuremodel_id}/average-rating")

        if response.status_code == 200:
            average_rating = response.json().get("average_rating")
            print(f"Promedio de calificaciones para dataset {featuremodel_id}: {average_rating}")
        elif response.status_code == 404:
            print(f"Dataset {featuremodel_id} no encontrado.")
        else:
            print(f"Error inesperado: {response.status_code}")

    @task(1)
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)


class FeaturemodelUser(HttpUser):
    tasks = [FeaturemodelBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
