# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestTestDelete():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_testDelete(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(945, 940)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
        deleted_item = self.driver.find_element(By.CSS_SELECTOR, ".col:nth-child(1) .card-title").text
        self.driver.find_element(By.CSS_SELECTOR, ".col:nth-child(1) .card-img-top").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-danger").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
        items = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{deleted_item}')]")
        assert len(items) == 0, f"El elemento '{deleted_item}' no se eliminó correctamente"