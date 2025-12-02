"""
URL configuration for furniture_app project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 📄 CONTENIDO ESTÁTICO (Sesión 1)
    path('static-pages/', include('staticpages.urls')),
    
    # 🎨 TEMPLATES DINÁMICOS (Sesión 2 y 3)
    path('dynamic-pages/', include('dynamicpages.urls')),
    
    # 🔌 API JSON
    path('api/', include('furniture_api.urls')),
]
