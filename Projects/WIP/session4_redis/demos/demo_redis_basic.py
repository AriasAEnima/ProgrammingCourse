#!/usr/bin/env python3
"""
Demo: RedisWorker Básico

Este demo muestra:
1. Conexión a Redis
2. Cola de tareas en Redis
3. Worker procesando tareas de Redis
4. Persistencia de tareas
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers import RedisTaskQueue, RedisWorker
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter, GrayscaleFilter


def main():
    print("🔴 Demo: RedisWorker Básico")
    print("=" * 70)
    
    # Verificar imagen
    image_path = "images/sample.jpg"
    image_path2 = "images/sample2.jpg"
    image_path3 = "images/sample2.jpg"
    
    images = [image_path, image_path2, image_path3]
    
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
    
    try:
        queue = RedisTaskQueue(host='localhost', port=6379)
        print("✅ Conectado a Redis")
        print(f"   Host: localhost:6379")
        print(f"   Cola: {queue.queue_name}")
    except ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Soluciones:")
        print("   1. Iniciar Redis localmente:")
        print("      $ redis-server")
        print("\n   2. O usar Docker:")
        print("      $ docker run -d -p 6379:6379 redis:7-alpine")
        return
    
    # Limpiar cola anterior (para demo limpio)
    queue.clear()
    print("✅ Cola limpia")
    
    # ========================================================================
    # PASO 2: Añadir Tareas a Redis
    # ========================================================================
    print("\n📦 PASO 2: Añadir 3 Tareas a Redis")
    print("-" * 70)
    
    tasks = [
        {
            'name': 'Tarea 1: Brightness',
            'image_path': image_path,
            'output_path': 'output/redis_Brightness.jpg'
        },
        {
            'name': 'Tarea 2: Blur',
            'image_path': image_path2,
            'output_path': 'output/redis_blur.jpg'
        },
        {
            'name': 'Tarea 3: Combined',
            'image_path': image_path3,
            'output_path': 'output/redis_grayscale.jpg'
        }
    ]
    
    task_ids = []
    for task in tasks:
        task_id = queue.add_task(task)
        task_ids.append(task_id)
        print(f"✅ {task['name']} → {task_id}")
    
    # Ver estadísticas
    stats = queue.get_stats()
    print(f"\n📊 Cola: {queue}")
    print(f"   Pendientes: {stats['pending']}")
    print(f"   Total: {stats['total']}")
    
    # ========================================================================
    # PASO 3: Crear Pipeline
    # ========================================================================
    print("\n📋 PASO 3: Crear Pipeline de Filtros")
    print("-" * 70)
    
    pipeline = FilterPipeline([
        BrightnessFilter(factor=1.8),
        BlurFilter(radius=2),
        GrayscaleFilter(),
    ])
    
    print(f"✅ Pipeline: {pipeline}")
    
    # ========================================================================
    # PASO 4: Crear y Ejecutar Worker
    # ========================================================================
    print("\n⚙️  PASO 4: Crear y Ejecutar Worker")
    print("=" * 70)
    print("(El worker procesará todas las tareas de Redis)")
    print("-" * 70)
    
    worker = RedisWorker(
        worker_id='redis-worker-1',
        pipeline=pipeline,
        queue=queue,
        poll_interval=0.5
    )
    
    print(f"✅ Worker creado: {worker}")
    
    # Iniciar worker (procesa hasta que la cola esté vacía)
    start_time = time.time()
    worker.start()
    total_time = time.time() - start_time
    
    # ========================================================================
    # PASO 5: Verificar Resultados en Redis
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADOS")
    print("=" * 70)
    
    queue_stats = queue.get_stats()
    worker_stats = worker.get_stats()
    
    print(f"\n🔴 Cola de Redis:")
    print(f"   Pendientes: {queue_stats['pending']}")
    print(f"   En proceso: {queue_stats['processing']}")
    print(f"   ✅ Completadas: {queue_stats['completed']}")
    print(f"   ❌ Fallidas: {queue_stats['failed']}")
    
    print(f"\n⚙️  Worker '{worker.worker_id}':")
    print(f"   Tareas completadas: {worker_stats['tasks_completed']}")
    print(f"   Tareas fallidas: {worker_stats['tasks_failed']}")
    print(f"   Tasa de éxito: {worker_stats['success_rate']:.1%}")
    print(f"   Tiempo total: {total_time:.3f}s")
    
    if worker_stats['tasks_completed'] > 0:
        avg_time = worker_stats['total_processing_time'] / worker_stats['tasks_completed']
        print(f"   Tiempo promedio: {avg_time:.3f}s por tarea")
    
    # Obtener resultados de Redis
    print(f"\n📋 Resultados Guardados en Redis:")
    results = queue.get_completed_results(limit=10)
    
    for result in results:
        task_id = result.get('task_id', 'unknown')
        output_path = result.get('output_path', 'N/A')
        total_time_task = result.get('total_time', 'N/A')
        
        print(f"   • {task_id}:")
        print(f"     Output: {output_path}")
        print(f"     Tiempo: {total_time_task}")
    
    # Archivos generados
    print(f"\n📁 Archivos Generados:")
    for task in tasks:
        output_file = task['output_path']
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"   • {os.path.basename(output_file)} ({size:.1f} KB)")
    
    # ========================================================================
    # PASO 6: Demostrar Persistencia
    # ========================================================================
    print("\n" + "=" * 70)
    print("💾 PERSISTENCIA DE REDIS")
    print("=" * 70)
    
    print("""
    Las tareas y resultados están en Redis, no en memoria.
    
    Esto significa:
    - ✓ Sobreviven reinicios del worker
    - ✓ Múltiples workers pueden leer de la misma cola
    - ✓ Workers pueden estar en diferentes máquinas
    - ✓ Puedes inspeccionar la cola con redis-cli
    
    Comandos útiles de redis-cli:
    
    # Ver todas las keys
    $ redis-cli KEYS "*"
    
    # Ver tareas pendientes
    $ redis-cli LRANGE image_processing:pending 0 -1
    
    # Ver tareas completadas
    $ redis-cli LRANGE image_processing:completed 0 -1
    
    # Ver detalles de una tarea
    $ redis-cli HGETALL task:TASK_ID
    """)
    
    # Mostrar algunas keys actuales
    print("🔑 Keys actuales en Redis:")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        keys = r.keys(f"{queue.queue_name}:*")
        for key in keys[:10]:  # Primeras 10
            print(f"   • {key}")
        if len(keys) > 10:
            print(f"   ... y {len(keys) - 10} más")
    except Exception as e:
        print(f"   (No se pudieron listar: {e})")
    
    # ========================================================================
    # Resumen
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADO")
    print("=" * 70)
    
    print(f"\n💡 Conceptos demostrados:")
    print(f"   ✓ Conexión a Redis")
    print(f"   ✓ Cola distribuida (RedisTaskQueue)")
    print(f"   ✓ Worker procesando desde Redis")
    print(f"   ✓ Persistencia de tareas y resultados")
    print(f"   ✓ Operaciones atómicas (RPOPLPUSH)")
    
    print(f"\n🎯 Ventajas sobre cola en memoria:")
    print(f"   ✓ Distribuida (múltiples workers/máquinas)")
    print(f"   ✓ Persistente (sobrevive reinicios)")
    print(f"   ✓ Escalable (Redis puede manejar millones)")
    print(f"   ✓ Observable (redis-cli para inspeccionar)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

