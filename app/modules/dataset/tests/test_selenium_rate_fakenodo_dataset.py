import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestTestpruebaseleniumratedataset():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_testpruebaseleniumratedataset(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(1702, 963)
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(11) .align-middle:nth-child(2)").click()
        self.driver.execute_script("document.body.style.zoom='50%'")
        self.driver.find_element(By.LINK_TEXT, "Staging area dataset").click()
        self.driver.execute_script("document.body.style.zoom='50%'")
        time.sleep(1)
        self.driver.find_element(By.ID, "upload_fakenodo_button").click()
        time.sleep(1)
        self.driver.find_element(By.LINK_TEXT, "Staging area dataset").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(3)").click()
        self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > button").click()
