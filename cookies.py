import pathlib, pickle
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

SELENIUM_PORT = 9222

s = Service('C:\Selenium-Evidian-main\selenium\chromedriver.exe')
options = Options()
options.add_argument('user-data-dir')
driver = webdriver.Chrome(service=s)
driver.get("htpps://www.google.com")
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

driver.quit()
