from flask import Flask, request, jsonify, render_template_string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, create_access_token
from functools import wraps
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Obtener variables del entorno con valores por defecto
db_name = os.getenv('MONGO_DB')
host = os.getenv('MONGO_HOST')
port = int(os.getenv('MONGO_PORT',0))

print(f"Host is : {host} and database name is: {db_name}")

app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = os.getenv("JWT_ACCESS_TOKEN_EXPIRES")

try:
    client = MongoClient(str(host)+":"+str(port)+"/")
    db = client[db_name]
    users_collection = db.users
    desks_collection = db.desks
    
    # Probar la conexión
    client.admin.command('ping')
    print("✅ Conexión a MongoDB exitosa")
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    print("⚠️  La aplicación requiere MongoDB para funcionar correctamente.")
    client = None
    db = None



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

def get_current_user_role():
    """
    Obtiene el rol del usuario actual desde el JWT
    """
    try:
        claims = get_jwt()
        return claims.get('role', 'user')
    except:
        return None


def role_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_fn(*args, **kwargs):
        current_role = get_current_user_role()
        print(current_role)
        if current_role is None:
            return jsonify({
                'error': 'Permisos insuficientes',
                'message': f'Se requiere autenticación válida. Tu rol: {current_role}'
            }), 403
        return f(*args, **kwargs)
    return decorated_fn

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
            return None, jsonify({
                'error': 'Credenciales inválidas',
                'message': 'Username o password incorrectos'
            }), 401
        
        return user, None, None
        
    except Exception as e:
        return None, jsonify({
            'error': 'Error de base de datos',
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }), 503 

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
    
    # Autenticar usuario
    user, error_response, status_code = authenticate_user(username, password)
    if error_response:
        return error_response, status_code
    
    # Crear token JWT
    user_id = user.get('user_id') or user.get('id')  # Compatibilidad con ambos formatos
    access_token = create_access_token(
        identity=username,
        additional_claims={
            'role': user['role'],
            'user_id': user_id
        }
    )
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user_id,
            'username': user['username'],
            'role': user['role']
        }
    })

    
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
        
    print(f"Filter query : {filter_query}")
    
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
     
        


@app.route('/desk/<string:desk_id>/',methods = ["GET"])
@role_required
def get_desk(desk_id):
    try:
        desk = get_desk_by_id(desk_id)
        if desk:
            # Normalizar la respuesta para mantener compatibilidad
            if '_id' in desk:
                del desk['_id']  # Remover ObjectId de MongoDB
            if 'desk_id' in desk:
                desk['id'] = desk['desk_id']  # Mantener compatibilidad con 'id'
            return desk, 200
        else:
            print("ERROR")
            return {"mensaje": "Mesa no existe"}, 404
    except Exception as e:
        return jsonify({
            'error': 'Error de base de datos',
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }), 503
    
@app.route('/desk',methods = ["GET"])
@role_required
def get_all_desks():
   width_query_param= request.args.get("width")
   height_query_param= request.args.get("height")
   print(f"width {width_query_param}, height {height_query_param}")
   
   try:
       desks = get_all_desks_filtered(width_query_param, height_query_param)
       
       # Normalizar la respuesta para mantener compatibilidad
       result = []
       for desk in desks:
           desk_copy = desk.copy()
           if '_id' in desk_copy:
               del desk_copy['_id']  # Remover ObjectId de MongoDB
           if 'desk_id' in desk_copy:
               desk_copy['id'] = desk_copy['desk_id']  # Mantener compatibilidad con 'id'
           result.append(desk_copy)

       return result, 200
   except Exception as e:
       return jsonify({
           'error': 'Error de base de datos',
           'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
       }), 503

@app.route('/desk',methods = ["POST"])
@admin_required
def post_desk():
   print(f"Body: {request.json}")
   body = request.json
   
   # Validar datos requeridos
   if not all(key in body for key in ['name', 'width', 'height']):
       return jsonify({
           'error': 'Datos incompletos',
           'message': 'Se requieren name, width y height'
       }), 400
   
   try:
       new_desk_data = {
           "name": body["name"],
           "width": body["width"],
           "height": body["height"]
       }
       
       new_desk = add_new_desk(new_desk_data)
       
       # Normalizar respuesta
       if '_id' in new_desk:
           del new_desk['_id']
       if 'desk_id' in new_desk:
           new_desk['id'] = new_desk['desk_id']
       
       return new_desk, 201
   except Exception as e:
       return jsonify({
           'error': 'Error de base de datos',
           'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
       }), 503



@app.route('/shapes/status/500',methods = ["GET"])
def get_shapes_200():
    return "Hola ya no soy shapes" , 500

@app.route('/shapes/status/200',methods = ["GET"])
def get_shapes_500():
    return "Hola ya no soy shapes" , 200

@app.route('/shapes/<string:shape_id>/',methods = ["GET"])
def get_shapes(shape_id):
    if int(shape_id) % 2 == 0:
        return "Es par"
    else:
        return "Es impar"
    
@app.errorhandler(404)
def page_not_found(e):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bienvenido - Flask App</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                margin: 0; 
                padding: 50px; 
                min-height: 100vh; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
            }
            .card { 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                text-align: center; 
                max-width: 400px; 
            }
            h1 { 
                color: #333; 
                margin-bottom: 10px; 
            }
            p { 
                color: #666; 
                line-height: 1.6; 
            }
            .highlight { 
                background: #ff6b6b; 
                color: white; 
                padding: 5px 10px; 
                border-radius: 20px; 
                display: inline-block; 
                margin: 10px 0; 
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>404 Page not Found :( </h1>
            <p>Esta es una página HTML con estilos CSS servida desde Flask.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/welcome', methods=["GET"])
def welcome_page():
    """Ejemplo sencillo de página HTML con estilos"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bienvenido - Flask App</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                margin: 0; 
                padding: 50px; 
                min-height: 100vh; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
            }
            .card { 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                text-align: center; 
                max-width: 400px; 
            }
            h1 { 
                color: #333; 
                margin-bottom: 10px; 
            }
            p { 
                color: #666; 
                line-height: 1.6; 
            }
            .highlight { 
                background: #ff6b6b; 
                color: white; 
                padding: 5px 10px; 
                border-radius: 20px; 
                display: inline-block; 
                margin: 10px 0; 
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎉 ¡Bienvenido!</h1>
            <p>Esta es una página HTML con estilos CSS servida desde Flask.</p>
            <div class="highlight">{{ current_time }}</div>
            <p>✨ MongoDB está <strong>{{ db_status }}</strong></p>
        </div>
    </body>
    </html>
    """
    
    # Determinar estado de la base de datos
    db_status_value = "conectado" if db is not None else "desconectado"
    current_time_value = datetime.now().strftime("%H:%M:%S")
    
    return render_template_string(html_content, 
                                db_status=db_status_value, 
                                current_time=current_time_value)
    

if __name__ == '__main__':
    # Inicializar datos en MongoDB si está disponible
    initialize_users()
    initialize_desks()
    
    app.run(
        host= '0.0.0.0',
        port= 8003,
        debug = True
    )