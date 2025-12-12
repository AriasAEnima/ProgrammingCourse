from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dynamicpages.models import FurnitureItem
from auth_api.utils import jwt_required, admin_required
from typing import Dict, Any

@api_view(['GET','DELETE'])
@jwt_required
def handle_furniture(request, id: str) -> Response:
    """
    🪑 Maneja peticiones GET y DELETE para un mueble específico
    
    GET - Obtiene información de un mueble por ID
    DELETE - Elimina un mueble del catálogo (requiere autenticación)
    
    Args:
        request: Request HTTP con JWT token
        id: ID del mueble en MongoDB
        
    Returns:
        Response con datos del mueble o mensaje de error
    """
    if request.method == "GET":
        return get_furniture(request, id)
    else:
        return delete_furniture(request, id)
                
def get_furniture(request, id: str) -> Response:
    """
    🪑 GET - Obtener un mueble por ID desde MongoDB
    
    Ejemplo: GET /api/furniture/123/
    Headers: Authorization: Bearer <token>
    
    Args:
        request: Request HTTP
        id: ID del mueble
        
    Returns:
        Response con datos del mueble o error 404
    """
    try:
        mueble: FurnitureItem = FurnitureItem.objects.get(id=id)
        
        return Response({
            "id": str(mueble.id),
            "nombre": mueble.nombre,
            "descripcion": mueble.descripcion,
            "altura": mueble.altura,
            "ancho": mueble.ancho,
            "material": mueble.material,
            "autor_username": mueble.autor_username,
            "fecha_creacion": mueble.fecha_creacion,
            "publicado": mueble.publicado
        }, status=status.HTTP_200_OK)
    except FurnitureItem.DoesNotExist:
        return Response({
            "error": "Mueble no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@jwt_required
def post_furniture(request) -> Response:
    """
    🪑 POST - Crear un nuevo mueble en MongoDB (requiere autenticación)
    
    El autor se obtiene automáticamente del JWT token
    
    Ejemplo: POST /api/furniture/create/
    Headers: Authorization: Bearer <token>
    Body: {
        "nombre": "Mesa de Roble",
        "descripcion": "Mesa de comedor elegante",
        "altura": 75,
        "ancho": 120,
        "material": "roble"
    }
    
    Args:
        request: Request HTTP con JWT token y datos del mueble
        
    Returns:
        Response con el mueble creado o mensaje de error
    """
    data: Dict[str, Any] = request.data
    
    # Validar campos requeridos
    required_fields: list[str] = ['nombre', 'descripcion', 'altura', 'ancho', 'material']
    missing_fields: list[str] = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return Response({
            "error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Obtener el username del usuario autenticado desde el JWT token
        autor_username: str = request.user_info['username']
        
        # Crear mueble en MongoDB
        mueble: FurnitureItem = FurnitureItem(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            altura=int(data['altura']),
            ancho=int(data['ancho']),
            material=data['material'],
            autor_username=autor_username,  # 🔐 Obtenido del token JWT
            publicado=data.get('publicado', True)
        )
        mueble.save()
        
        return Response({
            "id": str(mueble.id),
            "message": "Mueble creado exitosamente",
            "nombre": mueble.nombre,
            "descripcion": mueble.descripcion,
            "altura": mueble.altura,
            "ancho": mueble.ancho,
            "material": mueble.material,
            "autor_username": mueble.autor_username
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "error": f"Error al crear mueble: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@jwt_required
def put_furniture(request, id: str) -> Response:
    """
    🪑 PUT - Actualizar un mueble existente en MongoDB (requiere autenticación)
    
    Ejemplo: PUT /api/furniture/123/update/
    Headers: Authorization: Bearer <token>
    Body: {"altura": 80, "ancho": 150, "material": "pino"}
    
    Args:
        request: Request HTTP con JWT token y datos a actualizar
        id: ID del mueble en MongoDB
        
    Returns:
        Response con el mueble actualizado o mensaje de error
    """
    try:
        mueble: FurnitureItem = FurnitureItem.objects.get(id=id)
        data: Dict[str, Any] = request.data
        
        # Verificar que el usuario autenticado sea el autor o admin
        autor_username: str = request.user_info['username']
        user_role: str = request.user_info['role']
        
        if mueble.autor_username != autor_username and user_role != 'admin':
            return Response({
                "error": "Acceso denegado",
                "message": "Solo el autor o un administrador puede modificar este mueble"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Actualizar solo los campos proporcionados
        if 'nombre' in data:
            mueble.nombre = data['nombre']
        if 'descripcion' in data:
            mueble.descripcion = data['descripcion']
        if 'altura' in data:
            mueble.altura = int(data['altura'])
        if 'ancho' in data:
            mueble.ancho = int(data['ancho'])
        if 'material' in data:
            mueble.material = data['material']
        if 'publicado' in data:
            mueble.publicado = data['publicado']
        
        mueble.save()
        
        return Response({
            "id": str(mueble.id),
            "message": "Mueble actualizado exitosamente",
            "nombre": mueble.nombre,
            "descripcion": mueble.descripcion,
            "altura": mueble.altura,
            "ancho": mueble.ancho,
            "material": mueble.material
        }, status=status.HTTP_200_OK)
    except FurnitureItem.DoesNotExist:
        return Response({
            "error": "Mueble no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": f"Error al actualizar mueble: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)


def delete_furniture(request, id: str) -> Response:
    """
    🪑 DELETE - Eliminar un mueble de MongoDB (requiere autenticación)
    
    Solo el autor o un administrador puede eliminar el mueble
    
    Ejemplo: DELETE /api/furniture/123/
    Headers: Authorization: Bearer <token>
    
    Args:
        request: Request HTTP con JWT token
        id: ID del mueble en MongoDB
        
    Returns:
        Response con mensaje de éxito o error 404
    """
    try:
        mueble: FurnitureItem = FurnitureItem.objects.get(id=id)
        
        # Verificar que el usuario autenticado sea el autor o admin
        autor_username: str = request.user_info['username']
        user_role: str = request.user_info['role']
        
        if mueble.autor_username != autor_username and user_role != 'admin':
            return Response({
                "error": "Acceso denegado",
                "message": "Solo el autor o un administrador puede eliminar este mueble"
            }, status=status.HTTP_403_FORBIDDEN)
        
        nombre: str = mueble.nombre
        mueble.delete()
        
        return Response({
            "message": f"Mueble '{nombre}' eliminado exitosamente"
        }, status=status.HTTP_200_OK)
    except FurnitureItem.DoesNotExist:
        return Response({
            "error": "Mueble no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@jwt_required
def list_furniture(request) -> Response:
    """
    🪑 GET - Listar todos los muebles publicados de MongoDB (requiere autenticación)
    
    Ejemplo: GET /api/furniture/
    Headers: Authorization: Bearer <token>
    
    Args:
        request: Request HTTP con JWT token
        
    Returns:
        Response con lista de muebles ordenados por fecha de creación
    """
    muebles = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    data: list[Dict[str, Any]] = [{
        "id": str(m.id),
        "nombre": m.nombre,
        "descripcion": m.descripcion,
        "altura": m.altura,
        "ancho": m.ancho,
        "material": m.material,
        "autor_username": m.autor_username,
        "fecha_creacion": m.fecha_creacion
    } for m in muebles]
    
    return Response({
        "count": len(data),
        "results": data
    }, status=status.HTTP_200_OK)
