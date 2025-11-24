"""
Módulo de Workers para procesamiento distribuido con Redis.

Este módulo contiene:
- RedisTaskQueue: Cola distribuida usando Redis
- RedisWorker: Worker que procesa tareas de Redis

Uso:
    from workers import RedisTaskQueue, RedisWorker
    
    queue = RedisTaskQueue(host='localhost')
    worker = RedisWorker('worker-1', pipeline, queue)
    worker.start()
"""

from .redis_task_queue import RedisTaskQueue
from .redis_worker import RedisWorker

__all__ = [
    'RedisTaskQueue',
    'RedisWorker',
]

