from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongo_serializers
from .models import Desk


class DeskSerializer(serializers.Serializer):
    """
    Serializer para el modelo Desk de MongoDB
    Maneja la validación automática de campos
    """
    desk_id = serializers.CharField(read_only=True, source='id')
    name = serializers.CharField(required=True, max_length=100)
    width = serializers.IntegerField(required=True, min_value=0)
    height = serializers.IntegerField(required=True, min_value=0)
    
    def create(self, validated_data):
        """
        Crea una nueva mesa con los datos validados
        """
        desk = Desk(**validated_data)
        desk.save()
        return desk
    
    def update(self, instance, validated_data):
        """
        Actualiza una mesa existente con los datos validados
        """
        instance.name = validated_data.get('name', instance.name)
        instance.width = validated_data.get('width', instance.width)
        instance.height = validated_data.get('height', instance.height)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """
        Convierte el objeto Desk a diccionario
        """
        return {
            'desk_id': str(instance.id),
            'name': instance.name,
            'width': instance.width,
            'height': instance.height
        }

