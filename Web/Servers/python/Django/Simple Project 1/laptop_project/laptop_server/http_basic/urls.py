from django.urls import path
from . import views 


urlpatterns = [
    path('saludo/<str:nombre>/', views.saludo, name= 'saludo'),
    path('debug/<str:parameter>/', views.debug, name='debug'),
    path('imagen/<str:nombre_imagen>/', views.servir_imagen, name='imagen')
]