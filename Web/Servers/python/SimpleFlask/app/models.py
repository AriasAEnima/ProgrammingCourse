"""
Modelos y funciones de base de datos
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId

# Variables globales para la conexión
client = None
db = None
users_collection = None
desks_collection = None

def init_db(mongo_uri, database_name):
    """Inicializar conexión a MongoDB"""
    global client, db, users_collection, desks_collection
    
    try:
        client = MongoClient(mongo_uri)
        db = client[database_name]
        users_collection = db.users
        desks_collection = db.desks
        
        # Probar la conexión
        client.admin.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("⚠️  La aplicación requiere MongoDB para funcionar correctamente.")
        client = None
        db = None
        return False

def get_db_status():
    """Obtener estado de la conexión a MongoDB"""
    return db is not None

# ========== FUNCIONES DE USUARIOS ==========

def initialize_users():
    """Inicializar usuarios en MongoDB si no existen"""
    if db is None:
        return
    
    # Verificar si ya existen usuarios
    if users_collection.count_documents({}) == 0:
        users_data = [
            {
                'user_id': 'user-2',
                'username': 'manager',
                'password_hash': generate_password_hash('manager123'),
                'role': 'manager',
                'created_at': datetime.now()
            },
            {
                'user_id': 'user-1',
                'username': 'admin1',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'created_at': datetime.now()
            }
        ]
        users_collection.insert_many(users_data)
        print("✅ Usuarios iniciales creados en MongoDB")

def get_user_by_username(username):
    """Obtener usuario por username desde MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se puede autenticar usuarios.")
    
    return users_collection.find_one({"username": username})

def authenticate_user(username, password):
    """
    Autentica un usuario verificando sus credenciales
    
    Returns:
        tuple: (user_data, error_response, status_code)
        - Si es exitoso: (user_data, None, None)
        - Si hay error: (None, error_response, status_code)
    """
    try:
        user = get_user_by_username(username)
        print(user)
        if not user or not check_password_hash(user['password_hash'], password):
            return None, {
                'error': 'Credenciales inválidas',
                'message': 'Username o password incorrectos'
            }, 401
        
        return user, None, None
        
    except Exception as e:
        return None, {
            'error': 'Error de base de datos',
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }, 503

def get_user_count():
    """Obtener número total de usuarios"""
    if db is None:
        return 0
    return users_collection.count_documents({})

# ========== FUNCIONES DE ESCRITORIOS ==========

def initialize_desks():
    """Inicializar escritorios en MongoDB si no existen"""
    if db is None:
        return
    
    # Verificar si ya existen escritorios
    if desks_collection.count_documents({}) == 0:
        desks_data = [
            {"desk_id": 1, "name": "Mesa Venture", "width": 125, "height": 225},
            {"desk_id": 2, "name": "Mesa Koto", "width": 200, "height": 223},
            {"desk_id": 3, "name": "Mesa Amatista", "width": 200, "height": 300}
        ]
        desks_collection.insert_many(desks_data)
        print("✅ Escritorios iniciales creados en MongoDB")

def get_desk_by_id(desk_id):
    """Obtener escritorio por ID desde MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden consultar escritorios.")
    
    return desks_collection.find_one({"desk_id": int(desk_id)})

def get_all_desks_filtered(width_filter=None, height_filter=None):
    """Obtener todos los escritorios con filtros opcionales"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden consultar escritorios.")
    
    # Construir filtro para MongoDB
    filter_query = {}
    if width_filter:
        filter_query["width"] = {"$gte": int(width_filter)}
    if height_filter:
        filter_query["height"] = {"$gte": int(height_filter)}
    
    return list(desks_collection.find(filter_query))

def add_new_desk(desk_data):
    """Agregar nuevo escritorio a MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden crear escritorios.")
    
    # Obtener el próximo ID
    max_desk = desks_collection.find().sort("desk_id", -1).limit(1)
    next_id = 1
    for desk in max_desk:
        next_id = desk["desk_id"] + 1
        break
    
    new_desk = {
        "desk_id": next_id,
        "name": desk_data["name"],
        "width": desk_data["width"],
        "height": desk_data["height"]
    }
    
    result = desks_collection.insert_one(new_desk)
    new_desk["_id"] = result.inserted_id
    return new_desk

def get_desk_count():
    """Obtener número total de escritorios"""
    if db is None:
        return 0
    return desks_collection.count_documents({})

def get_all_desks():
    """Obtener todos los escritorios sin filtros"""
    if db is None:
        return []
    return list(desks_collection.find({}))