from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app_name = {"spanish": "muebles",
            "english": "forniture"}

app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'

jwt = JWTManager()

@app.route('/')
def home():
    language = request.args.get("language","english")
    return "<h1> Home app "+app_name[language] + "</h1>" 


## REST ENDPOINTS

furnitures ={ "1": {"name": "Mesa Redonda", "width": 150 , "depth": 150 , "heigh": 150, "price": 110000},
        "2": {"name": "Mesa Rectangular", "width": 150 , "depth": 60 , "heigh": 120, "price": 120000},
        "3": {"name": "Silla triangular", "width": 85 , "depth": 65 , "heigh": 130, "price": 60000} }

@app.route('/api/furniture/<string:id>/')
def get_furniture(id):    
    if id in furnitures:
        return furnitures[id], 200
    else:
        return {"messsage": "forniture with "+id+" not found"}, 404
    
@app.route('/api/furnitures/')
def get_furnitures(): 
    width = request.args.get("width",0)
    heigh =  request.args.get("heigh",0)   
    filtered = list(filter(lambda key : furnitures[key]["width"] >= int(width) 
                           and furnitures[key]["heigh"] >= int(heigh) , furnitures))
    return list(map(lambda k: furnitures[k], filtered))

@app.route('/api/furniture/', methods = ["POST"])
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
    
    
@app.route('/api/furniture/<string:id>', methods = ["DELETE"])
def delete_furniture(id): 
    if id not in furnitures:
        return {},208
    else:
        del furnitures[id]
        return {},200
    
users = [
            {
                'user_id': 'user-2',
                'username': 'user',
                'password_hash': generate_password_hash('user123'),
                'created_at': datetime.now()
            }
        ]

def get_users_by_username(username):
    return list(filter(lambda u: u["username"]== username))

def authenticate_user(username, password):
    users  = get_users_by_username(username)
    if not users[0] or not check_password_hash(users[0]['password_hash'], password):
        return None, False
    else:
        return users[0], True
    
@app.route('/login', methods=['POST'])
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
            'user_id': user_id
        })
        return {"message": "login success", "access_token": token}, 200
    else:
        return {"message": "Not authorized"}, 401
  
if __name__ == '__main__':
    app.run(debug=True,port=8001, host='0.0.0.0')