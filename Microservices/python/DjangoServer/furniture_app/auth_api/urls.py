from django.urls import path
from . import views

urlpatterns = [
    # 🔐 Autenticación endpoints
    path('login/', views.login, name='login'),           # POST - Login
    path('register/', views.register, name='register'),  # POST - Registro
]

