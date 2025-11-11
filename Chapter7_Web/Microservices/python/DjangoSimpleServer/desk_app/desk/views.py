from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Desk
from .serializers import DeskSerializer
from .services import websocket_notifier
from mongoengine.errors import DoesNotExist, ValidationError
from bson.errors import InvalidId


# ========== FUNCIONES AUXILIARES COMPARTIDAS ==========

def get_desk_or_404(desk_id):
    """
    Helper para obtener una mesa o lanzar error 404
    
    Args:
        desk_id (str): ID de la mesa
        
    Returns:
        Desk: La mesa encontrada
        
    Raises:
        DoesNotExist/InvalidId: Si la mesa no existe
    """
    try:
        return Desk.objects.get(id=desk_id)
    except (DoesNotExist, InvalidId):
        # Retornar None si no existe (para que cada función maneje su error)
        return None


def validate_and_save_desk(data, instance=None, partial=False):
    """
    Helper para validar y guardar una mesa usando el serializer
    
    Args:
        data: Datos a validar
        instance: Instancia existente (para actualización) o None (para creación)
        partial: True para permitir actualizaciones parciales
        
    Returns:
        tuple: (serializer_data, error_response)
    """
    serializer = DeskSerializer(instance, data=data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return serializer.data, None
    
    return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_paginated_desks(limit=None, offset=None):
    """
    Helper para obtener mesas con paginación opcional
    
    Args:
        limit: Número máximo de resultados
        offset: Número de resultados a saltar
        
    Returns:
        QuerySet: Mesas filtradas
    """
    desks = Desk.objects.all()
    
    if limit:
        limit = int(limit)
        offset = int(offset) if offset else 0
        desks = desks[offset:offset + limit]
    
    return desks


# ========== FUNCIONES DE LÓGICA DE NEGOCIO (Separadas por responsabilidad) ==========

def _handle_list_desks(request):
    """Lógica para listar todas las mesas"""
    try:
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        
        desks = get_paginated_desks(limit, offset)
        serializer = DeskSerializer(desks, many=True)
        
        return Response({
            "count": Desk.objects.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"Error al obtener las mesas: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _handle_create_desk(request):
    """Lógica para crear una nueva mesa"""
    print(f"Creando mesa: {request.data}")
    
    serializer = DeskSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar la mesa
    desk = serializer.save()
    
    # Enviar notificación WebSocket
    websocket_notifier.notify_desk_created(desk)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _handle_get_desk(desk_id):
    """Lógica para obtener una mesa por ID"""
    desk = get_desk_or_404(desk_id)
    
    if not desk:
        return Response(
            {"error": f"No se encontró una mesa con id: {desk_id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DeskSerializer(desk)
    return Response(serializer.data, status=status.HTTP_200_OK)


def _handle_update_desk(request, desk_id):
    """Lógica para actualizar una mesa"""
    print(f"Actualizando mesa {desk_id}: {request.data}")
    
    desk = get_desk_or_404(desk_id)
    
    if not desk:
        return Response(
            {"error": f"No se encontró una mesa con id: {desk_id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # partial=True para PATCH, False para PUT
    partial = request.method == 'PATCH'
    serializer = DeskSerializer(desk, data=request.data, partial=partial)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Guardar cambios
    updated_desk = serializer.save()
    
    # Enviar notificación WebSocket
    websocket_notifier.notify_desk_updated(updated_desk)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


def _handle_delete_desk(desk_id):
    """Lógica para eliminar una mesa"""
    desk = get_desk_or_404(desk_id)
    
    if not desk:
        return Response(
            {"error": f"No se encontró una mesa con id: {desk_id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Guardar datos antes de eliminar
    desk_name = desk.name
    desk_id_str = str(desk.id)
    
    # Eliminar mesa
    desk.delete()
    
    # Enviar notificación WebSocket
    websocket_notifier.notify_desk_deleted(desk_id_str, desk_name)
    
    return Response(
        {
            "message": f"Mesa '{desk_name}' eliminada exitosamente",
            "desk_id": desk_id_str
        },
        status=status.HTTP_200_OK
    )


# ========== VISTAS (Dispatchers que delegan a funciones de lógica) ==========

@api_view(['GET', 'POST'])
def desk_list(request):
    """
    GET  /api/desk/  → Listar todas las mesas
    POST /api/desk/  → Crear una nueva mesa
    
    Esta vista actúa como dispatcher: Django enruta aquí por el path,
    y luego delegamos a la función específica según el método HTTP.
    """
    if request.method == 'GET':
        return _handle_list_desks(request)
    elif request.method == 'POST':
        return _handle_create_desk(request)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def desk_detail(request, desk_id):
    """
    GET    /api/desk/<id>  → Obtener una mesa
    PUT    /api/desk/<id>  → Actualizar mesa completa
    PATCH  /api/desk/<id>  → Actualizar mesa parcialmente
    DELETE /api/desk/<id>  → Eliminar mesa
    
    Esta vista actúa como dispatcher: Django enruta aquí por el path,
    y luego delegamos a la función específica según el método HTTP.
    """
    if request.method == 'GET':
        return _handle_get_desk(desk_id)
    elif request.method in ['PUT', 'PATCH']:
        return _handle_update_desk(request, desk_id)
    elif request.method == 'DELETE':
        return _handle_delete_desk(desk_id)
