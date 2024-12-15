import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import os


class TestCreateds:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_createds(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1854, 1048)

        # Procede con la prueba de login
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(10) .align-middle:nth-child(2)").click()
        self.driver.find_element(By.ID, "title").click()
        self.driver.find_element(By.ID, "title").send_keys("test")
        self.driver.find_element(By.ID, "desc").click()
        self.driver.find_element(By.ID, "desc").send_keys("test")
        self.driver.find_element(By.CSS_SELECTOR, ".col-xl-6:nth-child(2)").click()
        self.driver.find_element(By.ID, "myDropzone").click()

        # Subir el archivo file1.uvl
        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file_input.send_keys(file_path)
        self.driver.execute_script("document.body.style.zoom='50%'")
        # Esperar a que el archivo se cargue completamente
        time.sleep(0.5)
        self.driver.find_element(By.ID, "create_button").click()
        time.sleep(0.5)
        # Verificar que estamos en la sección "Staging Area" de "Unprepared Datasets"
        # Comprobar si el título de la sección 'Staging Area' está visible
        self.driver.execute_script("document.body.style.zoom='50%'")
        staging_area_title = self.driver.find_element(By.XPATH, "//h5[contains(text(),'Staging Area')]")
        assert staging_area_title.is_displayed(), "La sección 'Staging Area' no está visible"

        # Verificar si hay filas en la tabla de "Unprepared Datasets"
        rows = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'card-body')]//table/tbody/tr")
        assert len(rows) > 0, "No hay datasets no preparados en la sección 'Staging Area'"
