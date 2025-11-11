#!/usr/bin/env python3
"""
Servidor WebSocket para manejo de notificaciones de restaurantes en tiempo real
Recibe y distribuye mensajes a todos los clientes conectados
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conjunto de conexiones activas
connected_clients = set()

async def register_client(websocket):
    """Registra un nuevo cliente WebSocket"""
    connected_clients.add(websocket)
    logger.info(f"🔗 Nuevo cliente conectado. Total: {len(connected_clients)}")
    
    # Mensaje de bienvenida
    welcome_message = {
        "type": "connection",
        "message": "Conectado al servidor de notificaciones",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "client_count": len(connected_clients)
    }
    await websocket.send(json.dumps(welcome_message))

async def unregister_client(websocket):
    """Desregistra un cliente WebSocket de forma segura"""
    if websocket in connected_clients:
        connected_clients.discard(websocket)
        client_id = "unknown"
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
        pass  # Ignorar errores al cerrar conexión ya cerrada

async def broadcast_message(message):
    """Envía un mensaje a todos los clientes conectados"""
    if not connected_clients:
        logger.warning("📢 No hay clientes conectados para enviar mensaje")
        return
    
    # Crear copia del set para evitar race conditions
    clients_snapshot = connected_clients.copy()
    disconnected_clients = []
    successful_sends = 0
    
    for websocket in clients_snapshot:
        try:
            # Verificar si la conexión sigue activa antes de enviar
            if websocket.closed:
                disconnected_clients.append(websocket)
                continue
                
            await websocket.send(json.dumps(message))
            successful_sends += 1
            
        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"🔌 Conexión cerrada detectada durante broadcast")
            disconnected_clients.append(websocket)
        except websockets.exceptions.WebSocketException as e:
            logger.debug(f"🔌 Error WebSocket: {e}")
            disconnected_clients.append(websocket)
        except Exception as e:
            logger.error(f"❌ Error inesperado enviando mensaje: {e}")
            disconnected_clients.append(websocket)
    
    # Limpiar clientes desconectados (solo quitar del set, no llamar unregister)
    # porque unregister será llamado desde handle_websocket_connection
    for websocket in disconnected_clients:
        connected_clients.discard(websocket)  # discard es thread-safe
    
    if disconnected_clients:
        logger.info(f"🧹 Limpiadas {len(disconnected_clients)} conexiones muertas")
    
    logger.info(f"📨 Mensaje enviado exitosamente a {successful_sends}/{len(clients_snapshot)} clientes")

async def handle_websocket_connection(websocket, path):
    """Maneja conexiones WebSocket individuales"""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    await register_client(websocket)
    
    try:
        # Enviar ping periódico para mantener conexión viva
        ping_task = None
        
        # Escuchar mensajes del cliente
        async for message in websocket:
            try:
                # Parsear mensaje JSON
                data = json.loads(message)
                logger.info(f"📥 Mensaje recibido de {client_id}: {data.get('type', 'unknown')}")
                
                # Procesar diferentes tipos de mensajes
                if data.get("type") == "restaurant_created":
                    # Mensaje de nuevo restaurante creado
                    restaurant = data.get("restaurant", {})
                    notification = {
                        "type": "restaurant_notification", 
                        "action": "created",
                        "restaurant": restaurant,
                        "message": f"🍽️ Nuevo restaurante registrado: {restaurant.get('nombre', 'Sin nombre')} ({restaurant.get('tipo_cocina', 'N/A')})",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "restaurant_updated":
                    # Mensaje de restaurante actualizado
                    restaurant = data.get("restaurant", {})
                    notification = {
                        "type": "restaurant_notification",
                        "action": "updated", 
                        "restaurant": restaurant,
                        "message": f"🔄 Restaurante actualizado: {restaurant.get('nombre', 'Sin nombre')} - ⭐ {restaurant.get('calificacion', 'N/A')}",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "restaurant_deleted":
                    # Mensaje de restaurante eliminado
                    restaurant = data.get("restaurant", {})
                    notification = {
                        "type": "restaurant_notification",
                        "action": "deleted",
                        "restaurant": restaurant, 
                        "message": f"🗑️ Restaurante eliminado: {restaurant.get('nombre', 'Sin nombre')} ({restaurant.get('tipo_cocina', 'N/A')})",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "ping":
                    # Responder a ping del cliente
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }))
                    
                else:
                    # Mensaje genérico
                    logger.debug(f"Mensaje genérico recibido de {client_id}: {data.get('type', 'unknown')}")
                    
            except json.JSONDecodeError:
                logger.warning(f"❌ Mensaje no JSON válido de {client_id}: {message[:100]}...")
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje de {client_id}: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Conexión cerrada normalmente por cliente {client_id}")
    except websockets.exceptions.WebSocketException as e:
        logger.info(f"🔌 Error WebSocket de cliente {client_id}: {e}")
    except Exception as e:
        logger.error(f"❌ Error inesperado en conexión {client_id}: {e}")
    finally:
        # Asegurar limpieza de conexión
        logger.info(f"🧹 Limpiando conexión de {client_id}")
        await unregister_client(websocket)

async def main():
    """Función principal para iniciar el servidor WebSocket"""
    # Configuración del servidor
    host = "localhost"
    port = 8765
    
    logger.info("🚀 Iniciando servidor WebSocket...")
    logger.info(f"📍 Servidor ejecutándose en ws://{host}:{port}")
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
        # Mantener el servidor ejecutándose
        await asyncio.Future()  # Correr indefinidamente
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en servidor: {e}")

if __name__ == "__main__":
    # Ejecutar el servidor WebSocket
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor WebSocket detenido")
