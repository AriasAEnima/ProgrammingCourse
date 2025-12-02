from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status


# Create your views here.

@api_view(['GET'])
def get_furniture(request,id):
    print(f"id del request : {id}")
    return JsonResponse({"heigh": 20 , "width": 30}, status=status.HTTP_200_OK)

@api_view(['POST'])
def post_furniture(request):
    body=request.data
    # request.headers
    # request.method
    return JsonResponse(body, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
def post_furniture(request):
    body=request.data
    # request.headers
    # request.method
    return JsonResponse(body, status=status.HTTP_201_CREATED)