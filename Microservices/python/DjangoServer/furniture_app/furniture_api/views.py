from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dynamicpages.models import FurnitureItem

@api_view(['GET','DELETE'])
def handle_furniture(request, id):
    if  request.method == "GET":
        return get_furniture(request, id)
    else:
        return delete_furniture(request,id)
                
def get_furniture(request, id):
    """
    🪑 GET - Obtener un mueble por ID desde MongoDB
    
    Ejemplo: GET /api/furniture/123/
    """
    try:
        mueble = FurnitureItem.objects.get(id=id)
        
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
def post_furniture(request):
    """
    🪑 POST - Crear un nuevo mueble en MongoDB
    
    Ejemplo: POST /api/furniture/
    Body: {
        "nombre": "Mesa",
        "descripcion": "Mesa de comedor",
        "altura": 75,
        "ancho": 120,
        "material": "roble",
        "autor_username": "Juan"
    }
    """
    data = request.data
    
    # Validar campos requeridos
    required_fields = ['nombre', 'descripcion', 'altura', 'ancho', 'material']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return Response({
            "error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Crear mueble en MongoDB
        mueble = FurnitureItem(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            altura=int(data['altura']),
            ancho=int(data['ancho']),
            material=data['material'],
            autor_username=data.get('autor_username', 'Anónimo'),
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
def put_furniture(request, id):
    """
    🪑 PUT - Actualizar un mueble existente en MongoDB
    
    Ejemplo: PUT /api/furniture/123/update/
    Body: {"altura": 80, "ancho": 150}
    """
    try:
        mueble = FurnitureItem.objects.get(id=id)
        data = request.data
        
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


def delete_furniture(request, id):
    """
    🪑 DELETE - Eliminar un mueble de MongoDB
    
    Ejemplo: DELETE /api/furniture/123/
    """
    try:
        mueble = FurnitureItem.objects.get(id=id)
        nombre = mueble.nombre
        mueble.delete()
        
        return Response({
            "message": f"Mueble '{nombre}' eliminado exitosamente"
        }, status=status.HTTP_200_OK)
    except FurnitureItem.DoesNotExist:
        return Response({
            "error": "Mueble no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_furniture(request):
    """
    🪑 GET - Listar todos los muebles de MongoDB
    
    Ejemplo: GET /api/furniture/list/
    """
    muebles = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    data = [{
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
