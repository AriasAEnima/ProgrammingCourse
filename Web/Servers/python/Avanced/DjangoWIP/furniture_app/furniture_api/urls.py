from django.urls import path
from . import views 

urlpatterns = [
    path('furnitures/',views.get_furnitures, name="get_furnitures"),
    path('furniture/', views.post_furniture, name="post_furniture") 
]
