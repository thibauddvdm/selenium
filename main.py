#Pour compiler: faire :
#pip3 install selenium
#pip3 install requests

import os
from fonctions_selenium import *
from cookies import *

#PARAMETRES
#Variable du driver
driver=webdriver.Chrome(executable_path="C:\Selenium-Evidian-main\selenium\chromedriver.exe")


#FIN PARAMETRES

#Aller sur le site de Sanctuaire
driver.get("https://www.aleth.cloud")

#On aggrandit la page parce que j'ai pas mes lunettes
driver.maximize_window()

#On se retrouve sur "Access Aleth", il faut recupérer le bouton "Entrer"
bouton_entrer=driver.find_element_by_id("ok")

#Il faut cliquer sur le bouton entrer
bouton_entrer.click()
#On attend un peu pour que la page se génére
time.sleep(2)

#On défini cet onglet comme le principal
window_main = driver.window_handles[0]

#La page demandant le login est affiché, on va chercher la barre de saisie de texte
barre_login=driver.find_element_by_id("mat-input-0")


#On remplit le champ de texte
barre_login.send_keys("sanctuaire.adminrun")
#barre_login.send_keys("support.sanctuaire")
time.sleep(1)

#le bouton "login" pour valider la saisie
barre_login.send_keys(Keys.ENTER)

#Intégrer ici une façon d'automatiser Double Octopus de manière sécurisé - Pense aux Filtrage d'IP mon gamin
time.sleep(15)

"""
element_continue_gmail=driver.find_element_by_tag_name("body")
frame_x = element_continue_gmail.location['x']
frame_y = element_continue_gmail.location['y']
action_continue_gmail= ActionChains(driver).move_to_element(element_continue_gmail).move_by_offset(frame_x-800, frame_y)

action_continue_gmail.context_click(element_continue_gmail)
action_continue_gmail.perform()

input("Press enter to start operations...")

"""
################## TEST GMAIL ########################

#Bouton d'accès à Gmail par SSO
#driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[1]/div/div[4]/a").click()

#time.sleep(10)

if os.path.exists('cookies.pkl'):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[1]/div/div[4]/a").click()
    time.sleep(5)

input("Wait...")
    
#On défini cette fenêtre comme la nouvelle fenêtre principal et on switch avec celui ci afin qu'il soit considéré comme la current window
#Cela permet aussi par la suite de pouvoir prendre un screenshot de la current window qui ici est défini comme la fenêtre gmail
#Sans ces 2 lignes la current window restais la page d'accueil Aleth ce qui rendais impossible les screenshot
window_gmail = driver.window_handles[1]
driver.switch_to.window(window_gmail)

time.sleep(10)



#On va essayer d' outrepasser la sécurité pour vérifier que ce n'est pas un bot :p 
#bouton_continue_gmail=driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button/span")
#On peut constater que le XPATH est un random qui change à chaque tentative, il est donc impossible d'utiliser un chemin vers l'element. Pas grave, on peut utiliser les coordonnées

#element_continue_gmail=driver.find_element_by_name('English (United States)')
#frame_x = element_continue_gmail.location['x']
#frame_y = element_continue_gmail.location['y']
#action_continue_gmail= ActionChains(driver).move_to_element(element_continue_gmail).move_by_offset(frame_x, frame_y)
#action_continue_gmail.context_click(element_continue_gmail)
#action_continue_gmail.perform()

#En fait non j'y arrive pas non plus, mais il y'a moyen


#Si Constat que ça marche bien
#gmail_est_ok=verifierSite(driver)
#On ferme l'onglet google pour pouvoir accéder au menu principal
fermer_onglet(driver)

########## Test BOX #########
#Bouton d'accès à Box par SSO
driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[2]/div/div[4]/a").click()
time.sleep(5)

window_box = driver.window_handles[1]
driver.switch_to.window(window_box)

#Confirmation qu'on fait partie d'Aleth
#bouton_box_confirme=driver.find_element_by_xpath("//div[contains(text(),'Continuer')]")
#bouton_box_confirme.click()
box_est_ok=verifierSite(driver)
fermer_onglet(driver)

################## TEST Request Manager ########################
#Bouton d'accès à Request Manager
driver.find_element_by_xpath("/html/body/div[5]/div[4]/div/div/div/div/div[2]/div[2]/div[3]/div/div[4]/a").click()
time.sleep(5)

window_rm = driver.window_handles[1]
driver.switch_to.window(window_rm)

time.sleep(5)
rm_est_ok=verifierSite(driver)

#On attend que la page s'affiche
#time.sleep(30)

#aleth_est_ok(gmail_est_ok,box_est_ok,rm_est_ok)

#On quitte le driver proprement, Chrome ça consomme un peu de RAM :p
driver.quit()


#Amélioration: -
# Implémentez fichier de logs pour gérer redémarage machine/service
# Checker sur le safekit les primaires et secondaire, et envoyer un mail si bascule
#  
