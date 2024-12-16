from selenium import webdriver
from selenium.webdriver.common.by import By


class TestFmrate():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_fmrate(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1702, 963)
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        self.driver.find_element(By.CSS_SELECTOR, "#star-rating-feature-10 > span:nth-child(3)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".list-group-item:nth-child(2) div:nth-child(5) > button").click()
