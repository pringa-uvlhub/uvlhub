from selenium.webdriver.common.by import By
from core.selenium.common import initialize_driver


class TestExplorePage():
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_explore_page(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1048)
        self.driver.find_element(By.CSS_SELECTOR, ".hamburger").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(3) .align-middle:nth-child(2)").click()
