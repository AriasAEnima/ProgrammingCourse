"""
RedisTaskQueue - Cola de tareas distribuida usando Redis.

Esta cola permite que múltiples workers en diferentes procesos
o máquinas procesen tareas de forma distribuida.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, List
import redis


class RedisTaskQueue:
    """
    Cola de tareas distribuida usando Redis.
    
    Características:
    - Distribuida: Múltiples workers en diferentes máquinas
    - Persistente: Las tareas sobreviven reinicios
    - Atómica: Operaciones thread-safe y process-safe
    - Estados: pending → processing → completed/failed
    
    Estructura en Redis:
    - queue:pending (LIST): Tareas pendientes (FIFO)
    - queue:processing (HASH): Tareas en proceso {task_id: worker_id}
    - queue:completed (LIST): IDs de tareas completadas
    - queue:failed (LIST): IDs de tareas fallidas
    - task:{task_id} (HASH): Datos de la tarea
    - result:{task_id} (HASH): Resultado de la tarea
    
    Ejemplo:
        queue = RedisTaskQueue(host='localhost')
        
        # Añadir tarea
        task_id = queue.add_task({
            'image_path': 'input.jpg',
            'output_path': 'output.jpg'
        })
        
        # Worker obtiene tarea
        task = queue.get_task('worker-1')
        
        # Marcar como completada
        queue.mark_completed(task_id, {'status': 'success'})
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        queue_name: str = 'image_processing'
    ):
        """
        Inicializa la conexión a Redis.
        
        Args:
            host: Hostname de Redis
            port: Puerto de Redis
            db: Número de base de datos
            password: Password (opcional)
            queue_name: Nombre de la cola (permite múltiples colas)
        """
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True  # Strings en vez de bytes
        )
        
        self.queue_name = queue_name
        
        # Keys en Redis
        self.pending_key = f"{queue_name}:pending"
        self.processing_key = f"{queue_name}:processing"
        self.completed_key = f"{queue_name}:completed"
        self.failed_key = f"{queue_name}:failed"
        
        # Verificar conexión
        try:
            self.redis.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(
                f"No se pudo conectar a Redis en {host}:{port}. "
                f"¿Está Redis corriendo? Error: {e}"
            )
    
    def add_task(self, task_data: Dict[str, Any]) -> str:
        """
        Añade una tarea a la cola.
        
        Args:
            task_data: Datos de la tarea (debe ser serializable a JSON)
            
        Returns:
            str: ID de la tarea
            
        Ejemplo:
            task_id = queue.add_task({
                'name': 'Process image',
                'image_path': 'input.jpg',
                'output_path': 'output.jpg',
                'filters': ['blur', 'brightness']
            })
        """
        # Generar ID único
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        # Preparar tarea
        task = {
            'id': task_id,
            'status': 'pending',
            'created_at': time.time(),
            **task_data
        }
        
        # Guardar en Redis (pipeline para atomicidad)
        pipe = self.redis.pipeline()
        
        # 1. Guardar datos de la tarea
        task_key = f"task:{task_id}"
        pipe.hset(task_key, mapping={
            'data': json.dumps(task),
            'status': 'pending',
            'created_at': task['created_at']
        })
        
        # 2. Añadir a la cola de pendientes (RPUSH = añadir al final)
        pipe.rpush(self.pending_key, task_id)
        
        pipe.execute()
        
        return task_id
    
    def get_task(self, worker_id: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """
        Obtiene la siguiente tarea de la cola (operación atómica).
        
        Args:
            worker_id: ID del worker que solicita la tarea
            timeout: Timeout en segundos (0 = no bloquear)
            
        Returns:
            Dict con la tarea o None si no hay tareas
            
        Nota:
            Usa RPOP atómico de Redis para obtener la tarea.
        """
        # Obtener tarea de pending
        if timeout > 0:
            # Versión bloqueante
            result = self.redis.brpop(self.pending_key, timeout=timeout)
            task_id = result[1] if result else None
        else:
            # Versión no bloqueante
            task_id = self.redis.rpop(self.pending_key)
        
        if not task_id:
            return None
        
        # Obtener datos de la tarea
        task_key = f"task:{task_id}"
        task_data = self.redis.hget(task_key, 'data')
        
        if not task_data:
            # Tarea no encontrada (raro, pero posible)
            return None
        
        task = json.loads(task_data)
        task['status'] = 'processing'
        task['worker_id'] = worker_id
        task['started_at'] = time.time()
        
        # Actualizar en Redis
        pipe = self.redis.pipeline()
        pipe.hset(task_key, mapping={
            'data': json.dumps(task),
            'status': 'processing',
            'worker_id': worker_id,
            'started_at': task['started_at']
        })
        # Añadir a processing (HASH)
        pipe.hset(self.processing_key, task_id, worker_id)
        pipe.execute()
        
        return task
    
    def mark_completed(self, task_id: str, result: Dict[str, Any]):
        """
        Marca una tarea como completada.
        
        Args:
            task_id: ID de la tarea
            result: Resultado del procesamiento
        """
        task_key = f"task:{task_id}"
        result_key = f"result:{task_id}"
        
        pipe = self.redis.pipeline()
        
        # 1. Actualizar estado
        pipe.hset(task_key, mapping={
            'status': 'completed',
            'completed_at': time.time()
        })
        
        # 2. Guardar resultado
        pipe.hset(result_key, mapping=result)
        
        # 3. Mover a lista de completadas
        pipe.hdel(self.processing_key, task_id)
        pipe.rpush(self.completed_key, task_id)
        
        pipe.execute()
    
    def mark_failed(self, task_id: str, error: str):
        """
        Marca una tarea como fallida.
        
        Args:
            task_id: ID de la tarea
            error: Mensaje de error
        """
        task_key = f"task:{task_id}"
        
        pipe = self.redis.pipeline()
        
        # 1. Actualizar estado
        pipe.hset(task_key, mapping={
            'status': 'failed',
            'failed_at': time.time(),
            'error': error
        })
        
        # 2. Mover a lista de fallidas
        pipe.hdel(self.processing_key, task_id)
        pipe.rpush(self.failed_key, task_id)
        
        pipe.execute()
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado de una tarea.
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Dict con datos de la tarea o None si no existe
        """
        task_key = f"task:{task_id}"
        task_data = self.redis.hgetall(task_key)
        
        if not task_data:
            return None
        
        # Parsear data JSON
        if 'data' in task_data:
            task_data['data'] = json.loads(task_data['data'])
        
        return task_data
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la cola.
        
        Returns:
            Dict con estadísticas
        """
        pending = self.redis.llen(self.pending_key)
        processing = self.redis.hlen(self.processing_key)
        completed = self.redis.llen(self.completed_key)
        failed = self.redis.llen(self.failed_key)
        
        return {
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'failed': failed,
            'total': pending + processing + completed + failed
        }
    
    def is_empty(self) -> bool:
        """
        Verifica si la cola está vacía.
        
        Returns:
            bool: True si no hay tareas pendientes
        """
        return self.redis.llen(self.pending_key) == 0
    
    def clear(self):
        """
        Limpia todas las tareas de la cola.
        
        CUIDADO: Esto borra todas las tareas y resultados.
        """
        # Obtener todos los task_ids
        all_task_ids = []
        all_task_ids.extend(self.redis.lrange(self.pending_key, 0, -1))
        all_task_ids.extend(self.redis.hkeys(self.processing_key))
        all_task_ids.extend(self.redis.lrange(self.completed_key, 0, -1))
        all_task_ids.extend(self.redis.lrange(self.failed_key, 0, -1))
        
        pipe = self.redis.pipeline()
        
        # Borrar listas y hashes principales
        pipe.delete(self.pending_key)
        pipe.delete(self.processing_key)
        pipe.delete(self.completed_key)
        pipe.delete(self.failed_key)
        
        # Borrar datos de tareas
        for task_id in all_task_ids:
            pipe.delete(f"task:{task_id}")
            pipe.delete(f"result:{task_id}")
        
        pipe.execute()
    
    def get_completed_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los resultados de las últimas tareas completadas.
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de resultados
        """
        # Obtener últimos task_ids completados
        task_ids = self.redis.lrange(self.completed_key, -limit, -1)
        
        results = []
        for task_id in reversed(task_ids):
            result_key = f"result:{task_id}"
            result = self.redis.hgetall(result_key)
            if result:
                result['task_id'] = task_id
                results.append(result)
        
        return results
    
    def __repr__(self) -> str:
        """Representación en string."""
        stats = self.get_stats()
        return (
            f"RedisTaskQueue("
            f"name={self.queue_name}, "
            f"pending={stats['pending']}, "
            f"processing={stats['processing']}, "
            f"completed={stats['completed']}, "
            f"failed={stats['failed']})"
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("📦 Ejemplo de uso de RedisTaskQueue")
    print("=" * 70)
    
    print("""
    RedisTaskQueue es una cola distribuida que usa Redis.
    
    Ventajas sobre TaskQueue (en memoria):
    - ✓ Distribuida: Workers en diferentes máquinas
    - ✓ Persistente: Sobrevive reinicios
    - ✓ Atómica: Operaciones seguras con RPOPLPUSH
    - ✓ Escalable: Redis puede manejar millones de tareas
    
    Ejemplo de código:
    """)
    
    print("""
    import redis
    from workers import RedisTaskQueue
    
    # Conectar a Redis
    queue = RedisTaskQueue(host='localhost', port=6379)
    
    # Añadir tareas
    queue.add_task({
        'image_path': 'input.jpg',
        'output_path': 'output.jpg'
    })
    
    # Worker obtiene tarea (operación atómica)
    task = queue.get_task('worker-1')
    
    # Procesar...
    
    # Marcar como completada
    queue.mark_completed(task['id'], {'status': 'success'})
    
    # Ver estadísticas
    print(queue.get_stats())
    """)
    
    print("\n🎯 Requisito:")
    print("   Redis debe estar corriendo:")
    print("   $ redis-server")
    print("\n   O con Docker:")
    print("   $ docker run -d -p 6379:6379 redis:7-alpine")

