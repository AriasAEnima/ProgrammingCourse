#!/usr/bin/env python3
"""
Servidor WebSocket para manejo de notificaciones de muebles en tiempo real
Recibe eventos de la API de Django y distribuye mensajes a todos los clientes conectados
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any
from websockets.server import WebSocketServerProtocol

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conjunto de conexiones activas (clientes WebSocket conectados)
connected_clients: Set[WebSocketServerProtocol] = set()

async def register_client(websocket: WebSocketServerProtocol) -> None:
    """
    Registra un nuevo cliente WebSocket
    
    Args:
        websocket: Conexión WebSocket del cliente
    """
    connected_clients.add(websocket)
    logger.info(f"🔗 Nuevo cliente conectado. Total: {len(connected_clients)}")
    
    # Mensaje de bienvenida
    welcome_message: Dict[str, Any] = {
        "type": "connection",
        "message": "Conectado al servidor de notificaciones de muebles",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "client_count": len(connected_clients)
    }
    await websocket.send(json.dumps(welcome_message))

async def unregister_client(websocket: WebSocketServerProtocol) -> None:
    """
    Desregistra un cliente WebSocket de forma segura
    
    Args:
        websocket: Conexión WebSocket del cliente a desregistrar
    """
    if websocket in connected_clients:
        connected_clients.discard(websocket)
        client_id: str = "unknown"
        try:
            if hasattr(websocket, 'remote_address') and websocket.remote_address:
                client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        except:
            pass
        logger.info(f"❌ Cliente {client_id} desconectado. Total activos: {len(connected_clients)}")
    
    # Cerrar conexión si aún está abierta
    try:
        if not websocket.closed:
            await websocket.close()
    except:
        pass

async def broadcast_message(message: Dict[str, Any]) -> None:
    """
    Envía un mensaje a todos los clientes conectados
    
    Args:
        message: Diccionario con el mensaje a enviar (se convertirá a JSON)
    """
    if not connected_clients:
        logger.warning("📢 No hay clientes conectados para enviar mensaje")
        return
    
    # Crear copia del set para evitar race conditions durante iteración
    clients_snapshot: Set[WebSocketServerProtocol] = connected_clients.copy()
    disconnected_clients: list[WebSocketServerProtocol] = []
    successful_sends: int = 0
    
    for websocket in clients_snapshot:
        try:
            if websocket.closed:
                disconnected_clients.append(websocket)
                continue
                
            await websocket.send(json.dumps(message))
            successful_sends += 1
            
        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"🔌 Conexión cerrada detectada durante broadcast")
            disconnected_clients.append(websocket)
        except Exception as e:
            logger.error(f"❌ Error inesperado enviando mensaje: {e}")
            disconnected_clients.append(websocket)
    
    # Limpiar clientes desconectados
    for websocket in disconnected_clients:
        connected_clients.discard(websocket)
    
    if disconnected_clients:
        logger.info(f"🧹 Limpiadas {len(disconnected_clients)} conexiones muertas")
    
    logger.info(f"📨 Mensaje enviado exitosamente a {successful_sends}/{len(clients_snapshot)} clientes")

async def handle_websocket_connection(websocket: WebSocketServerProtocol) -> None:
    """
    Maneja conexiones WebSocket individuales y procesa mensajes
    
    Args:
        websocket: Conexión WebSocket del cliente
    """
    client_id: str = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    await register_client(websocket)
    
    try:
        # Escuchar mensajes del cliente
        async for message in websocket:
            try:
                data: Dict[str, Any] = json.loads(message)
                logger.info(f"📥 Mensaje recibido de {client_id}: {data.get('type', 'unknown')}")
                
                # Procesar diferentes tipos de mensajes
                if data.get("type") == "furniture_created":
                    # Notificación de mueble creado
                    furniture: Dict[str, Any] = data.get("furniture", {})
                    notification: Dict[str, Any] = {
                        "type": "furniture_notification",
                        "action": "created",
                        "furniture": furniture,
                        "message": f"🪑 Nuevo mueble creado: {furniture.get('nombre', 'Sin nombre')} - {furniture.get('material', 'Material desconocido')} ({furniture.get('ancho')}x{furniture.get('altura')}cm)",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "furniture_updated":
                    # Notificación de mueble actualizado
                    furniture: Dict[str, Any] = data.get("furniture", {})
                    notification: Dict[str, Any] = {
                        "type": "furniture_notification",
                        "action": "updated",
                        "furniture": furniture,
                        "message": f"🔄 Mueble actualizado: {furniture.get('nombre', 'Sin nombre')} - {furniture.get('ancho')}x{furniture.get('altura')}cm",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "furniture_deleted":
                    # Notificación de mueble eliminado
                    furniture: Dict[str, Any] = data.get("furniture", {})
                    notification: Dict[str, Any] = {
                        "type": "furniture_notification",
                        "action": "deleted",
                        "furniture": furniture,
                        "message": f"🗑️ Mueble eliminado: {furniture.get('nombre', 'Sin nombre')}",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "ping":
                    # Responder a ping con pong (para mantener conexión viva)
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }))
                    
                else:
                    logger.debug(f"Mensaje genérico recibido de {client_id}: {data.get('type', 'unknown')}")
                    
            except json.JSONDecodeError:
                logger.warning(f"❌ Mensaje no JSON válido de {client_id}: {message[:100]}...")
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje de {client_id}: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Conexión cerrada normalmente por cliente {client_id}")
    except Exception as e:
        logger.error(f"❌ Error inesperado en conexión {client_id}: {e}")
    finally:
        logger.info(f"🧹 Limpiando conexión de {client_id}")
        await unregister_client(websocket)

async def main() -> None:
    """Función principal para iniciar el servidor WebSocket"""
    # 0.0.0.0 permite conexiones desde Docker y localhost
    host: str = "0.0.0.0"
    port: int = 8765
    
    logger.info("🚀 Iniciando servidor WebSocket para Muebles...")
    logger.info(f"📍 Servidor ejecutándose en ws://0.0.0.0:{port}")
    logger.info(f"📍 Accesible desde localhost en: ws://localhost:{port}")
    logger.info(f"📍 Accesible desde Docker en: ws://host.docker.internal:{port}")
    logger.info("💡 Para probar: wscat -c ws://localhost:8765")
    logger.info("⏹️  Para detener: Ctrl+C")
    
    # Iniciar servidor WebSocket
    start_server = websockets.serve(
        handle_websocket_connection,
        host,
        port
    )
    
    try:
        await start_server
        await asyncio.Future()  # Correr indefinidamente
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en servidor: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor WebSocket detenido")

