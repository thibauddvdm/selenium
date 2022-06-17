import requests
import time

from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from fonctions_selenium import *

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver=webdriver.Firefox(executable_path="C:\Projet Python\selenium\geckodriver.exe", options=options)

driver.get("https://www.aleth.cloud")
driver.maximize_window()
driver.find_element_by_id("ok").click()

time.sleep(2)

window_main = driver.window_handles[0]
barre_login=driver.find_element_by_xpath("/html/body/app/div[1]/div[1]/div[2]/label/input")
barre_login.send_keys("sanctuaire.adminrun")            #barre_login.send_keys("support.sanctuaire")

time.sleep(1)

barre_login.send_keys(Keys.ENTER)

time.sleep(2)

driver.find_element_by_xpath("/html/body/app/div[1]/div[1]/div[4]/button/span").click()
time.sleep(15)

######################## TEST GMAIL ########################
driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[1]/div/div[4]/a").click()

window_gmail = driver.window_handles[1]
driver.switch_to.window(window_gmail)

time.sleep(2)
gmail_est_ok=verifierSite(driver)
fermer_onglet(driver)

######################### TEST BOX #########################
driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[2]/div/div[4]/a").click()

window_box = driver.window_handles[1]
driver.switch_to.window(window_box)

time.sleep(2)
box_est_ok=verifierSite(driver)
fermer_onglet(driver)

################### TEST REQUEST MANAGER ###################
driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[3]/div/div[4]/a").click()

window_rm = driver.window_handles[1]
driver.switch_to.window(window_rm)

time.sleep(2)
rm_est_ok=verifierSite(driver)
fermer_onglet(driver)

aleth_est_ok(gmail_est_ok,box_est_ok,rm_est_ok)

driver.quit()