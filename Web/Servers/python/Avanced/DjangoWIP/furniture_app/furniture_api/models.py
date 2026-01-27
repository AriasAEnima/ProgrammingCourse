from django.db import models
from datetime import datetime
from mongoengine import Document, StringField, IntField,DateTimeField
# Create your models here.

class FurnitureItem(Document):
    name = StringField(max_length=200, required= True)
    width = IntField(min_value=1, required= True)
    height = IntField(min_value=1, required= True)
    depth = IntField(min_value=1, required= True)
    material = StringField(max_length=20)
    creation_date = DateTimeField(default=datetime.now)
    author = StringField(max_length=20)
    
    meta = {
        'collection': "furnitures",
        'ordering': ['-creation_date']
    }
    
    def as_dic(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "material": self.material
        }        
    
    def __str__(self):
        return f"{self.name} : {self.width}x{self.height}x{self.depth} {self.material}"
    
