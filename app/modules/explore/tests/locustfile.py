from locust import HttpUser, task, between


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def load_explore_page(self):
        print("Cargando la página de búsqueda...")
        response = self.client.get("/explore")
        if response.status_code == 200:
            print("Página de búsqueda cargada correctamente.")
        else:
            print(f"Error al cargar la página de búsqueda: {response.status_code}")
