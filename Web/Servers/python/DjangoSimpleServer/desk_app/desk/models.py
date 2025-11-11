from mongoengine import Document, StringField, IntField

# Modelo de Mesa usando MongoEngine
class Desk(Document):
    """
    Modelo para representar una mesa en MongoDB
    """
    name = StringField(required=True, max_length=100)
    width = IntField(required=True, min_value=0)
    height = IntField(required=True, min_value=0)
    
    meta = {
        'collection': 'desks',  # Nombre de la colección en MongoDB
        'ordering': ['name']     # Ordenar por nombre por defecto
    }
    
    def to_dict(self):
        """
        Convierte el documento de MongoDB a un diccionario para la API
        """
        return {
            'desk_id': str(self.id),  # MongoDB usa ObjectId, lo convertimos a string
            'name': self.name,
            'width': self.width,
            'height': self.height
        }
