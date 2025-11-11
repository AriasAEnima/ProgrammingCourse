from django.db import models

# Create your models here.

class RequestToJson(models.Model):
    method = models.CharField(max_length=200)
    path_param = models.CharField(max_length=200)
    headers = models.JSONField()
    body = models.JSONField()
    