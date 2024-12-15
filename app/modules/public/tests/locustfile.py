from locust import HttpUser, task, between


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def load_main_page(self):
        print("Cargando la página principal...")
        response = self.client.get("/")
        if response.status_code == 200:
            print("Página principal cargada correctamente.")
        else:
            print(f"Error al cargar la página principal: {response.status_code}")
