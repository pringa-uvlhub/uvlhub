# from selenium.common.exceptions import NoSuchElementException
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
# from core.environment.host import get_host_for_selenium_testing
# from core.selenium.common import initialize_driver, close_driver


class TestAdminDownloads:
    def setup_method(self, method):
        download_directory = os.path.abspath("test")  # Carpeta donde se guardarán las descargas
        chrome_options = Options()
        prefs = {
            "download.default_directory": download_directory,  # Ruta donde se guardarán los archivos
            "download.prompt_for_download": False,  # Evita el cuadro de diálogo de descarga
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True  # Evita problemas de seguridad al descargar
        }
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_argument("--disable-notifications")  # Deshabilitar las notificaciones del navegador
        chrome_options.add_argument("--disable-extensions")  # Deshabilitar las extensiones de Chrome
        self.driver = webdriver.Chrome(options=chrome_options)  # Iniciar sesión como usuario
        self.driver.implicitly_wait(5)
        self.vars = {}
        print(f"Setting up for {method.__name__}")

    def teardown_method(self, method):
        self.driver.quit()
        print(f"Tearing down after {method.__name__}")

    def test_admin_downloads(self):
        self.driver.get("http://localhost:5000/")

        # Iniciar sesión como admnistrador
        self.driver.set_window_size(1702, 963)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("admin1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()

        try:
            # Intentar detectar la alerta, si está presente
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())  # Espera hasta que la alerta aparezca

            # Simular la tecla Esc para cerrarla
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            print("Alerta cerrada con ESC.")
        except TimeoutException:
            print("No se encontró la alerta.")

        # Realiza clic en el botón de descarga
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dataset/download/3"]').click()

        # Espera para asegurar que el archivo se descargue
        time.sleep(3)

        # Realiza clic en el botón de descarga
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dataset/download/4"]').click()

        # Espera para asegurar que el archivo se descargue
        time.sleep(3)

        # Realiza clic en el botón de descarga
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dataset/download/2"]').click()

        # Espera para asegurar que el archivo se descargue
        time.sleep(3)

        self.driver.find_element(By.XPATH, '//a[@href="http://localhost:5000/doi/10.1234/dataset3"]').click()
        self.driver.find_element(By.ID, "btnGroupDropExport7").click()
        self.driver.find_element(By.LINK_TEXT, "UVL").click()
        self.driver.find_element(By.ID, "btnGroupDropExport8").click()
        self.driver.find_element(By.LINK_TEXT, "UVL").click()

        time.sleep(2)

        self.driver.find_element(By.CSS_SELECTOR, "a.sidebar-toggle.js-sidebar-toggle").click()
        self.driver.find_element(By.CSS_SELECTOR, "a.sidebar-link[href='/dashboard']").click()
        time.sleep(3)
        self.driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(5)
        current_url = self.driver.current_url
        assert current_url.endswith("/dashboard"), f"Error: URL actual {current_url} no es la esperada '/dashboard'."
        print("Se verificó correctamente que estás en la página /dashboard.")

        time.sleep(2)
        self.driver.execute_script("window.scrollBy(0, -800);")

        # Cerrar sesión
        time.sleep(2)
        dropdown_toggle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nav-link.dropdown-toggle"))
        )
        dropdown_toggle.click()

        option_to_click = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log out"))  # Cambia "Logout" por la opción que necesitas
        )
        option_to_click.click()

        time.sleep(10)

        self.driver.set_window_size(1702, 963)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()

        try:
            # Intentar detectar la alerta, si está presente
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())  # Espera hasta que la alerta aparezca

            # Simular la tecla Esc para cerrarla
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            print("Alerta cerrada con ESC.")
        except TimeoutException:
            print("No se encontró la alerta.")

        # Realiza clic en el botón de descarga
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dataset/download/3"]').click()

        # Espera para asegurar que el archivo se descargue
        time.sleep(3)

        # Realiza clic en el botón de descarga
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dataset/download/4"]').click()

        # Espera para asegurar que el archivo se descargue
        time.sleep(3)

        self.driver.find_element(By.XPATH, '//a[@href="http://localhost:5000/doi/10.1234/dataset3"]').click()
        self.driver.find_element(By.ID, "btnGroupDropExport7").click()
        self.driver.find_element(By.LINK_TEXT, "UVL").click()

        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, "a.sidebar-toggle.js-sidebar-toggle").click()
        self.driver.find_element(By.CSS_SELECTOR, "a.sidebar-link[href='/']").click()

        time.sleep(2)
        self.driver.find_element(By.XPATH, '//a[@href="http://localhost:5000/doi/10.1234/dataset4"]').click()
        self.driver.find_element(By.ID, "btnGroupDropExport10").click()
        self.driver.find_element(By.LINK_TEXT, "UVL").click()

        # Cerrar sesión
        time.sleep(2)
        dropdown_toggle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nav-link.dropdown-toggle"))
        )
        dropdown_toggle.click()

        option_to_click = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log out"))  # Cambia "Logout" por la opción que necesitas
        )
        option_to_click.click()

        time.sleep(2)

        # Iniciar sesión como admnistrador
        self.driver.set_window_size(1702, 963)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("admin1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()

        self.driver.find_element(By.CSS_SELECTOR, "a.sidebar-toggle.js-sidebar-toggle").click()
        self.driver.find_element(By.CSS_SELECTOR, "a.sidebar-link[href='/dashboard']").click()
        time.sleep(3)
        self.driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(5)
        current_url = self.driver.current_url
        assert current_url.endswith("/dashboard"), f"Error: URL actual {current_url} no es la esperada '/dashboard'."
        print("Se verificó correctamente que estás en la página /dashboard.")

        time.sleep(2)
        self.driver.execute_script("window.scrollBy(0, -800);")
