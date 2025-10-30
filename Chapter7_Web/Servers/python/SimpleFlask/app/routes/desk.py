"""
Blueprint para rutas de escritorios/mesas
"""
from flask import Blueprint, request, jsonify
from app.models import get_desk_by_id, get_all_desks_filtered, add_new_desk
from app.utils import role_required, admin_required

desk_bp = Blueprint('desk', __name__)

@desk_bp.route('/<string:desk_id>/', methods=["GET"])
@role_required
def get_desk(desk_id):
    """Obtener escritorio por ID"""
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

@desk_bp.route('', methods=["GET"])
@role_required
def get_all_desks():
    """Obtener todos los escritorios con filtros opcionales"""
    width_query_param = request.args.get("width")
    height_query_param = request.args.get("height")
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

@desk_bp.route('', methods=["POST"])
@admin_required
def post_desk():
    """Crear nuevo escritorio (solo administradores)"""
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