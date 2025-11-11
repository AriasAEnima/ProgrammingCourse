from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class BlogEntry(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    publicado = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo