from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_desk, name='api_get_desk'),
    path('all', views.get_desks , name='api_get_all_desks')
]