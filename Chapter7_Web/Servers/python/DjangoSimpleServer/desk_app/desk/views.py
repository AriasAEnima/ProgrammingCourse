from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
@api_view(['GET',"POST","PUT"])
def get_desk(request):
    if request.method == "GET":
        return Response({ "id": 1, "name": "Mesa Redonda",
                        "width": 150, "height": 150})
    elif request.method == "POST":
        body =  request.data
        print(f"Data recibida = {body}" )
        return Response(body, status=status.HTTP_201_CREATED)
    else:
        body =  request.data
        print(f"Data recibida = {body}")
        return Response(body, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_desks(_):
   
        return Response([
                {"desk_id": 1, "name": "Mesa Venture", "width": 125, "height": 225},
                {"desk_id": 2, "name": "Mesa Koto", "width": 200, "height": 223},
                {"desk_id": 3, "name": "Mesa Amatista", "width": 200, "height": 300}
            ])
   
    
    
