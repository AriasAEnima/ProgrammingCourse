#!/usr/bin/env python3
"""
Consumidor WebSocket que escucha notificaciones del servidor de muebles
Muestra en tiempo real las actualizaciones de muebles (creación, modificación, eliminación)
"""

import asyncio
import websockets
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

class FurnitureNotificationConsumer:
    """
    Clase para manejar las notificaciones de muebles vía WebSocket
    
    Escucha eventos de:
    - Creación de muebles
    - Actualización de muebles  
    - Eliminación de muebles
    """
    
    def __init__(self, websocket_url: Optional[str] = None) -> None:
        """
        Inicializa el consumidor de notificaciones
        
        Args:
            websocket_url: URL del servidor WebSocket (ej: ws://localhost:8765)
        """
        # Usar variable de entorno o valor por defecto
        self.websocket_url: str = websocket_url or os.getenv("WEBSOCKET_URL", "ws://localhost:8765")
        self.is_running: bool = False
        
    async def connect_and_listen(self) -> None:
        """
        Conecta al servidor WebSocket y escucha mensajes continuamente
        
        Mantiene la conexión abierta y procesa cada mensaje recibido
        """
        print("🚀 Iniciando consumidor de notificaciones de muebles...")
        print(f"📍 Conectando a: {self.websocket_url}")
        print("⏹️  Para detener: Ctrl+C")
        print("-" * 50)
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.is_running = True
                print("✅ Conectado al servidor WebSocket")
                
                # Escuchar mensajes continuamente
                async for message in websocket:
                    await self.process_message(message)
                    
        except websockets.exceptions.ConnectionClosed:
            print("❌ Conexión cerrada por el servidor")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            print("💡 Asegúrate de que el servidor WebSocket esté ejecutándose")
        finally:
            self.is_running = False
            print("👋 Desconectado del servidor WebSocket")
    
    async def process_message(self, message: str) -> None:
        """
        Procesa y muestra los mensajes recibidos del servidor
        
        Args:
            message: Mensaje JSON recibido del servidor WebSocket
        """
        try:
            data: Dict[str, Any] = json.loads(message)
            message_type: str = data.get("type", "unknown")
            timestamp_str: str = data.get("timestamp", "")
            
            # Convertir timestamp ISO a formato legible
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', ''))
            formatted_time: str = timestamp.strftime("%H:%M:%S")
            
            print(f"\n[{formatted_time}] ", end="")
            
            if message_type == "connection":
                # Mensaje de conexión inicial del servidor
                print(f"🔗 {data.get('message')}")
                print(f"👥 Clientes conectados: {data.get('client_count', 1)}")
                
            elif message_type == "furniture_notification":
                # Notificación de mueble (crear, actualizar, eliminar)
                action: str = data.get("action", "unknown")
                furniture: Dict[str, Any] = data.get("furniture", {})
                message_text: str = data.get("message", "")
                
                print(f"🪑 {message_text}")
                
                # Mostrar detalles del mueble
                if furniture:
                    print(f"   🆔 ID: {furniture.get('furniture_id', 'N/A')}")
                    print(f"   🏷️  Nombre: {furniture.get('nombre', 'Sin nombre')}")
                    print(f"   📏 Dimensiones: {furniture.get('ancho', 'N/A')}cm (ancho) x {furniture.get('altura', 'N/A')}cm (alto)")
                    print(f"   🪵 Material: {furniture.get('material', 'N/A')}")
                    print(f"   👤 Autor: {furniture.get('autor_username', 'Anónimo')}")
                    
                    # Mensaje específico según la acción
                    if action == "created":
                        print(f"   🎉 ¡Nuevo mueble disponible en el catálogo!")
                    elif action == "updated":
                        print(f"   🔄 Información del mueble actualizada")
                    elif action == "deleted":
                        print(f"   🗑️  Mueble eliminado del catálogo")
            
            else:
                # Mensaje genérico o desconocido
                print(f"📨 {data}")
            
            print("-" * 30)
            
        except json.JSONDecodeError:
            print(f"❌ Mensaje no válido (no es JSON): {message}")
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")

    async def run(self) -> None:
        """
        Ejecuta el consumidor con reconexión automática
        
        Reintenta la conexión hasta 5 veces en caso de fallo
        """
        retry_count: int = 0
        max_retries: int = 5
        
        while retry_count < max_retries:
            try:
                await self.connect_and_listen()
                break
                
            except KeyboardInterrupt:
                print("\n⏹️ Detenido por el usuario")
                break
                
            except Exception as e:
                retry_count += 1
                print(f"❌ Error de conexión (intento {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    print(f"🔄 Reintentando en 3 segundos...")
                    await asyncio.sleep(3)
                else:
                    print("❌ Máximo número de reintentos alcanzado")

def main() -> None:
    """Función principal para iniciar el consumidor"""
    print("🎯 Consumidor de Notificaciones de Muebles")
    print("=" * 50)
    
    # Crear y ejecutar el consumidor
    consumer = FurnitureNotificationConsumer()
    
    try:
        asyncio.run(consumer.run())
    except KeyboardInterrupt:
        print("\n👋 Consumidor detenido por el usuario")

if __name__ == "__main__":
    main()

