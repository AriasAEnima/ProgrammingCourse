"""
Blueprint para rutas misceláneas (shapes, status, etc.)
"""
from flask import Blueprint

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/shapes/status/500', methods=["GET"])
def get_shapes_500():
    """Endpoint de prueba que retorna status 500"""
    return "Hola ya no soy shapes", 500

@misc_bp.route('/shapes/status/200', methods=["GET"])
def get_shapes_200():
    """Endpoint de prueba que retorna status 200"""
    return "Hola ya no soy shapes", 200

@misc_bp.route('/shapes/<string:shape_id>/', methods=["GET"])
def get_shapes(shape_id):
    """Endpoint de prueba que verifica si un número es par o impar"""
    if int(shape_id) % 2 == 0:
        return "Es par"
    else:
        return "Es impar"