"""
Cliente WebSocket para enviar notificaciones en tiempo real
Maneja la comunicación con el servidor WebSocket cuando hay cambios en los muebles
"""

import asyncio
import websockets
import json
import os
from typing import Dict, Any, Optional
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# URL del servidor WebSocket (configurable por variable de entorno)
WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL", "ws://websocket-server:8765")


async def send_websocket_notification_async(
    notification_type: str, 
    furniture_data: Dict[str, Any]
) -> bool:
    """
    Envía una notificación al servidor WebSocket de forma asíncrona
    
    Args:
        notification_type: Tipo de notificación 
            - 'furniture_created': Cuando se crea un mueble
            - 'furniture_updated': Cuando se actualiza un mueble
            - 'furniture_deleted': Cuando se elimina un mueble
        furniture_data: Diccionario con los datos del mueble
            - furniture_id: ID del mueble
            - nombre: Nombre del mueble
            - descripcion: Descripción
            - altura: Altura en cm
            - ancho: Ancho en cm
            - material: Material del mueble
            - autor_username: Usuario que lo creó/modificó
            
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    try:
        # Conectar al servidor WebSocket (sin timeout explícito, usa el default)
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            message: Dict[str, Any] = {
                "type": notification_type,
                "furniture": furniture_data
            }
            # Se recibe un saludo por la conexion (no se ve)
            # no se ve la notificacion generada
            # Solo "hablo"
            await websocket.send(json.dumps(message))
            logger.info(f"✅ Notificación WebSocket enviada: {notification_type} - {furniture_data.get('nombre', 'N/A')}")
            return True
            
    except websockets.exceptions.WebSocketException as e:
        logger.warning(f"⚠️ Error de WebSocket: {e}")
        return False
    except asyncio.TimeoutError:
        logger.warning(f"⚠️ Timeout al conectar con WebSocket: {WEBSOCKET_URL}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado enviando notificación WebSocket: {e}")
        return False


def notify_websocket(notification_type: str, furniture_data: Dict[str, Any]) -> bool:
    """
    Wrapper sincrónico para enviar notificaciones WebSocket
    Permite usar la función asíncrona desde código sincrónico (views de Django)
    
    Args:
        notification_type: Tipo de notificación ('furniture_created', 'furniture_updated', 'furniture_deleted')
        furniture_data: Datos del mueble
        
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    try:
        # Crear un nuevo event loop para la operación asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            send_websocket_notification_async(notification_type, furniture_data)
        )
        loop.close()
        return result
    except Exception as e:
        logger.error(f"❌ Error ejecutando notificación: {e}")
        return False


def notify_furniture_created(furniture_id: str, nombre: str, descripcion: str, 
                            altura: int, ancho: int, material: str, 
                            autor_username: str) -> bool:
    """
    Notifica la creación de un nuevo mueble
    
    Args:
        furniture_id: ID del mueble creado
        nombre: Nombre del mueble
        descripcion: Descripción del mueble
        altura: Altura en cm
        ancho: Ancho en cm
        material: Material del mueble
        autor_username: Usuario que lo creó
        
    Returns:
        True si se envió exitosamente
    """
    furniture_data: Dict[str, Any] = {
        "furniture_id": furniture_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "altura": altura,
        "ancho": ancho,
        "material": material,
        "autor_username": autor_username
    }
    return notify_websocket("furniture_created", furniture_data)


def notify_furniture_updated(furniture_id: str, nombre: str, descripcion: str,
                            altura: int, ancho: int, material: str,
                            autor_username: str) -> bool:
    """
    Notifica la actualización de un mueble existente
    
    Args:
        furniture_id: ID del mueble actualizado
        nombre: Nombre actualizado
        descripcion: Descripción actualizada
        altura: Altura actualizada en cm
        ancho: Ancho actualizado en cm
        material: Material actualizado
        autor_username: Usuario que hizo la modificación
        
    Returns:
        True si se envió exitosamente
    """
    furniture_data: Dict[str, Any] = {
        "furniture_id": furniture_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "altura": altura,
        "ancho": ancho,
        "material": material,
        "autor_username": autor_username
    }
    return notify_websocket("furniture_updated", furniture_data)


def notify_furniture_deleted(furniture_id: str, nombre: str, descripcion: str,
                            altura: int, ancho: int, material: str,
                            autor_username: str) -> bool:
    """
    Notifica la eliminación de un mueble
    
    Args:
        furniture_id: ID del mueble eliminado
        nombre: Nombre del mueble eliminado
        descripcion: Descripción
        altura: Altura en cm
        ancho: Ancho en cm
        material: Material
        autor_username: Usuario que lo eliminó
        
    Returns:
        True si se envió exitosamente
    """
    furniture_data: Dict[str, Any] = {
        "furniture_id": furniture_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "altura": altura,
        "ancho": ancho,
        "material": material,
        "autor_username": autor_username
    }
    return notify_websocket("furniture_deleted", furniture_data)

