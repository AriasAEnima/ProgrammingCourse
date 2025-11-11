#!/usr/bin/env python3
"""
Script para iniciar automáticamente todo el sistema WebSocket + Flask
Lanza los 3 servicios y proporciona comandos para gestionarlos
"""

import subprocess
import time
import signal
import sys
import os
import requests
import json

class WebSocketSystemManager:
    """Gestor del sistema completo WebSocket + Flask"""
    
    def __init__(self):
        self.processes = {}
        self.logs_dir = "logs"
        
    def ensure_logs_directory(self):
        """Crear directorio de logs si no existe"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            print(f"📁 Directorio {self.logs_dir}/ creado")
    
    def start_websocket_server(self):
        """Iniciar servidor WebSocket"""
        print("🚀 Iniciando servidor WebSocket...")
        
        process = subprocess.Popen(
            ["python", "websocket_server.py"],
            stdout=open(f"{self.logs_dir}/websocket_server.log", "w"),
            stderr=subprocess.STDOUT
        )
        self.processes["websocket_server"] = process
        print(f"   ✅ Servidor WebSocket iniciado (PID: {process.pid})")
        return process
    
    def start_flask_api(self):
        """Iniciar API Flask"""
        print("🌐 Iniciando API Flask...")
        
        process = subprocess.Popen(
            ["python", "app.py"],
            stdout=open(f"{self.logs_dir}/flask_api.log", "w"),
            stderr=subprocess.STDOUT
        )
        self.processes["flask_api"] = process
        print(f"   ✅ API Flask iniciada (PID: {process.pid})")
        return process
    
    def start_websocket_consumer(self):
        """Iniciar consumidor WebSocket"""
        print("👂 Iniciando consumidor WebSocket...")
        
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"  # Importante para logs inmediatos
        
        process = subprocess.Popen(
            ["python", "websocket_consumer.py"],
            stdout=open(f"{self.logs_dir}/websocket_consumer.log", "w"),
            stderr=subprocess.STDOUT,
            env=env
        )
        self.processes["websocket_consumer"] = process
        print(f"   ✅ Consumidor WebSocket iniciado (PID: {process.pid})")
        return process
    
    def wait_for_service(self, url, service_name, max_attempts=30):
        """Esperar a que un servicio esté disponible"""
        print(f"⏳ Esperando {service_name}...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    print(f"   ✅ {service_name} disponible")
                    return True
            except:
                time.sleep(1)
                print(".", end="", flush=True)
        
        print(f"\n   ❌ {service_name} no disponible después de {max_attempts} segundos")
        return False
    
    def test_system(self):
        """Probar que el sistema funciona creando un restaurante"""
        print("\n🧪 Probando el sistema...")
        
        test_restaurant = {
            "nombre": "🎯 Restaurante de Prueba",
            "tipo_cocina": "Italiana",
            "direccion": "Calle Test 123",
            "telefono": "123-456-7890",
            "calificacion": 5,
            "precio_promedio": 25.50,
            "delivery": True
        }
        
        try:
            response = requests.post(
                "http://localhost:8001/api/restaurantes",
                json=test_restaurant,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                task = response.json()["task"]
                print(f"   ✅ Tarea creada: {task['title']}")
                print(f"   📝 ID: {task['id']}")
                print("   💡 Revisa el consumidor WebSocket para ver la notificación!")
                return True
            else:
                print(f"   ❌ Error creando restaurante: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def show_status(self):
        """Mostrar estado de todos los servicios"""
        print("\n📊 Estado del Sistema:")
        print("-" * 50)
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"✅ {name}: Ejecutándose (PID: {process.pid})")
            else:
                print(f"❌ {name}: Detenido")
    
    def show_logs(self):
        """Mostrar información sobre logs"""
        print("\n📋 Logs del Sistema:")
        print("-" * 50)
        print(f"📁 Directorio de logs: {self.logs_dir}/")
        print(f"🔍 Ver logs en tiempo real:")
        print(f"   tail -f {self.logs_dir}/websocket_consumer.log")
        print(f"   tail -f {self.logs_dir}/flask_api.log")
        print(f"   tail -f {self.logs_dir}/websocket_server.log")
    
    def stop_all(self):
        """Detener todos los procesos"""
        print("\n⏹️ Deteniendo todos los servicios...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"   🛑 Deteniendo {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("   ✅ Todos los servicios detenidos")
    
    def handle_signal(self, signum, frame):
        """Manejar señales para cierre limpio"""
        print(f"\n🛑 Señal {signum} recibida. Cerrando sistema...")
        self.stop_all()
        sys.exit(0)
    
    def run(self):
        """Ejecutar el sistema completo"""
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        print("🎯 Sistema WebSocket + Flask")
        print("=" * 50)
        
        # Crear directorio de logs
        self.ensure_logs_directory()
        
        try:
            # Iniciar servicios en orden
            self.start_websocket_server()
            time.sleep(2)
            
            self.start_flask_api()
            time.sleep(2)
            
            self.start_websocket_consumer()
            time.sleep(2)
            
            # Verificar servicios
            if not self.wait_for_service("http://localhost:8001", "API Flask"):
                raise Exception("API Flask no disponible")
            
            # Probar sistema
            if self.test_system():
                print("\n🎉 ¡Sistema iniciado correctamente!")
            else:
                print("\n⚠️ Sistema iniciado pero con problemas en las pruebas")
            
            self.show_status()
            self.show_logs()
            
            print("\n" + "=" * 50)
            print("💡 Comandos útiles:")
            print("   • Ctrl+C para detener todo")
            print("   • http://localhost:8001 - API Flask")
            print("   • ws://localhost:8765 - Servidor WebSocket")
            print("=" * 50)
            
            # Mantener script corriendo
            print("\n⏳ Sistema ejecutándose... Presiona Ctrl+C para detener")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.stop_all()

def main():
    """Función principal"""
    manager = WebSocketSystemManager()
    manager.run()

if __name__ == "__main__":
    main()
