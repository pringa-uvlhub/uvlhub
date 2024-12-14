from locust import HttpUser, task, between


class AdminTestSuite(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        response = self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234",
            "is_admin": True
        })
        if response.status_code == 200:
            print("Admin login successful")
        else:
            print(f"Admin login failed: {response.status_code}")

    @task(1)
    def load_dashboard_no_data(self):
        response = self.client.get("/no_data")
        if response.status_code == 200 or 302:
            print("Dashboard no data loaded successfully")
        else:
            print(f"Dashboard no data failed: {response.status_code}")
