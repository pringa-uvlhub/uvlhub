# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class TestGrantAdmin():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_grantadmin(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1048)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user2@example.com")
        self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(3) > .col-md-6").click()
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.LINK_TEXT, "My Created Communities").click()
        self.driver.find_element(By.CSS_SELECTOR, ".col:nth-child(3) .card-img-top").click()
        self.driver.find_element(By.LINK_TEXT, "View Members").click()
        time.sleep(0.2)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-warning").click()