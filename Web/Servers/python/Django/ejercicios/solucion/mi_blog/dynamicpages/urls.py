from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_blogentries, name='lista_blogentries'),
    path('blogentry/<int:blogentry_id>/', views.detalle_blogentry, name='detalle_blogentry'),
]