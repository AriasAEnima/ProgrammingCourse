from django.urls import path
from . import views

urlpatterns = [
    path('furniture/<str:id>/', views.get_furniture, name="get_furniture"),
    path('furniture/', views.post_furniture, name="post_furniture"),
]