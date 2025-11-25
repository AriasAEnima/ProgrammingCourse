"""
Demo 1: Worker Registry - Registro y health checks de workers.

Demuestra:
- Registrar workers
- Enviar heartbeats
- Detectar workers muertos
- Limpiar workers muertos
"""
import time
import sys
from pathlib import Path

# Agregar parent dir al path
sys.path.append(str(Path(__file__).parent.parent))

from workers import WorkerRegistry


def main():
    print("=" * 60)
    print("DEMO 1: Worker Registry")
    print("=" * 60)
    print()
    
    # Crear registry
    registry = WorkerRegistry(heartbeat_timeout=10)
    
    # Limpiar registry anterior
    registry.clear()
    
    # === Paso 1: Registrar workers ===
    print("📝 Paso 1: Registrando 3 workers...")
    registry.register_worker("worker-1", metadata={"hostname": "server-1"})
    registry.register_worker("worker-2", metadata={"hostname": "server-2"})
    registry.register_worker("worker-3", metadata={"hostname": "server-3"})
    print()
    
    # === Paso 2: Ver workers activos ===
    time.sleep(1)
    print("📊 Paso 2: Workers activos:")
    active = registry.get_active_workers()
    for worker in active:
        print(f"  - {worker['worker_id']}: alive={worker['is_alive']}, "
              f"heartbeat={worker['time_since_heartbeat']}s ago")
    print()
    
    # === Paso 3: Simular heartbeats ===
    print("💓 Paso 3: Enviando heartbeats para worker-1 y worker-2...")
    for i in range(3):
        registry.send_heartbeat("worker-1")
        registry.send_heartbeat("worker-2")
        # worker-3 NO envía heartbeat (se morirá)
        time.sleep(2)
        print(f"  Heartbeat #{i+1} enviado")
    print()
    
    # === Paso 4: Esperar a que worker-3 muera ===
    print("⏳ Paso 4: Esperando 6s para que worker-3 muera (sin heartbeat)...")
    time.sleep(6)
    print()
    
    # === Paso 5: Verificar workers muertos ===
    print("💀 Paso 5: Detectando workers muertos...")
    dead = registry.get_dead_workers()
    for worker in dead:
        print(f"  - {worker['worker_id']}: muerto hace {worker['time_since_heartbeat']}s")
    print()
    
    # === Paso 6: Ver estadísticas ===
    print("📊 Paso 6: Estadísticas del registry:")
    stats = registry.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # === Paso 7: Limpiar workers muertos ===
    print("🧹 Paso 7: Limpiando workers muertos...")
    cleaned = registry.cleanup_dead_workers()
    print(f"  Limpiados: {cleaned} workers")
    print()
    
    # === Paso 8: Ver workers activos después de limpiar ===
    print("📊 Paso 8: Workers activos después de limpiar:")
    active = registry.get_active_workers()
    for worker in active:
        print(f"  - {worker['worker_id']}")
    print()
    
    # === Paso 9: Des-registrar workers restantes ===
    print("👋 Paso 9: Des-registrando workers restantes...")
    registry.unregister_worker("worker-1")
    registry.unregister_worker("worker-2")
    print()
    
    print("=" * 60)
    print("✅ Demo completado!")
    print("=" * 60)


if __name__ == "__main__":
    main()

