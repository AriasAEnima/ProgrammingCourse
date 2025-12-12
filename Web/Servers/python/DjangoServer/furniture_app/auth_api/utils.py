"""
Utilidades para autenticación JWT en Django
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings


def get_user_from_token(request):
    """
    Extrae y autentica el usuario desde el token JWT
    
    Returns:
        tuple: (username, role, user_id) o (None, None, None) si falla
    """
    try:
        # Obtener el header Authorization
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None, None, None
        
        # Extraer el token
        token = auth_header.split(' ')[1]
        
        # Decodificar el token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Extraer información del token
        username = payload.get('username')
        role = payload.get('role', 'user')
        user_id = payload.get('user_id')
        
        return username, role, user_id
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, IndexError):
        return None, None, None


def jwt_required(f):
    """
    Decorator que requiere autenticación JWT válida
    
    Uso:
        @api_view(['GET'])
        @jwt_required
        def my_view(request):
            # request.user_info contiene (username, role, user_id)
            pass
    """
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        username, role, user_id = get_user_from_token(request)
        
        if username is None:
            return Response({
                'error': 'Token inválido o expirado',
                'message': 'Se requiere autenticación válida'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Adjuntar información del usuario al request
        request.user_info = {
            'username': username,
            'role': role,
            'user_id': user_id
        }
        
        return f(request, *args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    Decorator que requiere rol de administrador
    
    Uso:
        @api_view(['POST'])
        @admin_required
        def admin_only_view(request):
            pass
    """
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        username, role, user_id = get_user_from_token(request)
        
        if username is None:
            return Response({
                'error': 'Token inválido o expirado',
                'message': 'Se requiere autenticación válida'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if role != 'admin':
            return Response({
                'error': 'Acceso denegado',
                'message': 'Solo los administradores pueden acceder a este endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Adjuntar información del usuario al request
        request.user_info = {
            'username': username,
            'role': role,
            'user_id': user_id
        }
        
        return f(request, *args, **kwargs)
    
    return decorated_function


def role_required(f):
    """
    Decorator que requiere autenticación JWT (cualquier rol autenticado)
    Alias de jwt_required para compatibilidad
    """
    return jwt_required(f)

