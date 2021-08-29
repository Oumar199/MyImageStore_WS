from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib import request as rq
import requests
from PIL import Image
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from store.models import Image
# from .forms import ContactForm
# from django.http import HttpResponse
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
    paginator = Paginator(images_list, 6)
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

# def search(request):
#     query = request.GET.get('query')
#     if not query:
#         albums = Album.objects.all()
#     else:
#         albums = Album.objects.filter(title__icontains = query)
        
#         if not albums.exists():
#             albums = Album.objects.filter(artists__name__icontains = query)
    # title = "Résultats pour la requête %s"%query
#     context = {
#         'albums': albums,
#         'title': title,
#     }
#     return render(request, 'store/search.html', context)
    
def search(request):
    query = request.GET.get('query')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options = options)
    url = "https://www.google.sn/imghp?hl=fr&ogbl"
    driver.get(url)
    images_list = []
    search = driver.find_element_by_tag_name('input')
    search.clear()
    search.send_keys(query)
    search.send_keys(Keys.ENTER)
    content = driver.page_source
    try:
        doc = BeautifulSoup(content, 'lxml')
        imgs = [(a.find('img'), a.nextSibling) for a in doc.find('div', \
            class_ = "mJxzWe").find_all('a', class_ = ['wXeWr', 'islib', 'nfEiy'])]
        for img in imgs:
            try:
                rq.urlopen(img[0]['src'])
                images_list.append({"src" : img[0]['src'], "title": img[1]['title'], "categorie": query, "url": img[1]['href']})
                print("ok")
            except Exception:
                print("no ok")
    except Exception:
        raise Exception("Impossible de parser le lien")
    # for album in albums_list:
    #     artists = " et ".join([artist.name for artist in album.artists.all()])
    #     search.send_keys(Keys.ENTER)
    #     lien = driver.current_url
    #     try:
    #         doc = BeautifulSoup(content, 'lxml')
    #         imgs = [img['src'] for img in doc.find_all('img')]
    #         is_ok = False
    #         for img in imgs:
    #             try:
    #                 Image.open(rq.urlopen(img))
    #                 srcs.append(img)
    #                 is_ok = True
    #             except Exception:
    #                 pass
    #             if is_ok:
    #                 break;
    #     except Exception:
    #         pass
    # print(images_list)
    # paginator = Paginator(images_list, 6)
    # page = request.GET.get('page')
    # try:
        # images = paginator.page(page)
    # except PageNotAnInteger:
        # images = paginator.page(1)
    # except EmptyPage:
        # images = paginator.page(paginator.num_pages)
    title = "Résultats pour la requête '%s'"%query
    context = {
        'images': images_list,
        'paginate': True,
        'title': title,
    }
    return render(request, 'store/search.html', context)
    
    
def save(request):
    query = request.GET.get(request)
    print(query)