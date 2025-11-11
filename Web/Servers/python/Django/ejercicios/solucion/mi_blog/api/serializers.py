# api/serializers.py
from rest_framework import serializers
from dynamicpages.models import BlogEntry  # ✅ Reutilizamos el modelo
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información del autor"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class BlogEntrySerializer(serializers.ModelSerializer):
    """Serializer para convertir BlogEntry a JSON y viceversa"""
    autor = UserSerializer(read_only=True)  # Solo lectura para el autor
    
    class Meta:
        model = BlogEntry
        fields = [
            'id', 
            'titulo', 
            'contenido', 
            'autor', 
            'fecha_creacion', 
            'publicado'
        ]
        read_only_fields = ['id', 'fecha_creacion']

# Ya no necesitamos serializer específico para creación
