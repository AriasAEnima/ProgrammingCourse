#!/usr/bin/env python3
"""
Demo: Múltiples Workers en Paralelo

Este demo muestra:
1. Varios workers procesando de la misma cola
2. Uso de threading para paralelismo
3. Coordinación entre workers
4. Estadísticas agregadas
"""

import os
import sys
import time
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers import SimpleWorker, TaskQueue
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter


def main():
    print("👥 Demo: Múltiples Workers")
    print("=" * 70)
    
    # Verificar imagen
    image_path = "images/sample.jpg"
    if not os.path.exists(image_path):
        print(f"❌ No se encontró: {image_path}")
        return
    
    os.makedirs("output", exist_ok=True)
    
    # ========================================================================
    # PASO 1: Crear Pipeline
    # ========================================================================
    print("\n📋 PASO 1: Crear Pipeline")
    print("-" * 70)
    
    pipeline = FilterPipeline([
        BlurFilter(radius=2),
        BrightnessFilter(factor=1.3)
    ])
    
    print(f"✅ Pipeline: {pipeline}")
    
    # ========================================================================
    # PASO 2: Crear Cola con Muchas Tareas
    # ========================================================================
    print("\n📦 PASO 2: Crear Cola con 12 Tareas")
    print("-" * 70)
    
    queue = TaskQueue()
    
    # Añadir 12 tareas
    for i in range(1, 13):
        task_id = queue.add_task({
            'name': f'Task {i}',
            'image_path': image_path,
            'output_path': f'output/multi_worker_task{i}.jpg'
        })
        print(f"✅ Tarea {i:2d} añadida: {task_id}")
    
    print(f"\n📊 Cola inicial: {queue}")
    
    # ========================================================================
    # PASO 3: Crear Múltiples Workers
    # ========================================================================
    print("\n👥 PASO 3: Crear 3 Workers")
    print("-" * 70)
    
    num_workers = 3
    workers = []
    threads = []
    
    for i in range(num_workers):
        worker = SimpleWorker(
            worker_id=f'worker-{i+1}',
            pipeline=pipeline,
            queue=queue,
            poll_interval=0.1  # Poll rápido para demo
        )
        workers.append(worker)
        print(f"✅ Worker {i+1} creado: {worker.worker_id}")
    
    # ========================================================================
    # PASO 4: Iniciar Workers en Threads
    # ========================================================================
    print("\n🔄 PASO 4: Iniciando Workers")
    print("=" * 70)
    print("(Los 3 workers procesarán tareas en paralelo)")
    print("-" * 70)
    
    start_time = time.time()
    
    # Crear y arrancar threads
    for worker in workers:
        # Crear función wrapper que procesa hasta que no haya más tareas
        def worker_function(w):
            w.is_running = True
            w.stats['start_time'] = time.time()
            w.logger.info(f"🚀 Worker {w.worker_id} iniciado")
            
            while not queue.is_empty() or len(queue.processing) > 0:
                task = queue.get_task(w.worker_id)
                
                if task:
                    w.current_task = task
                    task_id = task.get('id')
                    
                    try:
                        result = w.process_task(task)
                        queue.mark_completed(task_id, result)
                    except Exception as e:
                        queue.mark_failed(task_id, str(e))
                    finally:
                        w.current_task = None
                else:
                    time.sleep(w.poll_interval)
            
            w.is_running = False
        
        thread = threading.Thread(target=worker_function, args=(worker,))
        threads.append(thread)
        thread.start()
        print(f"▶️  Thread iniciado para {worker.worker_id}")
    
    # Esperar a que todos terminen
    print(f"\n⏳ Esperando a que los workers terminen...")
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Todos los workers han terminado")
    
    # ========================================================================
    # PASO 5: Resultados Agregados
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADOS AGREGADOS")
    print("=" * 70)
    
    queue_stats = queue.get_stats()
    
    print(f"\n📦 Cola:")
    print(f"   Total de tareas: {queue_stats['total']}")
    print(f"   ✅ Completadas: {queue_stats['completed']}")
    print(f"   ❌ Fallidas: {queue_stats['failed']}")
    print(f"   ⏱️  Tiempo total: {total_time:.3f}s")
    
    print(f"\n👥 Workers (Estadísticas Individuales):")
    print("-" * 70)
    
    total_tasks = 0
    total_processing_time = 0
    
    for i, worker in enumerate(workers, 1):
        stats = worker.get_stats()
        total_tasks += stats['tasks_completed']
        total_processing_time += stats['total_processing_time']
        
        print(f"\n   Worker {i} ({worker.worker_id}):")
        print(f"      Tareas completadas: {stats['tasks_completed']}")
        print(f"      Tiempo de procesamiento: {stats['total_processing_time']:.3f}s")
        
        if stats['tasks_completed'] > 0:
            avg = stats['total_processing_time'] / stats['tasks_completed']
            print(f"      Tiempo promedio: {avg:.3f}s")
    
    # Estadísticas agregadas
    print(f"\n📊 Resumen Agregado:")
    print(f"   Total tareas procesadas: {total_tasks}")
    print(f"   Tiempo total de procesamiento: {total_processing_time:.3f}s")
    print(f"   Tiempo real transcurrido: {total_time:.3f}s")
    
    # Calcular eficiencia
    if total_time > 0:
        efficiency = (total_processing_time / total_time) / num_workers
        speedup = total_processing_time / total_time
        print(f"\n⚡ Performance:")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Eficiencia: {efficiency:.1%}")
        print(f"   Throughput: {total_tasks / total_time:.2f} tareas/segundo")
    
    # Archivos generados
    print(f"\n📁 Archivos Generados ({queue_stats['completed']} archivos):")
    output_files = sorted([
        f"output/multi_worker_task{i}.jpg" 
        for i in range(1, 13)
        if os.path.exists(f"output/multi_worker_task{i}.jpg")
    ])
    
    for output_file in output_files[:6]:  # Mostrar primeros 6
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"   • {os.path.basename(output_file)} ({size:.1f} KB)")
    
    if len(output_files) > 6:
        print(f"   ... y {len(output_files) - 6} archivos más")
    
    # ========================================================================
    # Análisis
    # ========================================================================
    print("\n" + "=" * 70)
    print("🔬 ANÁLISIS DE PERFORMANCE")
    print("=" * 70)
    
    sequential_time = total_processing_time
    parallel_time = total_time
    theoretical_speedup = num_workers
    actual_speedup = sequential_time / parallel_time
    
    print(f"""
    Escenario: {queue_stats['total']} tareas, {num_workers} workers
    
    Tiempo secuencial (1 worker):
    - Estimado: {sequential_time:.3f}s
    
    Tiempo paralelo ({num_workers} workers):
    - Real: {parallel_time:.3f}s
    
    Speedup teórico: {theoretical_speedup:.1f}x
    Speedup real: {actual_speedup:.2f}x
    
    ¿Por qué no es {theoretical_speedup}x perfecto?
    - Overhead de threading
    - Contención en la cola (lock)
    - Tareas no perfectamente balanceadas
    - Python GIL (Global Interpreter Lock)
    
    Nota: Para mejor paralelismo, usar multiprocessing
          (se verá en Sesión 5)
    """)
    
    # ========================================================================
    # Resumen
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADO")
    print("=" * 70)
    
    print(f"\n💡 Conceptos demostrados:")
    print(f"   ✓ Múltiples workers ({num_workers}) procesando en paralelo")
    print(f"   ✓ Threading para concurrencia")
    print(f"   ✓ TaskQueue thread-safe")
    print(f"   ✓ Speedup de {actual_speedup:.2f}x")
    print(f"   ✓ Distribución automática de carga")
    
    print(f"\n🎯 Aplicaciones:")
    print(f"   ✓ Procesamiento batch de imágenes")
    print(f"   ✓ Servidor de procesamiento (múltiples workers)")
    print(f"   ✓ Pipeline de datos en paralelo")
    
    print(f"\n📚 Próximos pasos:")
    print(f"   • Sesión 4: Redis para cola distribuida")
    print(f"   • Sesión 5: Multiprocessing para mejor paralelismo")
    print(f"   • Sesión 8: Kubernetes auto-scaling")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

