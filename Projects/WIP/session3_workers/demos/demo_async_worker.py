#!/usr/bin/env python3
"""
Demo: AsyncWorker - Worker Asíncrono

Este demo muestra:
1. Worker que procesa tareas concurrentemente
2. Ventajas de asyncio para I/O-bound tasks
3. Comparación de performance con SimpleWorker
"""

import os
import sys
import time
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers import AsyncWorker, TaskQueue
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter, EdgesFilter


def main():
    print("⚡ Demo: AsyncWorker (Asíncrono)")
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
        BrightnessFilter(factor=1.2),
        EdgesFilter()
    ])
    
    print(f"✅ Pipeline: {pipeline}")
    
    # ========================================================================
    # PASO 2: Crear Múltiples Tareas
    # ========================================================================
    print("\n📦 PASO 2: Crear Cola con 6 Tareas")
    print("-" * 70)
    
    queue = TaskQueue()
    
    # Añadir 6 tareas (simula procesamiento de múltiples imágenes)
    for i in range(1, 7):
        task_id = queue.add_task({
            'name': f'Async Task {i}',
            'image_path': image_path,
            'output_path': f'output/async_task{i}.jpg'
        })
        print(f"✅ Tarea {i} añadida: {task_id}")
    
    print(f"\n📊 Cola: {queue}")
    
    # ========================================================================
    # PASO 3: Crear AsyncWorker
    # ========================================================================
    print("\n⚡ PASO 3: Crear AsyncWorker")
    print("-" * 70)
    
    worker = AsyncWorker(
        worker_id='async-worker-1',
        pipeline=pipeline,
        queue=queue,
        poll_interval=0.5,
        max_concurrent=3  # Procesa hasta 3 tareas a la vez
    )
    
    print(f"✅ Worker creado: {worker}")
    print(f"   Max concurrencia: {worker.max_concurrent} tareas")
    
    # ========================================================================
    # PASO 4: Procesar Tareas Asíncronamente
    # ========================================================================
    print("\n🔄 PASO 4: Procesando Tareas (Asíncrono)")
    print("=" * 70)
    print("(El worker procesa hasta 3 tareas concurrentemente)")
    print("-" * 70)
    
    async def run_worker():
        """Función async para ejecutar el worker."""
        # Crear tarea para el worker
        worker_task = asyncio.create_task(worker.start())
        
        # Esperar hasta que la cola esté vacía
        while not queue.is_empty() or len(queue.processing) > 0:
            await asyncio.sleep(0.5)
        
        # Detener worker
        worker.stop()
        
        # Esperar a que termine
        try:
            await asyncio.wait_for(worker_task, timeout=2.0)
        except asyncio.TimeoutError:
            pass
    
    # Ejecutar
    start_time = time.time()
    asyncio.run(run_worker())
    total_time = time.time() - start_time
    
    # ========================================================================
    # PASO 5: Resultados
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADOS")
    print("=" * 70)
    
    queue_stats = queue.get_stats()
    worker_stats = worker.get_stats()
    
    print(f"\n📦 Cola:")
    print(f"   ✅ Completadas: {queue_stats['completed']}/{queue_stats['total']}")
    print(f"   ❌ Fallidas: {queue_stats['failed']}")
    
    print(f"\n⚡ AsyncWorker '{worker.worker_id}':")
    print(f"   Tareas completadas: {worker_stats['tasks_completed']}")
    print(f"   Tiempo total: {worker_stats['total_processing_time']:.3f}s")
    
    if worker_stats['tasks_completed'] > 0:
        avg_time = worker_stats['total_processing_time'] / worker_stats['tasks_completed']
        print(f"   Tiempo promedio: {avg_time:.3f}s por tarea")
    
    print(f"   Tiempo real transcurrido: {total_time:.3f}s")
    
    # Calcular mejora por concurrencia
    if worker_stats['tasks_completed'] > 0:
        sequential_time = worker_stats['total_processing_time']
        speedup = sequential_time / total_time
        print(f"\n⚡ Speedup por concurrencia: {speedup:.2f}x")
        print(f"   (Si fuera secuencial: {sequential_time:.3f}s)")
        print(f"   (Con async: {total_time:.3f}s)")
    
    # Archivos generados
    print(f"\n📁 Archivos Generados:")
    for task in queue.completed:
        if 'result' in task:
            output_path = task['result'].get('output_path')
            if output_path and os.path.exists(output_path):
                size = os.path.getsize(output_path) / 1024
                print(f"   • {os.path.basename(output_path)} ({size:.1f} KB)")
    
    # ========================================================================
    # Comparación con SimpleWorker
    # ========================================================================
    print("\n" + "=" * 70)
    print("🔬 COMPARACIÓN: Async vs Simple Worker")
    print("=" * 70)
    
    print("""
    Resultados esperados para 6 tareas:
    
    SimpleWorker (secuencial):
    - Procesa 1 tarea a la vez
    - Tiempo ≈ 0.2s × 6 = 1.2s
    
    AsyncWorker (concurrent=3):
    - Procesa 3 tareas a la vez
    - Tiempo ≈ 0.2s × 2 = 0.4s
    - Speedup: ~3x ⚡
    
    Nota: El speedup real depende de:
    - Tamaño de imágenes
    - I/O vs CPU bound
    - Número de CPUs disponibles
    """)
    
    # ========================================================================
    # Resumen
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADO")
    print("=" * 70)
    
    print(f"\n💡 Conceptos demostrados:")
    print(f"   ✓ Worker asíncrono con asyncio")
    print(f"   ✓ Procesamiento concurrente (hasta {worker.max_concurrent} tareas)")
    print(f"   ✓ Mejora de performance para I/O-bound tasks")
    print(f"   ✓ Semáforo para limitar concurrencia")
    
    print(f"\n🎯 Cuándo usar AsyncWorker:")
    print(f"   ✓ Muchas imágenes (alto throughput)")
    print(f"   ✓ Tareas I/O-bound (lectura/escritura)")
    print(f"   ✓ Necesitas maximizar uso de recursos")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

