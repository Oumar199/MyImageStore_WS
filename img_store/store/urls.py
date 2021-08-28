from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index),
    path('listing/', views.listing, name = 'listing'),
    path('search/', views.search, name = "search")
]
