# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from core.environment.host import get_host_for_selenium_testing

host = get_host_for_selenium_testing()

class Testcreatedataset():
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_testcreatedataset(self):
    self.driver.get(f"{host}")
    self.driver.set_window_size(1854, 1048)
    self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.ID, "title").click()
    self.driver.find_element(By.ID, "title").click()
    self.driver.find_element(By.ID, "title").click()
    element = self.driver.find_element(By.ID, "title")
    actions = ActionChains(self.driver)
    actions.double_click(element).perform()
    self.driver.find_element(By.ID, "title").send_keys("test_dataset")
    self.driver.find_element(By.ID, "desc").click()
    self.driver.find_element(By.ID, "desc").send_keys("test_dataset description")
    self.driver.find_element(By.ID, "myDropzone").click()
    self.driver.find_element(By.LINK_TEXT, "Log out").click()
  
