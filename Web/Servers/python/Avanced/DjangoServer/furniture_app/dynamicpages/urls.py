# dynamicpages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_muebles, name='lista_muebles'),
    path('<str:id>', views.detalle_mueble, name='detalle_mueble'),
    path('crear/', views.crear_mueble, name='crear_mueble'),
    path('v2/', views.lista_muebles_v2, name='lista_muebles_new'),
]

