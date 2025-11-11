"""
Servicio para enviar notificaciones a través de WebSocket
Mantiene la lógica de notificaciones separada de las vistas
"""

import websockets
import asyncio
import json
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# URL del servidor WebSocket (configurable)
# Opciones:
#   - host.docker.internal:8765 (Mac/Windows con Docker Desktop)
#   - 192.168.65.2:8765 (Mac con Docker Desktop - IP alternativa)
#   - TU_IP_LOCAL:8765 (reemplazar con tu IP, ej: 192.168.1.100:8765)
#   - localhost:8765 (si Django corre fuera de Docker)
import os
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://host.docker.internal:8765")


def send_desk_notification(notification_type, desk_data):
    """
    Envía una notificación de mesa al servidor WebSocket
    
    Args:
        notification_type (str): Tipo de notificación ('created', 'updated', 'deleted')
        desk_data (dict): Datos de la mesa
    
    Esta función utiliza threading para no bloquear la aplicación Django
    """
    message_data = {
        "type": f"desk_{notification_type}",
        "desk": desk_data,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    
    # Ejecutar en thread separado para no bloquear Django
    thread = threading.Thread(target=_send_message_sync, args=(message_data,))
    thread.daemon = True
    thread.start()


def _send_message_sync(message_data):
    """
    Función sincrónica que ejecuta el código asíncrono de envío
    """
    try:
        asyncio.run(_async_send_message(message_data))
    except Exception as e:
        logger.error(f"Error enviando notificación WebSocket: {e}")


async def _async_send_message(message_data):
    """
    Envía el mensaje al servidor WebSocket de forma asíncrona
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, timeout=2) as websocket:
            await websocket.send(json.dumps(message_data))
            logger.info(f"✅ Notificación WebSocket enviada: {message_data['type']}")
    except asyncio.TimeoutError:
        logger.warning(f"⏱️ Timeout conectando al servidor WebSocket en {WEBSOCKET_URL}")
    except ConnectionRefusedError:
        logger.warning(f"🔌 No se pudo conectar al servidor WebSocket en {WEBSOCKET_URL}")
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje WebSocket: {e}")


# Funciones de conveniencia para cada tipo de notificación

def notify_desk_created(desk):
    """
    Notifica que se creó una nueva mesa
    
    Args:
        desk: Instancia del modelo Desk
    """
    desk_data = {
        "desk_id": str(desk.id),
        "name": desk.name,
        "width": desk.width,
        "height": desk.height
    }
    send_desk_notification("created", desk_data)


def notify_desk_updated(desk):
    """
    Notifica que se actualizó una mesa
    
    Args:
        desk: Instancia del modelo Desk
    """
    desk_data = {
        "desk_id": str(desk.id),
        "name": desk.name,
        "width": desk.width,
        "height": desk.height
    }
    send_desk_notification("updated", desk_data)


def notify_desk_deleted(desk_id, desk_name):
    """
    Notifica que se eliminó una mesa
    
    Args:
        desk_id (str): ID de la mesa eliminada
        desk_name (str): Nombre de la mesa eliminada
    """
    desk_data = {
        "desk_id": desk_id,
        "name": desk_name
    }
    send_desk_notification("deleted", desk_data)

