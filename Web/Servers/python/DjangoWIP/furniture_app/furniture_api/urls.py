from django.urls import path
from . import views

urlpatterns = [
    # 🪑 Furniture API endpoints
    path('furniture/', views.list_furniture, name="list_furniture"),      # GET - Lista todos
    path('furniture/create/', views.post_furniture, name="post_furniture"), # POST - Crear
    path('furniture/<str:id>/', views.get_furniture, name="get_furniture"),  # GET - Obtener uno
    path('furniture/<str:id>/update/', views.put_furniture, name="put_furniture"),  # PUT - Actualizar
    path('furniture/<str:id>/delete/', views.delete_furniture, name="delete_furniture"),  # DELETE - Eliminar
]
