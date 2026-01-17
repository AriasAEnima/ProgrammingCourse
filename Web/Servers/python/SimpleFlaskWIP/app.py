from flask import Flask, request
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

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
def get_furnitures(): 
    width = request.args.get("width",0)
    heigh =  request.args.get("heigh",0)   
    filtered = list(filter(lambda key : furnitures[key]["width"] >= int(width) 
                           and furnitures[key]["heigh"] >= int(heigh) , furnitures))
    return list(map(lambda k: furnitures[k], filtered))

@app.route('/api/furniture/', methods = ["POST"])
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
          
        ]

def get_users_by_username(username):
    return list(filter(lambda u: u["username"]== username, users))

@app.route('/api/signIn', methods= ['POST'])
def sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        password = request.json['password']
        if len(get_users_by_username(username) ) >0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario ya existe'}, 400
        else:
            user_id = 'user-'+str(uuid.uuid4())
            new_user = {
                'user_id': user_id,
                'username': username,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now()
            }
            users.append(new_user)
            return { 'username': username, 'user_id': user_id,}, 201
        
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
                return { 'message': "login correcto"}, 200
            else:
                 return { 'message': "contraseña incorrecta"}, 401
            
if __name__ == '__main__':
    app.run(debug=True,
            port=8002, 
            host='0.0.0.0')