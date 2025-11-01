from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@api_view(['GET'])
def get_desk(_):
    return Response({ "id": 1, "name": "Mesa Redonda",
                     "width": 150, "height": 150})