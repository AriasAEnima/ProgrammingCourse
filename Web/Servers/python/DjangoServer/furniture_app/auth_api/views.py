"""
Vistas para autenticación JWT
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import User
from typing import Dict, Any


def create_tokens(user):
    """
    Crea tokens JWT para un usuario
    
    Returns:
        tuple: (access_token, refresh_token)
    """
    # Payload común
    common_payload = {
        'username': user.username,
        'role': user.role,
        'user_id': user.user_id
    }
    
    # Access Token (expira en 1 hora)
    access_payload = {
        **common_payload,
        'token_type': 'access',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    
    # Refresh Token (expira en 1 día)
    refresh_payload = {
        **common_payload,
        'token_type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    
    return access_token, refresh_token


@api_view(['POST'])
def login(request) -> Response:
    """
    🔐 POST - Login y obtención de JWT token
    
    Ejemplo: POST /api/auth/login/
    Body: {
        "username": "admin1",
        "password": "admin123"
    }
    
    Returns:
        Response con access_token, refresh_token e información del usuario
    """
    data: Dict[str, Any] = request.data
    
    # Validar campos requeridos
    if 'username' not in data or 'password' not in data:
        return Response({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    username: str = data['username']
    password: str = data['password']
    
    # Autenticar usuario
    user = User.authenticate(username, password)
    
    if user is None:
        return Response({
            'error': 'Credenciales inválidas',
            'message': 'Username o password incorrectos'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Crear tokens JWT
    access_token, refresh_token = create_tokens(user)
    
    return Response({
        'message': 'Login exitoso',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.user_id,
            'username': user.username,
            'role': user.role
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request) -> Response:
    """
    📝 POST - Registrar nuevo usuario
    
    Ejemplo: POST /api/auth/register/
    Body: {
        "username": "nuevo_usuario",
        "password": "password123",
        "role": "user"  // opcional, default: "user"
    }
    
    Returns:
        Response con información del usuario creado
    """
    data: Dict[str, Any] = request.data
    
    # Validar campos requeridos
    if 'username' not in data or 'password' not in data:
        return Response({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    username: str = data['username']
    password: str = data['password']
    role: str = data.get('role', 'user')
    
    # Validar que el rol sea válido
    if role not in ['admin', 'manager', 'user']:
        return Response({
            'error': 'Rol inválido',
            'message': 'El rol debe ser: admin, manager o user'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si el usuario ya existe
    try:
        existing_user = User.objects.get(username=username)
        return Response({
            'error': 'Usuario ya existe',
            'message': f'El username "{username}" ya está registrado'
        }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass
    
    try:
        # Generar user_id único
        last_user = User.objects.order_by('-user_id').first()
        if last_user and last_user.user_id.startswith('user-'):
            try:
                last_id = int(last_user.user_id.split('-')[1])
                new_user_id = f"user-{last_id + 1}"
            except:
                new_user_id = f"user-{User.objects.count() + 1}"
        else:
            new_user_id = f"user-{User.objects.count() + 1}"
        
        # Crear nuevo usuario
        user = User(
            user_id=new_user_id,
            username=username,
            role=role
        )
        user.set_password(password)
        user.save()
        
        return Response({
            'message': 'Usuario creado exitosamente',
            'user': {
                'id': user.user_id,
                'username': user.username,
                'role': user.role
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Error al crear usuario',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

