"""
Demo 2: Auto-Recovery - Reintentos automáticos y Dead Letter Queue.

Demuestra:
- Tareas que fallan se reintentan automáticamente
- Después de max_retries, van a Dead Letter Queue
- Recuperar tareas atascadas
- Reintentar manualmente desde DLQ
"""
import time
import sys
from pathlib import Path

# Agregar parent dir al path
sys.path.append(str(Path(__file__).parent.parent))

from workers import RedisTaskQueueV2


def main():
    print("=" * 60)
    print("DEMO 2: Auto-Recovery y Dead Letter Queue")
    print("=" * 60)
    print()
    
    # Crear cola con max_retries=3
    queue = RedisTaskQueueV2(max_retries=3)
    queue.clear()
    
    # === Paso 1: Agregar tareas ===
    print("📥 Paso 1: Agregando 3 tareas...")
    task1_id = queue.add_task({"input_path": "images/sample.jpg", "output_path": "output/test1.jpg"})
    task2_id = queue.add_task({"input_path": "images/sample.jpg", "output_path": "output/test2.jpg"})
    task3_id = queue.add_task({"input_path": "images/sample.jpg", "output_path": "output/test3.jpg"})
    print()
    
    # === Paso 2: Ver estadísticas iniciales ===
    print("📊 Paso 2: Estadísticas iniciales:")
    stats = queue.get_stats()
    print(f"  pending: {stats['pending']}")
    print(f"  processing: {stats['processing']}")
    print(f"  completed: {stats['completed']}")
    print(f"  dead_letter: {stats['dead_letter']}")
    print()
    
    # === Paso 3: Simular procesamiento y fallos ===
    print("💥 Paso 3: Simulando fallos en la primera tarea...")
    
    # Intento 1: fallar
    task = queue.get_task("test-worker", timeout=1)
    failing_task_id = task['task_id']
    print(f"  Intento 1: {task['task_id']} (retry={task['retry_count']})")
    queue.mark_failed(failing_task_id, "Error simulado #1")
    time.sleep(0.5)
    
    # Intento 2: fallar
    task = queue.get_task("test-worker", timeout=1)
    print(f"  Intento 2: {task['task_id']} (retry={task['retry_count']})")
    queue.mark_failed(failing_task_id, "Error simulado #2")
    time.sleep(0.5)
    
    # Intento 3: fallar
    task = queue.get_task("test-worker", timeout=1)
    print(f"  Intento 3: {task['task_id']} (retry={task['retry_count']})")
    queue.mark_failed(failing_task_id, "Error simulado #3")
    time.sleep(0.5)
    
    # Intento 4: fallar (va a DLQ)
    task = queue.get_task("test-worker", timeout=1)
    if task:
        print(f"  Intento 4: {task['task_id']} (retry={task['retry_count']})")
        queue.mark_failed(failing_task_id, "Error simulado #4 - DLQ")
    print()
    
    # === Paso 4: Ver estadísticas después de fallos ===
    print("📊 Paso 4: Estadísticas después de fallos:")
    stats = queue.get_stats()
    print(f"  pending: {stats['pending']}")
    print(f"  dead_letter: {stats['dead_letter']} 💀")
    print()
    
    # === Paso 5: Ver tareas en DLQ ===
    print("💀 Paso 5: Tareas en Dead Letter Queue:")
    dlq_tasks = queue.get_dead_letter_tasks()
    for task_id in dlq_tasks:
        print(f"  - {task_id}")
    print()
    
    # === Paso 6: Reintentar manualmente desde DLQ ===
    print("🔄 Paso 6: Reintentando tarea desde DLQ...")
    queue.retry_dead_letter_task(failing_task_id)
    print()
    
    # === Paso 7: Completar tareas exitosas ===
    print("✅ Paso 7: Completando tareas restantes...")
    
    # Completar todas las tareas pendientes
    while True:
        task = queue.get_task("test-worker", timeout=1)
        if not task:
            break
        print(f"  Completando {task['task_id']} (retry={task['retry_count']})")
        queue.mark_completed(task['task_id'])
    print()
    
    # === Paso 8: Estadísticas finales ===
    print("📊 Paso 8: Estadísticas finales:")
    stats = queue.get_stats()
    print(f"  pending: {stats['pending']}")
    print(f"  processing: {stats['processing']}")
    print(f"  completed: {stats['completed']} ✅")
    print(f"  dead_letter: {stats['dead_letter']}")
    print()
    
    print("=" * 60)
    print("✅ Demo completado!")
    print("=" * 60)


if __name__ == "__main__":
    main()

