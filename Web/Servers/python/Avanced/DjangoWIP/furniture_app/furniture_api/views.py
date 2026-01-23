from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def get_furnitures(request):
    return Response([{"description": "Mesa cuadrada"}], status=200)

@api_view(['POST'])
def post_furniture(request):
    return Response({"description": "Mesa cuadrada"}, status=201)