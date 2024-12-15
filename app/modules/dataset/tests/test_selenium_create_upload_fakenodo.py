import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import os


class TestUploadzenodo():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_uploadzenodo(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1854, 1048)
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
        self.driver.find_element(By.ID, "title").send_keys("test_ds_upload_fakenodo")
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
        time.sleep(2)  # Ajusta el tiempo de espera según sea necesario
        # Continuar con el resto del test si es necesario
        self.driver.find_element(By.ID, "create_button").click()
        time.sleep(1)

        # Navegar a la lista de datasets
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.LINK_TEXT, "My datasets").click()
        self.driver.execute_script("document.body.style.zoom='50%'")
        self.driver.find_element(By.LINK_TEXT, "test_ds_upload_fakenodo").click()
        self.driver.execute_script("document.body.style.zoom='50%'")
        # Hacer clic en el botón para subir a FakeNode
        self.driver.find_element(By.CSS_SELECTOR, "#upload_fakenodo_button > .feather").click()
        time.sleep(1)  # Esperar un momento para que el proceso de subida se complete

        # Obtener los títulos de los datasets en FakeNode Datasets
        dataset_titles = self.driver.find_elements(By.XPATH, "//table//tbody//tr//td//a")
        dataset_titles_text = [title.text for title in dataset_titles]

        # Verificar que el dataset 'test_ds_upload_fakenodo' está en la lista
        assert "test_ds_upload_fakenodo" in dataset_titles_text,  \
            "El dataset no se encuentra en la sección de FakeNode Datasets"
