"""
Módulo de Workers para procesamiento de tareas.

Este módulo contiene:
- BaseWorker: Clase base abstracta
- SimpleWorker: Worker síncrono
- TaskQueue: Cola de tareas en memoria

Uso:
    from workers import SimpleWorker, TaskQueue
    
    queue = TaskQueue()
    worker = SimpleWorker('worker-1', pipeline, queue)
    worker.start()
"""

from .base_worker import BaseWorker
from .simple_worker import SimpleWorker
from .task_queue import TaskQueue

__all__ = [
    'BaseWorker',
    'SimpleWorker',
    'TaskQueue',
]

