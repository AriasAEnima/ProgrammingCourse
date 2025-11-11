# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from dynamicpages.models import BlogEntry  # ✅ Reutilizamos el modelo
from .serializers import BlogEntrySerializer
from django.contrib.auth.models import User

@api_view(['GET'])
def lista_blogentries(request):
    """
    API manual - Solo lista todas las entradas
    GET /api/v1/blogentries/list/ → Lista todas las entradas en JSON
    """
    # Obtener todas las entradas publicadas
    blogentries = BlogEntry.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    # Convertir a JSON usando el serializer
    serializer = BlogEntrySerializer(blogentries, many=True)
    
    # Devolver respuesta JSON
    return Response({
        'count': len(blogentries),
        'results': serializer.data
    })

@api_view(['POST'])
def crear_blogentry(request):
    """
    API manual - Solo crea una nueva entrada
    POST /api/v1/blogentries/create/ → Crear nueva entrada desde JSON
    """
    # Crear nueva entrada desde JSON
    serializer = BlogEntrySerializer(data=request.data)
    
    if serializer.is_valid():
        # Asignar usuario demo automáticamente
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@example.com'}
        )
        serializer.save(autor=demo_user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def detalle_blogentry(request, pk):
    """
    API manual - Operaciones sobre una entrada específica
    GET /api/v1/blogentries/1/ → Detalle en JSON
    PUT /api/v1/blogentries/1/ → Actualizar entrada
    DELETE /api/v1/blogentries/1/ → Eliminar entrada
    """
    # Buscar la entrada o devolver 404
    blogentry = get_object_or_404(BlogEntry, pk=pk, publicado=True)
    
    if request.method == 'GET':
        # Devolver detalle en JSON
        serializer = BlogEntrySerializer(blogentry)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Actualizar entrada completa
        serializer = BlogEntrySerializer(blogentry, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Eliminar entrada
        blogentry.delete()
        return Response({'message': 'Entrada eliminada correctamente'}, 
                       status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def estadisticas_blog(request):
    """
    Endpoint personalizado - Estadísticas del blog
    GET /api/v1/stats/ → Estadísticas en JSON
    """
    stats = {
        'total_entries': BlogEntry.objects.count(),
        'published_entries': BlogEntry.objects.filter(publicado=True).count(),
        'draft_entries': BlogEntry.objects.filter(publicado=False).count(),
        'total_authors': User.objects.count(),
        'latest_entry': None
    }
    
    # Agregar última entrada si existe
    latest = BlogEntry.objects.filter(publicado=True).order_by('-fecha_creacion').first()
    if latest:
        stats['latest_entry'] = {
            'id': latest.id,
            'titulo': latest.titulo,
            'autor': latest.autor.username,
            'fecha': latest.fecha_creacion
        }
    
    return Response(stats)