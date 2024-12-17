# Generated by Selenium IDE
import time
from selenium.webdriver.common.by import By
from core.selenium.common import initialize_driver


class TestViewProfile3():
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_viewprofile3(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1862, 1048)
        time.sleep(2)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        time.sleep(2)
        self.driver.get("http://localhost:5000/profile/300")
        time.sleep(2)
        self.driver.find_element(By.LINK_TEXT, "Back to home").click()
        time.sleep(2)
