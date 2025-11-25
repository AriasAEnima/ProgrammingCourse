"""
Demo 3: Sistema Completo con Monitoring.

Demuestra:
- Múltiples workers monitoreados procesando tareas
- Worker Registry rastreando workers activos
- Heartbeats automáticos
- Procesamiento real de imágenes
"""
import time
import sys
from pathlib import Path
from multiprocessing import Process

# Agregar parent dir al path
sys.path.append(str(Path(__file__).parent.parent))

from workers import MonitoredRedisWorker, RedisTaskQueueV2, WorkerRegistry


def run_worker(worker_id: str):
    """
    Ejecuta un worker monitoreado en un proceso separado.
    
    Args:
        worker_id: ID del worker
    """
    worker = MonitoredRedisWorker(
        worker_id=worker_id,
        heartbeat_interval=5  # Heartbeat cada 5 segundos
    )
    worker.start()


def main():
    print("=" * 60)
    print("DEMO 3: Sistema Completo con Monitoring")
    print("=" * 60)
    print()
    
    # Limpiar estado previo
    queue = RedisTaskQueueV2()
    queue.clear()
    
    registry = WorkerRegistry()
    registry.clear()
    
    # === Paso 1: Agregar tareas ===
    print("📥 Paso 1: Agregando 10 tareas a la cola...")
    
    # Diferentes combinaciones de filtros para cada tarea
    filter_combinations = [
        [{"type": "blur", "radius": 3}, {"type": "brightness", "factor": 1.3}],
        [{"type": "grayscale"}, {"type": "edges"}],
        [{"type": "blur", "radius": 5}],
        [{"type": "brightness", "factor": 0.7}],
        [{"type": "blur", "radius": 2}, {"type": "grayscale"}],
        [{"type": "brightness", "factor": 1.5}, {"type": "edges"}],
        [{"type": "grayscale"}],
        [{"type": "edges"}, {"type": "blur", "radius": 1}],
        [{"type": "brightness", "factor": 0.5}, {"type": "blur", "radius": 2}],
        [{"type": "blur", "radius": 4}, {"type": "brightness", "factor": 1.1}, {"type": "edges"}]
    ]
    
    for i, filters in enumerate(filter_combinations):
        queue.add_task({
            "input_path": "images/sample.jpg",
            "output_path": f"output/monitored_{i}.jpg",
            "filters": filters
        })
    print(f"  ✅ {queue.get_stats()['pending']} tareas agregadas")
    print()
    
    # === Paso 2: Lanzar 3 workers ===
    print("🚀 Paso 2: Lanzando 3 workers monitoreados...")
    workers = []
    for i in range(3):
        worker_id = f"monitored-worker-{i+1}"
        process = Process(target=run_worker, args=(worker_id,))
        process.start()
        workers.append(process)
        time.sleep(0.5)  # Esperar un poco entre workers
    
    print(f"  ✅ {len(workers)} workers lanzados")
    print()
    
    # === Paso 3: Monitorear progreso ===
    print("📊 Paso 3: Monitoreando progreso...")
    print()
    
    start_time = time.time()
    last_check = 0
    
    while True:
        current_time = time.time()
        
        # Verificar cada 3 segundos
        if current_time - last_check >= 3:
            stats = queue.get_stats()
            active_workers = registry.get_active_workers()
            
            print(f"⏱️  {current_time - start_time:.0f}s | "
                  f"Workers activos: {len(active_workers)} | "
                  f"Pending: {stats['pending']} | "
                  f"Processing: {stats['processing']} | "
                  f"Completed: {stats['completed']}")
            
            # Mostrar workers activos
            for worker in active_workers:
                print(f"   - {worker['worker_id']}: heartbeat hace {worker['time_since_heartbeat']}s")
            
            last_check = current_time
            print()
        
        # Verificar si todas las tareas terminaron
        stats = queue.get_stats()
        if stats['pending'] == 0 and stats['processing'] == 0:
            print("✅ Todas las tareas completadas!")
            break
        
        time.sleep(1)
    
    elapsed = time.time() - start_time
    print()
    
    # === Paso 4: Estadísticas finales ===
    print("📊 Paso 4: Estadísticas finales:")
    stats = queue.get_stats()
    print(f"  Completadas: {stats['completed']}")
    print(f"  Failed/DLQ: {stats['dead_letter']}")
    print(f"  Tiempo total: {elapsed:.2f}s")
    print()
    
    # === Paso 5: Detener workers ===
    print("🛑 Paso 5: Deteniendo workers (espera 5s para graceful shutdown)...")
    time.sleep(5)  # Dar tiempo a que procesen señales y cierren limpiamente
    
    for process in workers:
        process.terminate()
        process.join(timeout=2)
    
    print("  ✅ Workers detenidos")
    print()
    
    # === Paso 6: Verificar registry después de shutdown ===
    print("📊 Paso 6: Workers en registry después de shutdown:")
    time.sleep(2)
    active = registry.get_active_workers()
    dead = registry.get_dead_workers()
    
    print(f"  Activos: {len(active)}")
    print(f"  Muertos: {len(dead)}")
    
    if dead:
        print("  Workers muertos:")
        for worker in dead:
            print(f"    - {worker['worker_id']}")
    print()
    
    print("=" * 60)
    print("✅ Demo completado!")
    print("=" * 60)
    print()
    print("💡 Nota: Si ves workers 'muertos', es normal.")
    print("   Los workers fueron terminados abruptamente para este demo.")


if __name__ == "__main__":
    main()

