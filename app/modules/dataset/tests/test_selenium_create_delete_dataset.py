from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time


class TestDelete:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_delete(self):
        # Navegar a la página inicial
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1854, 1048)

        # Iniciar sesión
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(10) .align-middle:nth-child(2)").click()

        # Subir un nuevo dataset
        self.driver.find_element(By.ID, "title").click()
        self.driver.find_element(By.ID, "title").send_keys("test_delete")
        self.driver.find_element(By.ID, "desc").click()
        self.driver.find_element(By.ID, "desc").send_keys("test_delete")
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

        # Navegar a la lista de datasets
        self.driver.find_element(By.CSS_SELECTOR, ".hamburger").click()
        self.driver.find_element(By.LINK_TEXT, "My datasets").click()
        self.driver.find_element(By.LINK_TEXT, "test_delete").click()

        # Borrar el dataset
        self.driver.execute_script("document.body.style.zoom='50%'")
        self.driver.find_element(By.ID, "delete_button").click()

        # Esperar a que se elimine el dataset
        time.sleep(1)

        # Comprobar que el dataset "test_delete" ya no está en el listado
        dataset_titles = self.driver.find_elements(By.XPATH, "//table//tbody//tr//td//a")
        dataset_titles_text = [title.text for title in dataset_titles]

        # Verificar que el título 'test_delete' ya no aparece en la lista de datasets
        assert "test_delete" not in dataset_titles_text, "El dataset 'test_delete' sigue apareciendo en el listado"
