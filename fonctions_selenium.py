import requests

#import undetected_chromedriver as chromedriver

#Focntion permettant de fermer l'onglet en cours
def fermer_onglet(driver):
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])



#Fonction permettant de vérifier le statut de l'url
def verifierSite(driver):

    #Retourne le code de statut http de l'url visite 
    """code=requests.get(driver.current_url)#.status_code
    print(code)
    print(code.cookies)"""
    print(requests.get(driver.current_url))
    code=200
    #Retour de la fonction : 0 si l'url a un problème, 1 si tout fonctionne comme prévu
    retour=0
    #Suite de conditionnels ... on dirait de l'intelligence artificielle :p
    if (code==200):
        print("Le site "+ driver.current_url +" est bon")
        retour=1
    elif(code==404) :
        print("Le site "+ driver.current_url + "n'est pas atteignable")
        #Screenshot de la page gmail par contre j'ai pas reussi à la mettre dans un dossier Screenshot à l'endroit ou se trouve le script :'(
        driver.get_screenshot_as_file("ErrorVerifScreen.png")
    else :
        print("Autre erreur sur Aleth")
    return retour

#Fonction permettant de vérifier si tout est bon
def aleth_est_ok(gmail,box,rm):
        if (gmail==1 and box==1 and rm==1 ):
            print ("Tout est ok. Tu peux prendre une pause.")
        else:
            print ("C'est dommage ça ne marche pas.")
