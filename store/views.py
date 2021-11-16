# from django.core import paginator
from django.http.response import JsonResponse
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import request as rq
import os
from glob import glob
# import requests
# from PIL import Image
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from store.models import Image
from django.contrib.auth.models import User
# from .forms import ContactForm
from django.http import HttpResponse
# Create your views here.
def index(request):
    '''Cette fonction permet d'afficher l'acceuil de la plateforme
    Args:
        request(Any): Une requête envoyée à la fonction
    Returns:
        Redirection vers le template d'affichage de l'accueil
    '''
    # message = "Salut tout le monde !"

    return render(request, 'store/index.html')

def listing(request):
    '''Cette fonction permet de lister toutes les images contenues dans la base de données grace au modele 'Image' créé à cet
    effet. La classe Paginator est utilisée pour la pagination des résultats.
    Args:
        request(Any): Une requête envoyée à la fonction
    Returns:
        La liste d'images et une variable booléens indiquant que les résultats sont paginées
        sont retournés vers le template qui va afficher les résultats
    '''
    # Initialisation du driver 
    images_list = Image.objects.all().order_by('id')
    paginator = Paginator(images_list, 12)
    page = request.GET.get('page', 1)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)
    context = {
        'images': images,
        'paginate': True,
        }
    return render(request, 'store/listing.html', context)
 
# def pagination(images_list):
    

def search(request):
    """ Cette méthode doit récupérer les mots clés de la recherche et utiliser le web-Scraping pour récupérer (gratter) toutes 
    les résultats de Google Image correspondant aux termes de la recherche. Les résultats devront être retournés au gabarit
    search.html
    Args:
        request(Any) : la requête envoyée au serveur de Django avec la méthode GET 
    Returns:
        Les résultats de la recherche (liste d'images et titre) sont retournés vers un template qui va les afficher
    """
    #On vérifie si la méthode employée est GET
    if request.method == "GET":
        
        # Récupération des mots clés
        query = request.GET.get('query', '')
        
        # On récupère les options de contrôle de la fenêtre de navigation Chrome 
        options = webdriver.ChromeOptions()
        
        # On ajoute l'argument --headless qui va faire disparaitre la fenetre de navigation pour diminuer le temps
        # d'attente
        options.add_argument("--headless")
        
        # On récupère le service
        s = service.Service(executable_path="C:\Program Files\Chromedriver\chromedriver.exe")
        
        # On récupère le driver
        driver = webdriver.Chrome(service = s, options=options)
        
        # Affectation de l'url de Google Image à la variable url
        url = "https://www.google.sn/imghp?hl=fr&ogbl"
        
        # Récupération de l'adresse et execution de la requete 
        driver.get(url)
        
        # On initialise la liste des images 
        images_list = []
        
        # Recherche dans la page d'acceuil de la barre de recherche
        search = driver.find_element_by_tag_name('input')
        
        # Effacons le contenu de la barre de recherche
        search.clear()
        
        # Envoyons les mots clés dans la barre de recherche
        search.send_keys(query)
        
        # Effectuons la recherche voulue dans la page 
        search.send_keys(Keys.ENTER)
        
        # Récupération du contenu de la page des résultats
        content = driver.page_source
        
        # Essayons de parser le contenu 
        try:
            # Récupération des élements de la page
            doc = BeautifulSoup(content, 'lxml')
            
            # Récupération des liens contenu dans le div où les résultats sont présents 
            links = [a for a in doc.find('div', class_ = "OcgH4b").find_all('a', class_ = ['wXeWr', 'islib', 'nfEiy'])]
            
            # Pour chaque lien effectuons des manipulations
            for a in links:
                
                # Récupération de l'image contenu dans le lien '<a>'
                src = a.find('img')
                
                # Stockons dans une variable un tuple contenant l'image et le lien voisin qui contient l'url de la page source
                # de l'image
                img = ((a.find('img'), a.nextSibling))
                
                # Essayons de récupérer les attributs du résultat dans une liste si le résultat en question n'est pas déjà enre-
                # -gistré dans la base de données
                try:
                    if (not Image.objects.filter(title = img[1]['title']).exists()):                         
                            images_list.append({"src" : img[0]['src'], "title": img[1]['title'], "categorie": query, "url": img[1]['href']})
                except Exception:
                    pass
                
                # Essayons de stocker les images similaires à l'image précédemment enregistrée dans la liste
                try:
                    # Trouvons l'image avec selenium à l'aide de sa source
                    image = driver.find_element_by_css_selector(f"img[src = '{src['src']}']")
                    
                    # Effectuons un click sur l'image
                    image.click()
                    
                    # Réalisons une attente pour voir si tous les images similaires sont chargées
                    WebDriverWait(driver, 0.6).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.lxa62b.MIdC8d.So4Urb"))
                    ) 
                    # sous_lien = driver.find_element_by_css_selector("a.lxa62b.MIdC8d.So4Urb")
                    # sous_lien.click()
                    
                    # Le contenu de la page a changé donc récupérons le une nouvelle fois
                    content = driver.page_source
                    
                    # Récupérons les éléments du nouveau contenu
                    doc = BeautifulSoup(content, 'lxml')
                    
                    # Pour chacun des liens conformes aux images similaires effectuons des manipulations
                    for a2 in doc.find('div', {'id': 'islsp'}).find_all('a', class_ = ['wXeWr', 'islib', 'nfEiy']):
                        # Stockons dans une variable un tuple contenant l'image et le lien voisin qui contient l'url de la page source
                        # de l'image similaire
                        img = ((a2.find('img'), a2.nextSibling))
                        
                        # Essayons de récupérer les attributs concernant cette image similaire à l'image de premier niveau
                        # si cette image similaire ne se trouve déjà dans la base de données
                        try:
                            if (not Image.objects.filter(title = img[1]['title']).exists()):                         
                                    images_list.append({"src" : img[0]['src'], "title": img[1]['title'], "categorie": query, "url": img[1]['href']})
                        except Exception:
                            pass
                except Exception:
                    pass
            
            '''Le code mis en commentaire permet de récupérer de manière aléatoire presque 200 images de différentes niveaux 
            mais le temps d'execution du code nous oblige à ne pas l'utiliser. Le concept est tout de même intéressant dans 
            la mesure ou la variété de types d'images recueillies est très grande.'''
            # for i in range(200):
            #     content = driver.page_source
            #     doc = BeautifulSoup(content, 'lxml')
            #     links = [a for a in doc.find('div', class_ = "mJxzWe").find_all('a', class_ = ['wXeWr', 'islib', 'nfEiy'])]
            #     link = random.choice(links)
            #     src = link.find('img')
            #     imgs.append((link.find('img'), link.nextSibling))
            #     try:
            #         image = driver.find_element_by_css_selector("img[src = '{}']".format(src['src']))
            #         image.click()
            #         sous_lien = WebDriverWait(driver, 0.6).until(
            #             EC.presence_of_element_located((By.CSS_SELECTOR, "a.lxa62b.MIdC8d.So4Urb"))
            #         ) 
            #         # sous_lien = driver.find_element_by_css_selector("a.lxa62b.MIdC8d.So4Urb")
            #         sous_lien.click()
            #         content = driver.page_source
            #     except Exception:
            #         pass
            
        except Exception as e:
            # fermer le driver de google chrome à la vue d'une erreur
            driver.quit()
            
            # afficher l'erreur
            raise Exception("Erreur trouvée : %s"%(e))
        finally:
            # fermer le driver de google chrome après avoir terminé le web scraping
            driver.quit()
        
    '''Le code mis en commentaire suivant nous permettait d'effectuer une pagination des résultats mais n'est pas valable 
    pour ce cas de figure assez complexe de Web-Scraping'''
  
    # Affectation du titre de la page de résultats de la recherche 
    title = "%d résultats pour la recherche '%s'"%(len(images_list), query)
    
    # Enregistrement du contexte sous forme de dictionnaire
    context = {
        'images': images_list,
        'title': title,
        # 'paginate': True
    }
    
    # Retournons le résultat vers un template
    return render(request, 'store/search.html', context)
    
    
def local_storage(objet: dict):
    '''Cette fonction permet de télécharger l'image sauvegardée à partir du view save dans une répertoire 
    dont le nom sera l'étiquette de cette image. Cela dans le but d'entrainer un modéle capable de reconnaitre les images
    qu'on lui présente. Les librairies capables de manipuler des répertoires et de les analyser seront utilisées
    Args:
        object(dict): Un dictionnaire contenant les attributs de l'image sauvegardée
    Returns:
        None
    '''
    characters = "éèê"
    categorie = objet["categorie"]
    categorie = str.lower(categorie)
    for character in characters:
        categorie = categorie.replace(character, "e")
    categorie = categorie.replace("à", "a")
    categorie = categorie.replace("ù", "u")
    categorie = categorie.replace("î", "i")
    categorie = categorie.replace("â", "a")
    categorie = categorie.replace("ô", "o")
    path = os.getcwd() + "/store/static/store/assets/stockage/{}".format(categorie)
    if not os.path.exists(path):
        print(path)
        os.makedirs(path)
    number = len(glob(path + "/*"))
    try:
        rq.urlretrieve(objet['src'], path + f"/image{str(number+1)}.jpg")
    except Exception as e:
        print(str(e))
    return os.getcwd()+r"\store\static\store\assets\stockage"

def save(request):
    '''Cette fonction doit sauvegarder une image dans la base de données après avoir vérifié que l'image n'existe pas déjà.
    Utilise une fonction local_storage pour le téléchargement des images.
    Args:
        request(Any): Les attributs de l'image à sauvegarder
    Returns:
        Une réponse Json 
    '''
    if request.is_ajax and request.method == 'POST':
        title = request.POST.get("title")
        categorie = request.POST.get("categorie")
        src = request.POST.get("src")
        url = request.POST.get("url")
        if not Image.objects.filter(title = title, url = url).exists():
            error = None
            try:
                Image.objects.create(title = title, categorie = categorie, src = src, url = url)
            except Exception as e:
                error = e
            objet = {"title":title, "src": src, "categorie": categorie, "error": str(error)}
            local_storage(objet)
            return JsonResponse({"error": str(error)}, status = 200)
        else:
            return JsonResponse({"Response": "Image already saved !"}, status = 200)
    return JsonResponse({"Response": "Not OK !"}, status = 404)

def delete(request):
    '''Cette fonction supprime une image de la base de données sans toucher au répertoire de celle-ci. Utilise la méthode Post 
    pour la supression comme pour la sauvegarde
    Args:
        request(Any): le titre de l'image à supprimer
    Returns:
        Une réponse Json
    '''
    if request.is_ajax and request.method == 'POST':
        title = request.POST.get("title")
        if Image.objects.filter(title = title).exists():
            error = None
            try:
                Image.objects.filter(title = title).delete()
            except Exception as e:
                error = e
            return JsonResponse({"Response": "OK !","title":title, "error": str(error)}, status = 200)
        else:
            return JsonResponse({"Response": "Image don't exist !"}, status = 200)
    return JsonResponse({"Response": "Not OK !"}, status = 404)
                
                
            