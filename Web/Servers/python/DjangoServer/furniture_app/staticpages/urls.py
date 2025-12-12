# staticpages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='static_home'),
    path('about/', views.about, name='static_about'),
    path('contact/', views.contact, name='static_contact'),
]

