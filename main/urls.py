from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about_me/', views.about_me, name='about_me'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
