from django.urls import path
from . import views

urlpatterns = [
    # 🪑 Furniture API endpoints
    path('furniture/', views.list_furniture, name="list_furniture"),      # GET - Lista todos
    path('furniture/create/', views.post_furniture, name="post_furniture"), # POST - Crear
    path('furniture/<str:id>/', views.handle_furniture, name="handle_furniture"),  # GET - DELETE Obtener uno
    path('furniture/<str:id>/update/', views.put_furniture, name="put_furniture"),  # PUT - Actualizar
]
