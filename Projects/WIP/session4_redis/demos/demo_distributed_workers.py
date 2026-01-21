#!/usr/bin/env python3
"""
Demo: Múltiples Workers Distribuidos con Redis

Este demo muestra:
1. Múltiples workers procesando de la misma cola de Redis
2. Workers corriendo en procesos separados (simula distribución)
3. Distribución automática de carga
4. Estadísticas agregadas
"""

import os
import sys
import time
import multiprocessing

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers import RedisTaskQueue, RedisWorker
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter, EdgesFilter


def worker_process(worker_id, queue_config, num_tasks_to_process=None):
    """
    Función que ejecuta un worker en un proceso separado.
    
    Args:
        worker_id: ID del worker
        queue_config: Configuración de la cola
        num_tasks_to_process: Número de tareas a procesar (None = todas)
    """
    # Reconectar a Redis (cada proceso necesita su propia conexión)
    queue = RedisTaskQueue(**queue_config)
    
    # Crear pipeline
    pipeline = FilterPipeline([
        BlurFilter(radius=1),
        BrightnessFilter(factor=1.2)
    ])
    
    # Crear worker
    worker = RedisWorker(
        worker_id=worker_id,
        pipeline=pipeline,
        queue=queue,
        poll_interval=0.2
    )
    
    # Procesar tareas
    worker.start()
    
    return worker.get_stats()


def main():
    print("👥 Demo: Múltiples Workers Distribuidos")
    print("=" * 70)
    
    # Verificar imagen
    image_path1 = "images/sample.jpg"
    image_path2 = "images/sample2.jpg"
    image_path3 = "images/sample2.jpg"
    
    images = [image_path1, image_path2, image_path3]
    
    for img_path in images:
        if not os.path.exists(img_path):
            print(f"❌ No se encontró: {img_path}")
            return
    
    os.makedirs("output", exist_ok=True)
    
    # ========================================================================
    # PASO 1: Conectar a Redis
    # ========================================================================
    print("\n🔌 PASO 1: Conectar a Redis")
    print("-" * 70)
    
    queue_config = {
        'host': 'localhost',
        'port': 6379,
        'queue_name': 'distributed_demo'
    }
    
    try:
        queue = RedisTaskQueue(**queue_config)
        print("✅ Conectado a Redis")
    except ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Inicia Redis primero:")
        print("   $ redis-server")
        print("   # O con Docker:")
        print("   $ docker run -d -p 6379:6379 redis:7-alpine")
        return
    
    # Limpiar cola
    queue.clear()
    print("✅ Cola limpia")
    
    # ========================================================================
    # PASO 2: Añadir Muchas Tareas
    # ========================================================================
    print("\n📦 PASO 2: Añadir 15 Tareas a Redis")
    print("-" * 70)
    
    num_tasks = 15
    
    for i in range(1, num_tasks + 1):
        target_img = (i - 1)%3
        
        task_id = queue.add_task({
            'name': f'Task {i}',
            'image_path': images[target_img],
            'output_path': f'output/distributed_task{i:02d}.jpg'
        })
        print(f"✅ Tarea {i:2d} añadida: {task_id}")
    
    stats = queue.get_stats()
    print(f"\n📊 Cola: {queue}")
    print(f"   Pendientes: {stats['pending']}")
    
    # ========================================================================
    # PASO 3: Lanzar Múltiples Workers en Procesos Separados
    # ========================================================================
    print("\n⚙️  PASO 3: Lanzar 3 Workers en Procesos Separados")
    print("=" * 70)
    print("(Cada worker corre en su propio proceso, simulando distribución)")
    print("-" * 70)
    
    num_workers = 10
    processes = []
    
    start_time = time.time()
    
    for i in range(num_workers):
        worker_id = f'distributed-worker-{i+1}'
        
        # Crear proceso
        process = multiprocessing.Process(
            target=worker_process,
            args=(worker_id, queue_config)
        )
        
        processes.append(process)
        process.start()
        print(f"▶️  Worker {i+1} iniciado en proceso {process.pid}")
    
    # Esperar a que todos terminen
    print(f"\n⏳ Esperando a que los {num_workers} workers terminen...")
    for i, process in enumerate(processes, 1):
        process.join()
        print(f"✅ Worker {i} terminó")
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Todos los workers han terminado")
    
    # ========================================================================
    # PASO 4: Analizar Resultados
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADOS AGREGADOS")
    print("=" * 70)
    
    final_stats = queue.get_stats()
    
    print(f"\n🔴 Cola de Redis:")
    print(f"   Total de tareas: {final_stats['total']}")
    print(f"   ✅ Completadas: {final_stats['completed']}")
    print(f"   ❌ Fallidas: {final_stats['failed']}")
    print(f"   Pendientes: {final_stats['pending']}")
    
    print(f"\n⚡ Performance:")
    print(f"   Tiempo total: {total_time:.3f}s")
    print(f"   Workers: {num_workers}")
    print(f"   Throughput: {final_stats['completed'] / total_time:.2f} tareas/segundo")
    
    # Obtener resultados de Redis
    print(f"\n📋 Resultados (primeros 10):")
    results = queue.get_completed_results(limit=10)
    
    # Agrupar por worker
    worker_task_counts = {}
    for result in results:
        worker_id = result.get('worker_id', 'unknown')
        worker_task_counts[worker_id] = worker_task_counts.get(worker_id, 0) + 1
    
    print(f"\n👥 Distribución de Carga:")
    for worker_id, count in sorted(worker_task_counts.items()):
        print(f"   • {worker_id}: {count} tareas")
    
    # Mostrar algunos resultados
    print(f"\n📄 Detalles de Tareas (primeras 5):")
    for result in results[:5]:
        task_id = result.get('task_id', 'unknown')
        worker_id = result.get('worker_id', 'unknown')
        total_time_task = result.get('total_time', 'N/A')
        
        print(f"   • {task_id}")
        print(f"     Worker: {worker_id}")
        print(f"     Tiempo: {total_time_task}")
    
    # Archivos generados
    print(f"\n📁 Archivos Generados ({final_stats['completed']} archivos):")
    output_files = []
    for i in range(1, num_tasks + 1):
        output_file = f'output/distributed_task{i:02d}.jpg'
        if os.path.exists(output_file):
            output_files.append(output_file)
    
    for output_file in output_files[:6]:  # Primeros 6
        size = os.path.getsize(output_file) / 1024
        print(f"   • {os.path.basename(output_file)} ({size:.1f} KB)")
    
    if len(output_files) > 6:
        print(f"   ... y {len(output_files) - 6} archivos más")
    
    # ========================================================================
    # Análisis de Escalabilidad
    # ========================================================================
    print("\n" + "=" * 70)
    print("🔬 ANÁLISIS DE ESCALABILIDAD")
    print("=" * 70)
    
    # Estimar tiempo secuencial
    avg_task_time = 0.15  # Estimado
    sequential_time = num_tasks * avg_task_time
    speedup = sequential_time / total_time
    efficiency = (speedup / num_workers) * 100
    
    print(f"""
    Escenario: {num_tasks} tareas, {num_workers} workers distribuidos
    
    Tiempo estimado secuencial (1 worker):
    - {sequential_time:.3f}s
    
    Tiempo real paralelo ({num_workers} workers):
    - {total_time:.3f}s
    
    Speedup: {speedup:.2f}x
    Eficiencia: {efficiency:.1f}%
    
    Ventajas de Redis sobre threading (Sesión 3):
    - ✓ Verdadero paralelismo (multiprocessing, sin GIL)
    - ✓ Workers pueden estar en máquinas diferentes
    - ✓ Persistencia de tareas
    - ✓ Fácil de escalar (añadir más workers)
    - ✓ Tolerancia a fallos (workers pueden reiniciar)
    """)
    
    # ========================================================================
    # Demostrar Distribución Real
    # ========================================================================
    print("\n" + "=" * 70)
    print("🌍 DISTRIBUCIÓN REAL")
    print("=" * 70)
    
    print("""
    En producción, podrías tener:
    
    Máquina 1 (Producer):
    - API que recibe requests
    - Añade tareas a Redis
    
    Máquina 2 (Worker):
    - Worker 1 conectado a Redis
    - Worker 2 conectado a Redis
    
    Máquina 3 (Worker):
    - Worker 3 conectado a Redis
    - Worker 4 conectado a Redis
    
    Máquina 4 (Redis):
    - Redis server (cola centralizada)
    
    Todos se comunican a través de Redis.
    Si un worker falla, los otros continúan.
    Puedes añadir/quitar workers dinámicamente.
    """)
    
    # ========================================================================
    # Resumen
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADO")
    print("=" * 70)
    
    print(f"\n💡 Conceptos demostrados:")
    print(f"   ✓ {num_workers} workers en procesos separados")
    print(f"   ✓ Procesamiento distribuido con Redis")
    print(f"   ✓ Distribución automática de carga")
    print(f"   ✓ Speedup de {speedup:.2f}x")
    print(f"   ✓ Verdadero paralelismo (sin GIL)")
    
    print(f"\n🎯 Próximos pasos:")
    print(f"   • Sesión 5: Health checks y auto-recovery")
    print(f"   • Sesión 6: Docker para workers")
    print(f"   • Sesión 8: Kubernetes auto-scaling")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Necesario para multiprocessing en Windows/Mac
    multiprocessing.set_start_method('spawn', force=True)
    main()

