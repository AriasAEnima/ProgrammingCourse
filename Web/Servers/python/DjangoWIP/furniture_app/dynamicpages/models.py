# dynamicpages/models.py
from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField
from datetime import datetime

class FurnitureItem(Document):
    """Modelo de mueble - se guarda en MongoDB"""
    nombre = StringField(max_length=200, required=True)
    descripcion = StringField(required=True)
    altura = IntField(required=True)  # en cm
    ancho = IntField(required=True)   # en cm
    material = StringField(max_length=100, required=True)
    autor_username = StringField(required=True)  # Usuario que lo registró
    fecha_creacion = DateTimeField(default=datetime.now)
    publicado = BooleanField(default=True)
    
    meta = {
        'collection': 'furniture_items',
        'ordering': ['-fecha_creacion']
    }
    
    def __str__(self):
        return f"{self.nombre} ({self.material})"
