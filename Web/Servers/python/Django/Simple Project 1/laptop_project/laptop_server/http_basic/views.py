from django.http import HttpResponse, FileResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RequestSerializer
from rest_framework import status
from django.conf import settings
import os

# Create your views here.

@api_view(['GET'])
def saludo(request, nombre):
    print(request.method)
    return HttpResponse(f"<h1> ¡ Hola {nombre} ! </h1>")

@api_view(['GET','POST'])
def debug(request, parameter):
    print(request.headers)
    print(request.data)
    response={
        'method': request.method,
        'path_param': parameter,
        'headers': {}, # Todo Serializer headers (?)
        'body': request.data
    }

    serializer = RequestSerializer(data=response)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def servir_imagen(request, nombre_imagen):
    if request.method != 'GET':
        return HttpResponse(status=405)
    
    # Construir ruta de la imagen
    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', f'{nombre_imagen}-123.jpg')
    
    try:
        # ✨ CLAVE: FileResponse para archivos
        return FileResponse(open(ruta_imagen, 'rb'), content_type='image/png')
    except FileNotFoundError:
        raise Http404("Imagen no encontrada")