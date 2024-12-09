from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()
        self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234"
        })

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

