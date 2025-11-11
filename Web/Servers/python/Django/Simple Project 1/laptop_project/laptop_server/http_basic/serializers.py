from .models import RequestToJson
from rest_framework import serializers

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestToJson
        fields =  ['method','path_param','headers', 'body']