# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestTestCreate():

    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_testCreate(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(945, 940)
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(6) .align-middle:nth-child(2)").click()
        self.driver.find_element(By.LINK_TEXT, "Create Community").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.LINK_TEXT, "All Communities").click()
        self.driver.find_element(By.LINK_TEXT, "Create Community").click()
        self.driver.find_element(By.ID, "submit").click()
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".community-item")
        assert len(elements) == 0, "Se creó una comunidad inesperadamente"
