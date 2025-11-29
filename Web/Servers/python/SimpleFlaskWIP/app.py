import os
from flask import Flask, request, jsonify, render_template_string
from datetime import timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
from functools import wraps
from flask_jwt_extended import create_access_token, JWTManager, jwt_required,get_jwt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
app = Flask(__name__)

app_name = {"spanish": "muebles",
            "english": "forniture"}

app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)
host = 'mongodb://localhost'
port = 27017
db_name = 'furniture_database'
forniture_collection = None

def connect_db():
    try:
        client = MongoClient(str(host)+":"+str(port)+"/")
        db = client[db_name]
        global forniture_collection
        forniture_collection = db.forniture        
        # Probar la conexión
        client.admin.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        print(f"✅ DB check {forniture_collection !=None}")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("⚠️  La aplicación requiere MongoDB para funcionar correctamente.")
        client = None
        db = None

def get_current_user_role():
    try:
        claims = get_jwt()
        return claims.get('role','user')
    except:
        return None

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def our_decorated_function(*args,**kwargs):
        current_role = get_current_user_role()
        if current_role != 'admin':
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'Solo los administradores pueden acceder a este endpoint'
                }), 403
        return f(*args,**kwargs)
    return our_decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def check_roles(*args, **kwargs):
            current_role = get_current_user_role()
            print(f"current_role {current_role}")    
            if current_role not in roles:
                return jsonify({
                    'error': 'Acceso denegado',
                    'message': 'Solo ciertos roles pueden acceder a este endpoint'
                    }), 403
            return f(*args, **kwargs)
        return check_roles
    return decorator

@app.route('/')
def home():
    language = request.args.get("language","english")
    return "<h1> Home app "+app_name[language] + "</h1>" 

## REST ENDPOINTS

@app.route('/api/furniture/<string:id>/',methods = ["GET"])
@jwt_required()
def get_furniture(id):   
    found =  forniture_collection.find_one({"_id": ObjectId(id)})
    if found is not None :
        found["_id"] = str(found["_id"])
        return found, 200
    else:
        return {"messsage": "forniture with "+id+" not found"}, 404
    
@app.route('/api/furniture/<string:id>/',methods = ["DELETE"])
@role_required(["admin", "manager"])
def del_furniture(id):   
    found =  forniture_collection.find_one({"_id": ObjectId(id)})
    if found is None:
        return {},208
    else:
        result = forniture_collection.delete_one({"_id": ObjectId(id)})
        return {},200
    
def get_all_furnitures_filtered(width_filter = None, height_filter = None):
    filter_query = {}
    if width_filter:
        filter_query["width"] = {"$gte": int(width_filter)}
    if height_filter:
        filter_query["height"] = {"$gte": int(height_filter)}
        
    print(f"Filter query : {filter_query}")
    
    return list(forniture_collection.find(filter_query))

def normalize_id(item):
    item["_id"] = str(item["_id"])
    return item

@app.route('/api/furnitures/')
@jwt_required()
def get_furnitures(): 
    width = request.args.get("width",0)
    height =  request.args.get("height",0)      
    result =  get_all_furnitures_filtered(width,height )
    results = list(map( lambda fur : normalize_id(fur), result))
    return results , 200

def add_new_forniture(data):   
    new_forniture = {
        "name": data["name"],
        "width": data["width"],
        "height": data["height"],
        "depth": data["depth"],
        "price": data["price"]
    }
    global forniture_collection
    result = forniture_collection.insert_one(new_forniture)
    print("Insert exitoso")
    new_forniture["_id"] = str(result.inserted_id)
    return new_forniture


@app.route('/api/furniture/', methods = ["POST"])
@admin_required
def post_furniture(): 
    if not request.json or \
        'name' not in request.json or \
        'width' not in request.json or \
        'height' not in request.json or \
        'depth' not in request.json or \
        'price' not in request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }), 400
    body = request.json
    return add_new_forniture(body), 201
    
@app.route('/api/furniture/<string:id>/', methods=["PUT"])
@admin_required
def put_furniture(id):
    body = request.json
    price = body.get("price")
    name = body.get("name")
    found =  forniture_collection.find_one({"_id": ObjectId(id)})
    query_update =  { "$set": {}}

    if found is not None:
        if price != None:
            query_update["$set"]["price"] = price
        if name != None:
            query_update["$set"]["name"] = name  
        print(f"Update query {query_update}")
        result = forniture_collection.update_one({"_id": ObjectId(id)}, query_update )      
        found =  forniture_collection.find_one({"_id": ObjectId(id)})
        found["_id"] = str(found["_id"])
        return found,200
    else:
        return {"messsage": "forniture with "+id+" not found"}, 404
         
users = [
            {
                'user_id': 'user-1',
                'username': 'user-admin',
                'role': 'admin',
                'password_hash': generate_password_hash('user-admin-123'),
                'created_at': datetime.now()
            },
               {
                'user_id': 'user-1',
                'username': 'user-manager',
                'role': 'manager',
                'password_hash': generate_password_hash('user-mager-123'),
                'created_at': datetime.now()
            },
        ]

def get_users_by_username(username):
    return list(filter(lambda u: u["username"]== username, users))

def authenticate_user(username, password):
    users  = get_users_by_username(username)
    print(f"users found: {users}, with username : {username}" )
    if len(users)<= 0 or not check_password_hash(users[0]['password_hash'], password):
        return None, False
    else:
        return users[0], True
   
@app.route('/api/signIn', methods= ['POST'])
def sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }), 400
    username = request.json['username']
    password = request.json['password']
    if len(get_users_by_username(username) ) >0:
        return  jsonify({
            'error': 'Nombre de usuario ya existe'
        }), 400
    user_id = 'user-'+str(uuid.uuid4())
    users.append({
                'user_id': user_id,
                'username': username,
                'role': 'client',
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now()
            })
    return {
        'username': username,
        'user_id': user_id
    }, 201

    
@app.route('/api/login', methods=['POST'])
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }), 400
        
    username = request.json['username']
    password = request.json['password']
    user, auth_result = authenticate_user(username,password)
    if auth_result:
        user_id = user.get('user_id') 
        token = create_access_token(identity=username,additional_claims={
            'user_id': user_id,
            'role': user["role"]
        })
        return {"message": "login success", "access_token": token}, 200
    else:
        return {"message": "Not authorized"}, 401
    

@app.route('/dynamic-home')
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
            <h1>🎉 ¡Bienvenid@!</h1>
            <p>Esta es una página HTML con estilos CSS servida desde Flask.</p>
            <div class="highlight">{{ current_time }}</div>
            <p>✨ MongoDB está <strong>{{ db_status }}</strong></p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, 
                                  current_time= datetime.now() )
    
PORT = os.getenv('PORT_FLASK', '8001')

if __name__ == '__main__':
    connect_db()
    app.run(debug=True,port=PORT, host='0.0.0.0')