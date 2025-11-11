
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import uuid
import websockets
import asyncio
import json
import threading
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración JWT
app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'  # ¡Cambiar en producción!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# =============================================================================
# FUNCIONES DE VERIFICACIÓN DE ROLES
# =============================================================================

def get_current_user_role():
    """
    Obtiene el rol del usuario actual desde el JWT
    """
    try:
        claims = get_jwt()
        return claims.get('role', 'user')
    except:
        return None

def get_current_user_data():
    """
    Obtiene todos los datos del usuario actual desde el JWT
    """
    try:
        username = get_jwt_identity()
        claims = get_jwt()
        return {
            'username': username,
            'role': claims.get('role', 'user'),
            'user_id': claims.get('user_id')
        }
    except:
        return None

def role_required(required_roles):
    """
    Decorator para verificar que el usuario tenga uno de los roles requeridos
    
    Args:
        required_roles (str or list): Rol requerido o lista de roles permitidos
    
    Usage:
        @role_required('admin')
        @role_required(['admin', 'manager'])
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_role = get_current_user_role()
            
            if current_role not in required_roles:
                return jsonify({
                    'error': 'Permisos insuficientes',
                    'message': f'Se requiere uno de estos roles: {", ".join(required_roles)}. Tu rol: {current_role}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator específico para endpoints que solo pueden acceder administradores
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_role = get_current_user_role()
        
        if current_role != 'admin':
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'Solo los administradores pueden acceder a este endpoint'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def manager_or_admin_required(f):
    """
    Decorator para endpoints que pueden acceder managers y administradores
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_role = get_current_user_role()
        
        if current_role not in ['manager', 'admin']:
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'Se requiere rol de manager o admin'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Configuración WebSocket
WEBSOCKET_URL = "ws://localhost:8765"

def send_websocket_message(message_data):
    """
    Envía un mensaje al servidor WebSocket de forma asíncrona
    Utiliza threading para no bloquear la aplicación Flask
    """
    def _send_message():
        try:
            # Ejecutar el envío de mensaje WebSocket
            asyncio.run(_async_send_message(message_data))
        except Exception as e:
            print(f"❌ Error enviando mensaje WebSocket: {e}")
    
    # Ejecutar en un hilo separado para no bloquear Flask
    thread = threading.Thread(target=_send_message)
    thread.daemon = True
    thread.start()

async def _async_send_message(message_data):
    """Función asíncrona para enviar mensaje WebSocket"""
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            await websocket.send(json.dumps(message_data))
    except Exception as e:
        print(f"❌ Error conectando con WebSocket server: {e}")
        print("💡 Asegúrate de que el servidor WebSocket esté ejecutándose en ws://localhost:8765")

# Base de datos simulada en memoria para el ejemplo
# En producción usarías una base de datos real
restaurantes = [
    {
        'id': '1',
        'nombre': 'La Pizzería Italiana',
        'tipo_cocina': 'Italiana',
        'direccion': 'Calle Principal 123',
        'telefono': '+1-555-0123',
        'calificacion': 4.5,
        'precio_promedio': 25.50,
        'delivery': True,
        'created_at': '2024-01-15T10:00:00Z'
    },
    {
        'id': '2', 
        'nombre': 'Sushi Tokyo',
        'tipo_cocina': 'Japonesa',
        'direccion': 'Avenida Central 456',
        'telefono': '+1-555-0456',
        'calificacion': 4.8,
        'precio_promedio': 45.00,
        'delivery': False,
        'created_at': '2024-01-15T11:00:00Z'
    },
    {
        'id': '3',
        'nombre': 'Tacos El Patrón',
        'tipo_cocina': 'Mexicana',
        'direccion': 'Plaza Mayor 789',
        'telefono': '+1-555-0789',
        'calificacion': 4.2,
        'precio_promedio': 18.75,
        'delivery': True,
        'created_at': '2024-01-15T12:00:00Z'
    }
]

# Base de datos simulada de usuarios para autenticación
users = {
    'admin': {
        'id': 'user-1',
        'username': 'admin',
        'password_hash': generate_password_hash('admin123'),  # Password: admin123
        'role': 'admin',
        'created_at': '2024-01-15T10:00:00Z'
    },
    'manager': {
        'id': 'user-2', 
        'username': 'manager',
        'password_hash': generate_password_hash('manager123'),  # Password: manager123
        'role': 'manager',
        'created_at': '2024-01-15T11:00:00Z'
    },
    'user': {
        'id': 'user-3',
        'username': 'user',
        'password_hash': generate_password_hash('user123'),  # Password: user123
        'role': 'user',
        'created_at': '2024-01-15T12:00:00Z'
    }
}

# Ruta principal - Información de la API
@app.route('/')
def index():
    """
    Endpoint principal que muestra información sobre la API
    """
    return jsonify({
        'message': 'Bienvenido a la API de Restaurantes con Flask',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'Información de la API',
            'POST /auth/login': 'Iniciar sesión (obtener JWT token)',
            'POST /auth/register': 'Registrar nuevo usuario',
            'GET /auth/profile': 'Obtener perfil del usuario autenticado',
            'GET /auth/whoami': 'Verificar datos y permisos del usuario actual',
            'GET /api/restaurantes': 'Obtener todos los restaurantes (con filtros)',
            'GET /api/restaurantes/<id>': 'Obtener un restaurante específico',
            'POST /api/restaurantes': 'Crear nuevo restaurante [Auth requerida]',
            'PUT /api/restaurantes/<id>': 'Actualizar restaurante completo [Auth requerida]',
            'PATCH /api/restaurantes/<id>': 'Actualizar parcialmente un restaurante [Auth requerida]',
            'DELETE /api/restaurantes/<id>': 'Eliminar un restaurante [Admin requerido]'
        },
        'autenticacion': {
            'tipo': 'JWT (JSON Web Token)',
            'duracion': '1 hora',
            'header': 'Authorization: Bearer <token>',
            'usuarios_demo': {
                'admin': 'admin123 (puede crear, editar, eliminar)',
                'manager': 'manager123 (puede crear, editar)',
                'user': 'user123 (solo lectura)'
            }
        },
        'filtros_disponibles': {
            'tipo_cocina': 'Filtrar por tipos de cocina (array separado por comas, ej: Italiana,Japonesa)',
            'calificacion_min': 'Calificación mínima (ej: 4.0)',
            'precio_max': 'Precio máximo promedio',
            'delivery': 'true/false para filtrar por disponibilidad de delivery',
            'nombre': 'Buscar por nombre (búsqueda parcial)'
        }
    })

# GET /api/restaurantes - Obtener todos los restaurantes
@app.route('/api/restaurantes', methods=['GET'])
def get_restaurantes():
    """
    Obtiene todos los restaurantes.
    Soporta múltiples filtros mediante query parameters.
    
    Query parameters:
odiram    - tipo_cocina: Filtrar por tipos de cocina (array separado por comas, ej: Italiana,Japonesa,Mexicana)
    - calificacion_min: Calificación mínima (ej: 4.0)
    - precio_max: Precio máximo promedio (ej: 30.0)
    - delivery: true/false para filtrar por disponibilidad de delivery
    - nombre: Buscar por nombre (búsqueda parcial, insensible a mayúsculas)
    """
    filtered_restaurantes = restaurantes.copy()
    
    # Filtro por tipo de cocina (array separado por comas) - Enfoque funcional
    tipo_cocina = request.args.get('tipo_cocina')
    if tipo_cocina:
        # Dividir por comas, limpiar espacios y filtrar elementos vacíos
        tipos_cocina = list(filter(None, map(str.strip, tipo_cocina.split(','))))
        # Convertir a minúsculas para comparación insensible a mayúsculas
        tipos_cocina_lower = list(map(str.lower, tipos_cocina))
        # Filtrar restaurantes usando filter()
        filtered_restaurantes = list(filter(
            lambda r: r['tipo_cocina'].lower() in tipos_cocina_lower, 
            filtered_restaurantes
        ))
    
    # Filtro por calificación mínima - Enfoque funcional
    calificacion_min = request.args.get('calificacion_min')
    if calificacion_min:
        try:
            cal_min = float(calificacion_min)
            filtered_restaurantes = list(filter(
                lambda r: r['calificacion'] >= cal_min, 
                filtered_restaurantes
            ))
        except ValueError:
            return jsonify({
                'error': 'Parámetro inválido',
                'message': 'calificacion_min debe ser un número válido'
            }), 400
    
    # Filtro por precio máximo - Enfoque funcional
    precio_max = request.args.get('precio_max')
    if precio_max:
        try:
            precio_max_val = float(precio_max)
            filtered_restaurantes = list(filter(
                lambda r: r['precio_promedio'] <= precio_max_val, 
                filtered_restaurantes
            ))
        except ValueError:
            return jsonify({
                'error': 'Parámetro inválido',
                'message': 'precio_max debe ser un número válido'
            }), 400
    
    # Filtro por delivery - Enfoque funcional
    delivery_filter = request.args.get('delivery')
    if delivery_filter is not None:
        delivery_bool = delivery_filter.lower() == 'true'
        filtered_restaurantes = list(filter(
            lambda r: r['delivery'] == delivery_bool, 
            filtered_restaurantes
        ))
    
    # Filtro por nombre (búsqueda parcial) - Enfoque funcional
    nombre_filter = request.args.get('nombre')
    if nombre_filter:
        filtered_restaurantes = list(filter(
            lambda r: nombre_filter.lower() in r['nombre'].lower(), 
            filtered_restaurantes
        ))
    
    return jsonify({
        'restaurantes': filtered_restaurantes,
        'total': len(filtered_restaurantes),
        'filtros_aplicados': dict(request.args)
    })

# GET /api/restaurantes/<id> - Obtener restaurante específico
@app.route('/api/restaurantes/<string:restaurant_id>', methods=['GET'])
def get_restaurante(restaurant_id):
    """
    Obtiene un restaurante específico por su ID
    """
    restaurant = next((r for r in restaurantes if r['id'] == restaurant_id), None)
    
    if restaurant is None:
        return jsonify({
            'error': 'Restaurante no encontrado',
            'message': f'No existe un restaurante con ID: {restaurant_id}'
        }), 404
    
    return jsonify(restaurant)

# POST /api/restaurantes - Crear nuevo restaurante
@app.route('/api/restaurantes', methods=['POST'])
@manager_or_admin_required
def create_restaurante():
    """
    Crea un nuevo restaurante
    
    Body JSON requerido:
    {
        "nombre": "string",
        "tipo_cocina": "string",
        "direccion": "string",
        "telefono": "string",
        "calificacion": float,
        "precio_promedio": float,
        "delivery": boolean
    }
    """
    required_fields = ['nombre', 'tipo_cocina', 'direccion', 'telefono', 'calificacion', 'precio_promedio']
    
    if not request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requiere JSON en el body'
        }), 400
    
    # Validar campos requeridos
    for field in required_fields:
        if field not in request.json:
            return jsonify({
                'error': 'Datos inválidos',
                'message': f'El campo {field} es requerido'
            }), 400
    
    # Validar tipos de datos
    try:
        calificacion = float(request.json['calificacion'])
        precio_promedio = float(request.json['precio_promedio'])
        
        if not (0 <= calificacion <= 5):
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'La calificación debe estar entre 0 y 5'
            }), 400
            
        if precio_promedio < 0:
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'El precio promedio debe ser mayor a 0'
            }), 400
            
    except ValueError:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'calificacion y precio_promedio deben ser números'
        }), 400
    
    # Crear nuevo restaurante
    new_restaurant = {
        'id': str(uuid.uuid4()),  # Generar ID único
        'nombre': request.json['nombre'],
        'tipo_cocina': request.json['tipo_cocina'],
        'direccion': request.json['direccion'],
        'telefono': request.json['telefono'],
        'calificacion': calificacion,
        'precio_promedio': precio_promedio,
        'delivery': request.json.get('delivery', False),
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    restaurantes.append(new_restaurant)
    
    # Enviar notificación WebSocket de nuevo restaurante creado
    websocket_message = {
        "type": "restaurant_created",
        "restaurant": new_restaurant,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    send_websocket_message(websocket_message)
    
    return jsonify({
        'message': 'Restaurante creado exitosamente',
        'restaurant': new_restaurant
    }), 201

# PUT /api/restaurantes/<id> - Actualizar restaurante completo
@app.route('/api/restaurantes/<string:restaurant_id>', methods=['PUT'])
@manager_or_admin_required
def update_restaurante(restaurant_id):
    """
    Actualiza un restaurante completo (reemplaza todos los campos)
    
    Body JSON requerido:
    {
        "nombre": "string",
        "tipo_cocina": "string",
        "direccion": "string",
        "telefono": "string",
        "calificacion": float,
        "precio_promedio": float,
        "delivery": boolean
    }
    """
    restaurant = next((r for r in restaurantes if r['id'] == restaurant_id), None)
    
    if restaurant is None:
        return jsonify({
            'error': 'Restaurante no encontrado',
            'message': f'No existe un restaurante con ID: {restaurant_id}'
        }), 404
    
    if not request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requiere JSON en el body'
        }), 400
    
    # Validar y actualizar todos los campos
    restaurant['nombre'] = request.json.get('nombre', restaurant['nombre'])
    restaurant['tipo_cocina'] = request.json.get('tipo_cocina', restaurant['tipo_cocina'])
    restaurant['direccion'] = request.json.get('direccion', restaurant['direccion'])
    restaurant['telefono'] = request.json.get('telefono', restaurant['telefono'])
    restaurant['delivery'] = request.json.get('delivery', restaurant['delivery'])
    
    # Validar y actualizar campos numéricos
    if 'calificacion' in request.json:
        try:
            cal = float(request.json['calificacion'])
            if 0 <= cal <= 5:
                restaurant['calificacion'] = cal
            else:
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'La calificación debe estar entre 0 y 5'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'La calificación debe ser un número'
            }), 400
    
    if 'precio_promedio' in request.json:
        try:
            precio = float(request.json['precio_promedio'])
            if precio >= 0:
                restaurant['precio_promedio'] = precio
            else:
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'El precio promedio debe ser mayor a 0'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'El precio promedio debe ser un número'
            }), 400
    
    # Enviar notificación WebSocket de restaurante actualizado
    websocket_message = {
        "type": "restaurant_updated",
        "restaurant": restaurant,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    send_websocket_message(websocket_message)
    
    return jsonify({
        'message': 'Restaurante actualizado exitosamente',
        'restaurant': restaurant
    })

# PATCH /api/restaurantes/<id> - Actualización parcial
@app.route('/api/restaurantes/<string:restaurant_id>', methods=['PATCH'])
@manager_or_admin_required
def patch_restaurante(restaurant_id):
    """
    Actualiza parcialmente un restaurante (solo los campos enviados)
    
    Body JSON (todos los campos son opcionales):
    {
        "nombre": "string",
        "tipo_cocina": "string",
        "direccion": "string",
        "telefono": "string",
        "calificacion": float,
        "precio_promedio": float,
        "delivery": boolean
    }
    """
    restaurant = next((r for r in restaurantes if r['id'] == restaurant_id), None)
    
    if restaurant is None:
        return jsonify({
            'error': 'Restaurante no encontrado',
            'message': f'No existe un restaurante con ID: {restaurant_id}'
        }), 404
    
    if not request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requiere JSON en el body'
        }), 400
    
    # Actualizar solo los campos proporcionados
    if 'nombre' in request.json:
        restaurant['nombre'] = request.json['nombre']
    if 'tipo_cocina' in request.json:
        restaurant['tipo_cocina'] = request.json['tipo_cocina']
    if 'direccion' in request.json:
        restaurant['direccion'] = request.json['direccion']
    if 'telefono' in request.json:
        restaurant['telefono'] = request.json['telefono']
    if 'delivery' in request.json:
        restaurant['delivery'] = request.json['delivery']
    
    # Validar y actualizar campos numéricos
    if 'calificacion' in request.json:
        try:
            cal = float(request.json['calificacion'])
            if 0 <= cal <= 5:
                restaurant['calificacion'] = cal
            else:
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'La calificación debe estar entre 0 y 5'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'La calificación debe ser un número'
            }), 400
    
    if 'precio_promedio' in request.json:
        try:
            precio = float(request.json['precio_promedio'])
            if precio >= 0:
                restaurant['precio_promedio'] = precio
            else:
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'El precio promedio debe ser mayor a 0'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'El precio promedio debe ser un número'
            }), 400
    
    # Enviar notificación WebSocket de restaurante actualizado
    websocket_message = {
        "type": "restaurant_updated",
        "restaurant": restaurant,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    send_websocket_message(websocket_message)
    
    return jsonify({
        'message': 'Restaurante actualizado parcialmente',
        'restaurant': restaurant
    })

# DELETE /api/restaurantes/<id> - Eliminar restaurante
@app.route('/api/restaurantes/<string:restaurant_id>', methods=['DELETE'])
@admin_required
def delete_restaurante(restaurant_id):
    """
    Elimina un restaurante específico
    """
    global restaurantes
    restaurant = next((r for r in restaurantes if r['id'] == restaurant_id), None)
    
    if restaurant is None:
        return jsonify({
            'error': 'Restaurante no encontrado',
            'message': f'No existe un restaurante con ID: {restaurant_id}'
        }), 404
    
    restaurantes = [r for r in restaurantes if r['id'] != restaurant_id]
    
    # Enviar notificación WebSocket de restaurante eliminado
    websocket_message = {
        "type": "restaurant_deleted",
        "restaurant": restaurant,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    send_websocket_message(websocket_message)
    
    return jsonify({
        'message': 'Restaurante eliminado exitosamente',
        'deleted_restaurant': restaurant
    })

# GET /api/restaurantes/<id>/details - Ejemplo combinando PATH y QUERY parameters
@app.route('/api/restaurantes/<string:restaurant_id>/details', methods=['GET'])
def get_restaurante_details(restaurant_id):
    """
    Obtiene detalles de un restaurante específico con opciones de personalización.
    
    PATH PARAMETER:
    - restaurant_id: ID del restaurante a obtener
    
    QUERY PARAMETERS:
    - include_metadata: true/false - incluir metadatos (default: false)
    - format: json/summary/full - formato de respuesta (default: json)
    - lang: es/en - idioma de los mensajes (default: es)
    - fields: nombre,tipo_cocina,calificacion - campos específicos a incluir
    
    Ejemplo: /api/restaurantes/1/details?include_metadata=true&format=full&lang=en&fields=nombre,calificacion
    """
    # Buscar el restaurante (PATH PARAMETER)
    restaurant = next((r for r in restaurantes if r['id'] == restaurant_id), None)
    
    if restaurant is None:
        return jsonify({
            'error': 'Restaurante no encontrado',
            'message': f'No existe un restaurante con ID: {restaurant_id}'
        }), 404
    
    # Procesar QUERY PARAMETERS
    include_metadata = request.args.get('include_metadata', 'false').lower() == 'true'
    format_type = request.args.get('format', 'json').lower()
    language = request.args.get('lang', 'es').lower()
    fields = request.args.get('fields', '').split(',') if request.args.get('fields') else []
    
    # Validar formato
    if format_type not in ['json', 'summary', 'full']:
        return jsonify({
            'error': 'Formato inválido',
            'message': 'Los formatos válidos son: json, summary, full'
        }), 400
    
    # Construir respuesta base
    response_data = restaurant.copy()
    
    # Filtrar campos específicos si se solicita
    if fields and fields != ['']:
        filtered_restaurant = {}
        valid_fields = ['id', 'nombre', 'tipo_cocina', 'direccion', 'telefono', 'calificacion', 'precio_promedio', 'delivery', 'created_at']
        
        for field in fields:
            field = field.strip()
            if field in valid_fields:
                filtered_restaurant[field] = restaurant.get(field)
        
        response_data = filtered_restaurant
    
    # Agregar metadatos si se solicita
    if include_metadata:
        response_data['metadata'] = {
            'request_timestamp': datetime.utcnow().isoformat() + 'Z',
            'restaurant_age_days': (datetime.utcnow() - datetime.fromisoformat(restaurant['created_at'].replace('Z', ''))).days,
            'path_parameter': restaurant_id,
            'query_parameters': dict(request.args),
            'endpoint': f'/api/restaurantes/{restaurant_id}/details'
        }
    
    # Diferentes formatos de respuesta
    if format_type == 'summary':
        delivery_status = '🚚 Con delivery' if restaurant['delivery'] else '🏪 Solo local'
        messages = {
            'es': {
                'summary': f"Restaurante '{restaurant['nombre']}' - {restaurant['tipo_cocina']} ⭐ {restaurant['calificacion']}",
                'details': f"💰 ${restaurant['precio_promedio']} promedio | {delivery_status} | Creado: {restaurant['created_at'][:10]}"
            },
            'en': {
                'summary': f"Restaurant '{restaurant['nombre']}' - {restaurant['tipo_cocina']} ⭐ {restaurant['calificacion']}",
                'details': f"💰 ${restaurant['precio_promedio']} average | {delivery_status} | Created: {restaurant['created_at'][:10]}"
            }
        }
        
        lang_messages = messages.get(language, messages['es'])
        return jsonify({
            'restaurant_id': restaurant_id,
            'summary': lang_messages['summary'],
            'details': lang_messages['details'],
            'format': 'summary'
        })
    
    elif format_type == 'full':
        # Análisis completo del restaurante
        created_date = datetime.fromisoformat(restaurant['created_at'].replace('Z', ''))
        age_days = (datetime.utcnow() - created_date).days
        
        # Categorización por precio
        if restaurant['precio_promedio'] <= 15:
            price_category = 'Económico ($)'
        elif restaurant['precio_promedio'] <= 35:
            price_category = 'Moderado ($$)'
        else:
            price_category = 'Premium ($$$)'
        
        # Categorización por calificación
        if restaurant['calificacion'] >= 4.5:
            rating_category = 'Excelente'
        elif restaurant['calificacion'] >= 4.0:
            rating_category = 'Muy bueno'
        elif restaurant['calificacion'] >= 3.5:
            rating_category = 'Bueno'
        else:
            rating_category = 'Regular'
        
        analysis = {
            'basic_info': response_data,
            'analysis': {
                'price_category': price_category,
                'rating_category': rating_category,
                'cuisine_type': restaurant['tipo_cocina'],
                'delivery_available': restaurant['delivery'],
                'age_days': age_days,
                'status_emoji': '⭐' * int(restaurant['calificacion']),
                'recommendation': 'Altamente recomendado' if restaurant['calificacion'] >= 4.0 and restaurant['precio_promedio'] <= 30 else 'Recomendado'
            },
            'request_info': {
                'path_param_received': restaurant_id,
                'query_params_received': dict(request.args),
                'total_query_params': len(request.args)
            }
        }
        
        return jsonify(analysis)
    
    # Formato JSON por defecto
    return jsonify({
        'restaurant': response_data,
        'request_info': {
            'path_parameter': restaurant_id,
            'query_parameters': dict(request.args),
            'format': format_type
        }
    })

# =============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# =============================================================================

@app.route('/auth/login', methods=['POST'])
def login():
    """
    Endpoint para iniciar sesión y obtener JWT token
    
    Body JSON requerido:
    {
        "username": "string",
        "password": "string"
    }
    """
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }), 400
    
    username = request.json['username']
    password = request.json['password']
    
    # Verificar si el usuario existe
    user = users.get(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({
            'error': 'Credenciales inválidas',
            'message': 'Username o password incorrectos'
        }), 401
    
    # Crear token JWT
    access_token = create_access_token(
        identity=username,
        additional_claims={
            'role': user['role'],
            'user_id': user['id']
        }
    )
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })

@app.route('/auth/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario
    
    Body JSON requerido:
    {
        "username": "string",
        "password": "string",
        "role": "user" (opcional, default: "user")
    }
    """
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }), 400
    
    username = request.json['username']
    password = request.json['password']
    role = request.json.get('role', 'user')
    
    # Validar que el username no exista
    if username in users:
        return jsonify({
            'error': 'Usuario ya existe',
            'message': f'El username {username} ya está registrado'
        }), 400
    
    # Validar rol
    valid_roles = ['user', 'manager', 'admin']
    if role not in valid_roles:
        return jsonify({
            'error': 'Rol inválido',
            'message': f'El rol debe ser uno de: {", ".join(valid_roles)}'
        }), 400
    
    # Crear nuevo usuario
    new_user = {
        'id': str(uuid.uuid4()),
        'username': username,
        'password_hash': generate_password_hash(password),
        'role': role,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    users[username] = new_user
    
    return jsonify({
        'message': 'Usuario creado exitosamente',
        'user': {
            'id': new_user['id'],
            'username': new_user['username'],
            'role': new_user['role']
        }
    }), 201

@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Endpoint para obtener el perfil del usuario autenticado
    Requiere JWT token en el header Authorization
    """
    current_username = get_jwt_identity()
    user = users.get(current_username)
    
    if not user:
        return jsonify({
            'error': 'Usuario no encontrado',
            'message': 'El usuario autenticado no existe'
        }), 404
    
    # Determinar permisos basados en el rol
    permissions = {
        'admin': ['read', 'create', 'update', 'delete'],
        'manager': ['read', 'create', 'update'],
        'user': ['read']
    }
    
    user_permissions = permissions.get(user['role'], ['read'])
    
    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'created_at': user['created_at'],
            'permissions': user_permissions
        }
    })

@app.route('/auth/whoami', methods=['GET'])
@jwt_required()
def whoami():
    """
    Endpoint rápido para verificar datos del usuario actual desde JWT
    """
    user_data = get_current_user_data()
    
    return jsonify({
        'current_user': user_data,
        'jwt_claims': get_jwt(),
        'can_create': user_data['role'] in ['manager', 'admin'],
        'can_update': user_data['role'] in ['manager', 'admin'],
        'can_delete': user_data['role'] == 'admin'
    })

# Manejo de errores globales
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Recurso no encontrado',
        'message': 'El endpoint solicitado no existe'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ocurrió un error inesperado'
    }), 500

# Manejo de errores JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token expirado',
        'message': 'El token JWT ha expirado. Por favor inicia sesión nuevamente.'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'Token inválido',
        'message': 'El token JWT no es válido.'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'Token requerido',
        'message': 'Se requiere un token JWT válido para acceder a este endpoint.'
    }), 401

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask API...")
    print("🍕 API de Restaurantes con JWT disponible en: http://localhost:8001")
    print("📚 Documentación disponible en: http://localhost:8001")
    print("🔐 Autenticación JWT habilitada:")
    print("   POST /auth/login - Obtener token")
    print("   POST /auth/register - Registrar usuario")
    print("   GET /auth/profile - Ver perfil (requiere token)")
    print("🔍 Endpoints principales:")
    print("   GET /api/restaurantes - Listar restaurantes (público)")
    print("   POST /api/restaurantes - Crear restaurante (requiere auth)")
    print("👥 Usuarios demo: admin:admin123, manager:manager123, user:user123")
    
    # Ejecutar en modo desarrollo
    app.run(
        host='0.0.0.0',  # Permitir conexiones externas
        port=8001,       # Puerto libre
        debug=False      # Sin debug para evitar reinicios automáticos
    )
