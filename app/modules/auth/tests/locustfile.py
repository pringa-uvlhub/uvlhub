from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token, fake
from core.environment.host import get_host_for_locust_testing


class SignupBehavior(TaskSet):
    def on_start(self):
        self.signup()

    @task
    def signup(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/signup", data={
            "email": fake.email(),
            "password": fake.password(),
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")
        else:
            # Simular que el correo electrónico ha sido enviado y se genera un enlace de confirmación
            confirmation_token = self.extract_confirmation_token(response)
            if confirmation_token:
                self.confirm_email(confirmation_token)

    def extract_confirmation_token(self, response):
        # Aquí se debe extraer el token de confirmación del correo desde la respuesta del servidor.
        token = None
        if "confirmation_link" in response.text:
            # Suponiendo que el enlace de confirmación contiene el token
            token = response.text.split("confirmation_link=")[1].split('"')[0]
        return token

    def confirm_email(self, token):
        # Simula hacer una solicitud para confirmar el correo electrónico
        confirmation_url = f"/confirm_email?token={token}"
        response = self.client.get(confirmation_url)
        if response.status_code == 200 and "Email confirmed" in response.text:
            print("Email successfully confirmed!")
        else:
            print(f"Email confirmation failed: {response.status_code}")


class LoginBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login()

    @task
    def ensure_logged_out(self):
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task
    def login(self):
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": 'user1@example.com',
            "password": '1234',
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class AuthUser(HttpUser):
    tasks = [SignupBehavior, LoginBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
