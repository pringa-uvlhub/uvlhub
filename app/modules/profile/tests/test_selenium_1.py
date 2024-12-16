# Generated by Selenium IDE
import time
from selenium.webdriver.common.by import By
from core.selenium.common import initialize_driver


class TestViewprofile1():
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_viewprofile1(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1862, 1048)
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        time.sleep(2)
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        time.sleep(2)
        self.driver.find_element(By.LINK_TEXT, "Doe, Jane").click()
        time.sleep(2)
        self.driver.find_element(By.LINK_TEXT, "Doe, John").click()
        self.driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(2)").click()
