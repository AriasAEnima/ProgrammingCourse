# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs más explícitas y educativas
    path('blogentries/list/', views.lista_blogentries, name='api_lista_blogentries'),
    path('blogentries/create/', views.crear_blogentry, name='api_crear_blogentry'),
    path('blogentries/<int:pk>/', views.detalle_blogentry, name='api_detalle_blogentry'),
    path('stats/', views.estadisticas_blog, name='api_estadisticas'),
]
