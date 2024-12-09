from selenium import webdriver
from selenium.webdriver.common.by import By


class TestRatedataset:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_ratedataset(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1854, 1048)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        self.driver.find_element(By.CSS_SELECTOR, "#star-rating-12 > span:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > button").click()

        # Verificar éxito
        assert "Rating added" in self.driver.page_source, "El mensaje de calificación no apareció."
