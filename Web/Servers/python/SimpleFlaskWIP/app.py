from flask import Flask, request
import uuid
#import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt
#from dotenv import load_dotenv

app = Flask(__name__)

#load_dotenv()

app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccio'

#app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

jwt = JWTManager(app)
host = 'mongodb://localhost'
port = 27017
db_name = 'furniture_flask'
# admin , manager , user
user_collection = None
furniture_collection = None

def connect_db():
    try:
        client = MongoClient(host+":"+str(port)+"/")
        db = client[db_name]
        client.admin.command('ping')
        global user_collection
        user_collection = db.users
        global furniture_collection
        furniture_collection = db.furnitures
        print("✅ Conexión a MongoDB exitosa")
        print(f"DB Check : {db!=None}")        
        print(f"DB furniture_collection : {furniture_collection!=None}") 
        print(f"DB user_collection : {user_collection!=None}")         
    except Exception as e:
        pass
 
# Returns list    
def check_if_usr_exist(username): 
    global user_collection
    print(f"Debug username: {username}")
    query = {"username" : {"$eq": username }}
    return list(user_collection.find(query))
    
def create_usr(usr):
    global user_collection
    result = user_collection.insert_one(usr)
    print( f"DEBUG ID value {result.inserted_id} type {type(result.inserted_id)}")
    usr["_id"] = str(result.inserted_id)
    return usr

def create_admin_if_exist(usr):
    check_admin = check_if_usr_exist(usr["username"])
    if len(check_admin) > 0:
        return check_admin
    else:
        return create_usr(usr)

def get_token_role():
    try:
        claims = get_jwt()
        return claims.get('role','user')
    except:
        return None
    

def manager_required(f):
    @jwt_required()
    def custom_validation(*args,**kwargs):
        role = get_token_role()
        if role == 'manager':
            return f(*args,**kwargs)
        else:
            print(f"Debug Role: {role}")
            return {
                'error': 'Acceso denegado',
                'message': 'Solo los manager pueden acceder a este endpoint'
            }, 403
    return custom_validation         
        


@app.route('/')
def hello():
    return "<h1> Hola Mundo </h1>"

@app.route('/hello/<string:name>')
def grettings(name):
    return "<h1> Hola Mundo "+ name +  "</h1>"


#https://www.alkosto.com/fuente

#https://www.alkosto.com/?fuente=google&medio=cpc&campaign=AK_COL_SEM_PEF_CPC_PB_AON_TLP_TLP_Brand-General-AON_PAC&keyword=alkosto&gad_source=1&gad_campaignid=2018735487&gbraid=0AAAAADlnVbhjpa2yNJXbRpygnnsX8VizY&gclid=CjwKCAiAvaLLBhBFEiwAYCNTf7C40kfNPJpky3V0zSRGu-gSyhJjIbLtlSTqw3Q8kPaLJiK2O4N3lBoCGjoQAvD_BwE
#https://listado.mercadolibre.com.co/laptop#D[A:laptop]&origin=UNKNOWN&as.comp_t=SUG&as.comp_v=lapto&as.comp_id=SUG
#https://www.amazon.com/s?k=laptop&__mk_es_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1FUXXWEL7GE7T&sprefix=laptop%2Caps%2C167&ref=nb_sb_noss_1

saludo = {"ES": "Hola Mundo",
          "EN": "Hello World"}

@app.route('/dynamic-hello/<string:name>/')
def data(name):
    language = request.args.get("language", "EN")
    uppercase = request.args.get("uppercase", False)
    phase = saludo[language] + " " + name
    if uppercase == "True" or uppercase == "true":
        phase = phase.upper()
    return "<h1>" + phase + "</h1>"

furnitures = { "1": {"name": "Mesa Redonda", "width": 150 , "depth": 150 , "heigh": 150, "price": 110000},
        "2": {"name": "Mesa Rectangular", "width": 150 , "depth": 60 , "heigh": 120, "price": 120000},
        "3": {"name": "Silla triangular", "width": 85 , "depth": 65 , "heigh": 130, "price": 60000} }


@app.route('/api/furniture/<string:id>/',methods = ["GET", "DELETE"])
@jwt_required()
def get_furniture(id):   
    print(f"METHOD {request.method}")
    if request.method == "GET":
        if id in furnitures:
            return furnitures[id], 200
        else:
            return {"messsage": "forniture with "+id+" not found"}, 404
    else:
        if id in furnitures:
            element = furnitures[id]
            del furnitures[id]
            return element , 200
        else:
            return {}, 204
    
@app.route('/api/furnitures/')
@jwt_required()
def get_furnitures(): 
    width = request.args.get("width",0)
    heigh =  request.args.get("heigh",0)   
    filtered = list(filter(lambda key : furnitures[key]["width"] >= int(width) 
                           and furnitures[key]["heigh"] >= int(heigh) , furnitures))
    return list(map(lambda k: furnitures[k], filtered))

@app.route('/api/furniture/', methods = ["POST"])
@manager_required
def post_furnitures():
    body = request.json
    copy = body.copy()
    new_id = body["id"]
    if new_id in furnitures:
        return {"message": "Fornture with id "+new_id + " already exist" }, 409    
    else:
        del body["id"]
        furnitures[new_id] = body   
        return copy, 201

@app.route('/api/furniture/<string:id>/', methods=["PATCH"])
@jwt_required()
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

@app.route('/api/admin/signIn/manager', methods= ['POST'])
#manager_required
def admin_sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        password = request.json['password']
        if len(check_if_usr_exist(username)) >0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario ya existe'}, 400
        else:
            new_user = {
                'username': username,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now(),
                'role': 'manager'
            }
            user_created = create_usr(new_user)
            
            return { 'username': username, '_id': user_created["_id"], 'role': 'manager'}, 201
   

@app.route('/api/signIn', methods= ['POST'])
def sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        password = request.json['password']
        if len(check_if_usr_exist(username) ) >0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario ya existe'}, 400
        else:
            new_user = {
                'username': username,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now(),
                'role': 'client'
            }
            user_created = create_usr(new_user)
            
            return { 'username': username, '_id': user_created["_id"], 'role': 'client'}, 201
        
@app.route('/api/login', methods= ['POST'])
def log_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        body_password = request.json['password']
        if len(get_users_by_username(username) ) == 0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario no existe'}, 400
        else:
            user = get_users_by_username(username)[0]
            user_password = user["password_hash"]
            if check_password_hash(user_password, body_password):
                token = create_access_token(identity=username,additional_claims={
                    "user_id" : user.get('user_id'),
                     "role": user.get('role')
                })
                return { 'message': "login correcto",
                        'token': token}, 200
            else:
                 return { 'message': "contraseña incorrecta"}, 401
            
if __name__ == '__main__':
    connect_db()
    admin_usr =    {
                'username': "admin",
                'password_hash': generate_password_hash('123456'),
                'created_at': datetime.now(),
                'role': "admin"
            }
    print( f"Admin user: {create_admin_if_exist(admin_usr)}")
    app.run(debug=True,
            port=8002, 
            host='0.0.0.0')