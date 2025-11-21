#!/usr/bin/env python3
"""
Demo: SimpleWorker - Worker síncrono básico

Este demo muestra:
1. Crear una cola de tareas
2. Crear un worker con pipeline
3. Procesar tareas automáticamente
4. Ver logs y estadísticas
"""

import os
import sys
import time

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers import SimpleWorker, TaskQueue
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter, EdgesFilter, GrayscaleFilter


def main():
    print("⚙️  Demo: SimpleWorker")
    print("=" * 70)
    
    # Verificar imagen
    image_path = "images/sample.jpg"
    if not os.path.exists(image_path):
        print(f"❌ No se encontró: {image_path}")
        return
    
    # Crear directorio de salida
    os.makedirs("output", exist_ok=True)
    
    # ========================================================================
    # PASO 1: Crear Pipeline
    # ========================================================================
    print("\n📋 PASO 1: Crear Pipeline de Filtros")
    print("-" * 70)
    
    pipeline = FilterPipeline([
        BlurFilter(radius=2),
        BrightnessFilter(factor=1.2),
        EdgesFilter()
    ])
    
    print(f"✅ Pipeline creado: {pipeline}")
    print(f"   Filtros: {pipeline.get_filter_names()}")
    
    # ========================================================================
    # PASO 2: Crear Cola de Tareas
    # ========================================================================
    print("\n📦 PASO 2: Crear Cola de Tareas")
    print("-" * 70)
    
    queue = TaskQueue()
    
    # Añadir múltiples tareas (variaciones del mismo pipeline)
    tasks_config = [
        {
            'name': 'Task 1: Basic Pipeline',
            'image_path': image_path,
            'output_path': 'output/worker_task1.jpg'
        },
        {
            'name': 'Task 2: Same Pipeline',
            'image_path': image_path,
            'output_path': 'output/worker_task2.jpg'
        },
        {
            'name': 'Task 3: Another',
            'image_path': image_path,
            'output_path': 'output/worker_task3.jpg'
        },
    ]
    
    for task_config in tasks_config:
        task_id = queue.add_task(task_config)
        print(f"✅ Tarea añadida: {task_id} - {task_config['name']}")
    
    print(f"\n📊 Estado de la cola: {queue}")
    
    # ========================================================================
    # PASO 3: Crear Worker
    # ========================================================================
    print("\n⚙️  PASO 3: Crear Worker")
    print("-" * 70)
    
    worker = SimpleWorker(
        worker_id='demo-worker-1',
        pipeline=pipeline,
        queue=queue,
        poll_interval=0.5  # Revisar cola cada 0.5s
    )
    
    print(f"✅ Worker creado: {worker}")
    
    # ========================================================================
    # PASO 4: Procesar Tareas
    # ========================================================================
    print("\n🔄 PASO 4: Procesando Tareas")
    print("=" * 70)
    print("(El worker procesará tareas automáticamente)")
    print("(Presiona Ctrl+C para detener después de que termine)")
    print("-" * 70)
    
    start_time = time.time()
    
    try:
        # Iniciar worker en thread separado o procesar hasta que no haya más tareas
        # Para este demo, procesamos hasta que la cola esté vacía
        worker.is_running = True
        worker.stats['start_time'] = time.time()
        worker.logger.info(f"🚀 Worker {worker.worker_id} iniciado")
        
        while not queue.is_empty() or len(queue.processing) > 0:
            task = queue.get_task(worker.worker_id)
            
            if task:
                worker.current_task = task
                task_id = task.get('id')
                
                try:
                    result = worker.process_task(task)
                    queue.mark_completed(task_id, result)
                except Exception as e:
                    queue.mark_failed(task_id, str(e))
                finally:
                    worker.current_task = None
            else:
                # Ya no hay más tareas
                break
        
        worker.is_running = False
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada, deteniendo worker...")
        worker.stop()
    
    total_time = time.time() - start_time
    
    # ========================================================================
    # PASO 5: Resultados y Estadísticas
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADOS Y ESTADÍSTICAS")
    print("=" * 70)
    
    # Estadísticas de la cola
    queue_stats = queue.get_stats()
    print(f"\n📦 Cola:")
    print(f"   Total de tareas: {queue_stats['total']}")
    print(f"   ✅ Completadas: {queue_stats['completed']}")
    print(f"   ❌ Fallidas: {queue_stats['failed']}")
    print(f"   🔄 En proceso: {queue_stats['processing']}")
    print(f"   ⏳ Pendientes: {queue_stats['pending']}")
    
    # Estadísticas del worker
    worker_stats = worker.get_stats()
    print(f"\n⚙️  Worker '{worker.worker_id}':")
    print(f"   Tareas completadas: {worker_stats['tasks_completed']}")
    print(f"   Tareas fallidas: {worker_stats['tasks_failed']}")
    print(f"   Tiempo total procesamiento: {worker_stats['total_processing_time']:.3f}s")
    
    if worker_stats['tasks_completed'] > 0:
        avg_time = worker_stats['total_processing_time'] / worker_stats['tasks_completed']
        print(f"   Tiempo promedio por tarea: {avg_time:.3f}s")
    
    print(f"   Tasa de éxito: {worker_stats['success_rate']:.1%}")
    print(f"   Tiempo total: {total_time:.3f}s")
    
    # Detalles de tareas completadas
    if queue.completed:
        print(f"\n✅ Tareas Completadas:")
        for i, task in enumerate(queue.completed, 1):
            print(f"\n   {i}. {task['id']}")
            print(f"      Entrada: {task.get('image_path', 'N/A')}")
            print(f"      Salida: {task.get('output_path', 'N/A')}")
            
            if 'result' in task and 'times' in task['result']:
                times = task['result']['times']
                print(f"      Tiempo total: {times['total']:.3f}s")
                print(f"         - Carga: {times['load']:.3f}s")
                print(f"         - Pipeline: {times['pipeline']:.3f}s")
                print(f"         - Guardado: {times['save']:.3f}s")
    
    # Archivos generados
    print(f"\n📁 Archivos Generados:")
    for task in queue.completed:
        if 'result' in task:
            output_path = task['result'].get('output_path')
            if output_path and os.path.exists(output_path):
                size = os.path.getsize(output_path) / 1024  # KB
                print(f"   • {output_path} ({size:.1f} KB)")
    
    # ========================================================================
    # Resumen Final
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADO")
    print("=" * 70)
    
    print(f"\n🎯 Resumen:")
    print(f"   • Pipeline con {len(pipeline)} filtros")
    print(f"   • {queue_stats['total']} tareas procesadas")
    print(f"   • {worker_stats['tasks_completed']} exitosas, {worker_stats['tasks_failed']} fallidas")
    print(f"   • Tiempo total: {total_time:.3f}s")
    
    print(f"\n💡 Conceptos demostrados:")
    print(f"   ✓ Patrón Worker (BaseWorker → SimpleWorker)")
    print(f"   ✓ Cola de tareas (TaskQueue)")
    print(f"   ✓ Procesamiento síncrono")
    print(f"   ✓ Logging estructurado")
    print(f"   ✓ Estadísticas y monitoreo")
    
    print(f"\n📚 Próximo paso:")
    print(f"   • Ejecuta otros demos para ver workers asíncronos")
    print(f"   • En Sesión 4 veremos Redis para colas distribuidas")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

