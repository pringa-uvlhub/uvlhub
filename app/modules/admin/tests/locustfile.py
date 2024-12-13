from locust import HttpUser, TaskSet, task, between
from core.environment.host import get_host_for_locust_testing

class AdminTestSuite(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234",
            "is_admin": True
        })

    @task(1)
    def load_dashboard_no_data(self):
        response = self.client.get("/no_data")
        if response.status_code == 200 or 302:
            print("Dashboard no data loaded successfully")
        else:
            print(f"Dashboard no data failed: {response.status_code}")


class AdminBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        response = self.client.get("/admin")

        if response.status_code != 200:
            print(f"Admin index failed: {response.status_code}")


class AdminUser(HttpUser):
    tasks = [AdminBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
