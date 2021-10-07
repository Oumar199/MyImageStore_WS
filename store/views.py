from django.http.response import JsonResponse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import request as rq
import requests
from PIL import Image
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from store.models import Image
import traceback
from django.contrib.auth.models import User
# from .forms import ContactForm
from django.http import HttpResponse
# Create your views here.
def index(request):
    message = "Salut tout le monde !"
    context = {
        'message': message
    }
    return render(request, 'store/index.html', context)

def listing(request):
    # Initialisation du driver 
    images_list = Image.objects.all().order_by('id')
    paginator = Paginator(images_list, 9    )
    page = request.GET.get('page')
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
 
def search(request):
    query = request.GET.get('query')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="C:\Program Files\chromedriver\chromedriver.exe", options=options)
    url = "https://www.google.sn/imghp?hl=fr&ogbl"
    driver.get(url)
    images_list = []
    search = driver.find_element_by_tag_name('input')
    search.clear()
    search.send_keys(query)
    search.send_keys(Keys.ENTER)
    final_imgs = []
    content = driver.page_source
    try:
        doc = BeautifulSoup(content, 'lxml')
        imgs = []
        for a in doc.find('div', class_ = "mJxzWe").find_all('a', class_ = ['wXeWr', 'islib', 'nfEiy']):
            src = a.find('img')
            imgs.append((a.find('img'), a.nextSibling))
            try:
                image = driver.find_element_by_css_selector("img[src = '{}']".format(src['src']))
                image.click()
                sous_lien = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.lxa62b.MIdC8d.So4Urb"))
                )
                sous_lien.click()
                content = driver.page_source
                doc = BeautifulSoup(content, 'lxml')
                imgs.extend([(a.find('img'), a.nextSibling) for a in doc.find('div', \
                    class_ = "mJxzWe").find_all('a', class_ = ['wXeWr', 'islib', 'nfEiy'])])
                driver.back()
                driver.back()
            except Exception:
                pass
        for img in imgs:
            try:
                if Image.objects.filter(title = img[1]['title']).exists(): 
                    pass
                else :
                    rq.urlopen(img[0]['src'])
                    images_list.append({"src" : img[0]['src'], "title": img[1]['title'], "categorie": query, "url": img[1]['href']})
            except Exception:
                pass
    except Exception as e:
        raise Exception("Erreur trouvée : %s"%(e))
    
    title = "%d résultats pour la recherche '%s'"%(len(images_list), query)
    context = {
        'images': images_list,
        'paginate': True,
        'title': title,
    }
    return render(request, 'store/search.html', context)
    
    
def save(request):
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
            return JsonResponse({"Response": "OK !","title":title, "src":len(src), "categorie":categorie, "url":url, "error": str(error)}, status = 200)
        else:
            return JsonResponse({"Response": "Image already saved !"}, status = 200)
    return JsonResponse({"Response": "Not OK !"}, status = 404)

def delete(request):
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
                
                
            