from django.urls import path
from . import views 

urlpatterns = [
    path('furnitures/',views.get_furnitures, name="get_furnitures"),
    path('furniture/', views.post_furniture, name="post_furniture"),
    path('furniture/<str:id>/',views.handle_one_furniture, name= "get_furniture"),
]
