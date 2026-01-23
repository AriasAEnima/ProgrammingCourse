from django.db import models

# Create your models here.

class Material:
    # **kwargs Materials(name= , descrition= ..... )
    def __init__(self,dic):
        self.name= dic["name"]
        self.description= dic["description"]
        self.price_starting= dic["price_starting"]
        self.furniture_types= dic["furniture_types"]
        
        
def create_materials(dic):
    return list(map( lambda e: Material(e), dic) )

MATERIALS = create_materials([
    {"name": "Madera", 
     "description": "Cedro claro",
     "price_starting": 300000, 
     "furniture_types": "Camas, mesas y escritorios"},
    {"name": "Metal",
     "description": "Acero de diferentes colores", 
     "price_starting": 300000, 
     "furniture_types": "Estantes, mesas y sillas" },
    {"name": "Marmol",
     "description": "Marol de diferentes colores y patrones", 
     "price_starting": 4000000, 
     "furniture_types": "Mesas, bibliotecas y escritorios" },
    {"name": "Vidrio",
     "description": "de 25 mm a 30 mm", 
     "price_starting": 3000000, 
     "furniture_types": "Mesas, estantes y escritorios" }  
])

