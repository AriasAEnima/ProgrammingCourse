from flask import Flask, request,jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, create_access_token
from functools import wraps

app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'  # ¡Cambiar en producción!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

users = {"manager": {
                    'id': 'user-2', 
                    'username': 'manager',
                    'password_hash': generate_password_hash('manager123'),  # Password: manager123
                    'role': 'manager',
                    'created_at': '2024-01-15T11:00:00Z'
                },
         "admin1": {
                    'id': 'user-1', 
                    'username': 'admin1',
                    'password_hash': generate_password_hash('admin123'),  # Password: manager123
                    'role': 'admin',
                    'created_at': '2024-01-15T11:00:00Z'
                }} 

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
    print(user)
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
    
desks = [
    {"id": 1,
    "name": "Mesa Venture",
     "width": 125,
     "height": 225},
     {"id": 2,
    "name": "Mesa Koto",
     "width": 200,
     "height": 223},
     {"id": 3,
       "name": "Mesa Amatista",
     "width": 200,
     "height": 300}]



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
                'message': f'Se requiere uno de estos roles: {", ".join(required_roles)}. Tu rol: {current_role}'
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
        
        


@app.route('/desk/<string:desk_id>/',methods = ["GET"])
@role_required
def get_desk(desk_id):
    ans = list(filter(lambda x: x["id"]==int(desk_id), desks))
    if len(ans)>0:
        return ans[0] , 200 
    else:
        print("ERROR")
        return {"mensaje": "Mesa no existe"}, 404
    
@app.route('/desk',methods = ["GET"])
@role_required
def get_all_desks():
   width_query_param= request.args.get("width")
   height_query_param= request.args.get("height")
   print(f"width {width_query_param}, height {height_query_param}")
   ans = desks
   if width_query_param is not None:
    ans = list(filter(lambda x: x["width"]>=int(width_query_param), ans))
   if height_query_param is not None:
    ans = list(filter(lambda x: x["height"]>=int(height_query_param), ans))

   return ans , 200

@app.route('/desk',methods = ["POST"])
@admin_required
def post_desk():
   print(f"Body: {request.json}")
   body = request.json
   new_desk = {"id": body["id"],
    "name": body["name"],
     "width": body["width"],
     "height": body["height"]}
   desks.append(new_desk)
   return new_desk , 201
    

if __name__ == '__main__':
    app.run(
        host= '0.0.0.0',
        port= 8003,
        debug = True
    )