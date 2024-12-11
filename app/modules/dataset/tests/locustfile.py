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
