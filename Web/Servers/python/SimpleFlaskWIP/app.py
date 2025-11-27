from flask import Flask, request, jsonify
from datetime import timedelta
from functools import wraps
from flask_jwt_extended import create_access_token, JWTManager, jwt_required,get_jwt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
app = Flask(__name__)

app_name = {"spanish": "muebles",
            "english": "forniture"}

app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

jwt = JWTManager(app)

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

@app.route('/')
def home():
    language = request.args.get("language","english")
    return "<h1> Home app "+app_name[language] + "</h1>" 

## REST ENDPOINTS

furnitures ={ "1": {"name": "Mesa Redonda", "width": 150 , "depth": 150 , "heigh": 150, "price": 110000},
        "2": {"name": "Mesa Rectangular", "width": 150 , "depth": 60 , "heigh": 120, "price": 120000},
        "3": {"name": "Silla triangular", "width": 85 , "depth": 65 , "heigh": 130, "price": 60000} }

@app.route('/api/furniture/<string:id>/',methods = ["GET"])
@jwt_required()
def get_furniture(id):   
    if id in furnitures:
        return furnitures[id], 200
    else:
        return {"messsage": "forniture with "+id+" not found"}, 404
    
@app.route('/api/furniture/<string:id>/',methods = ["DELETE"])
@admin_required
# role_required(["admin", "manager"])
def del_furniture(id):     
    if id not in furnitures:
        return {},208
    else:
        del furnitures[id]
        return {},200

@app.route('/api/furnitures/')
@jwt_required()
def get_furnitures(): 
    width = request.args.get("width",0)
    heigh =  request.args.get("heigh",0)   
    filtered = list(filter(lambda key : furnitures[key]["width"] >= int(width) 
                           and furnitures[key]["heigh"] >= int(heigh) , furnitures))
    return list(map(lambda k: furnitures[k], filtered))

@app.route('/api/furniture/', methods = ["POST"])
@admin_required
def post_furniture(): 
    body = request.json
    furniture_id = str(body["id"])
    if furniture_id in furnitures:
        return {"message": "Fornture with id "+furniture_id + " already exist" }, 409    
    else:
        del body["id"] 
        furnitures[furniture_id] = body
        return furnitures[furniture_id], 201
    
@app.route('/api/furniture/<string:id>/', methods=["PUT"])
@admin_required
def put_furniture(id):
    body = request.json
    price = body.get("price")
    name = body.get("name")
    if id in furnitures:
        if price != None:
            furnitures[id]["price"] = price
        if name != None:
            furnitures[id]["name"] = name
            
        return furnitures[id], 200
    else:
        return {"messsage": "forniture with "+id+" not found"}, 404
         
users = [
            {
                'user_id': 'user-1',
                'username': 'user-admin',
                'role': 'admin',
                'password_hash': generate_password_hash('user-admin-123'),
                'created_at': datetime.now()
            }
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
  
if __name__ == '__main__':
    app.run(debug=True,port=8001, host='0.0.0.0')