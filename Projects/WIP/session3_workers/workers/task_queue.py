"""
TaskQueue - Cola de tareas en memoria para workers.

En esta sesión: Cola simple en memoria (deque)
En Sesión 4: Cola distribuida en Redis
En Sesión 7: Kubernetes Jobs
"""

from collections import deque
from typing import Dict, Any, Optional, List
import time
import threading


class TaskQueue:
    """
    Cola de tareas en memoria para workers.
    
    Thread-safe para múltiples workers.
    
    Attributes:
        queue (deque): Cola de tareas pendientes
        processing (dict): Tareas en procesamiento
        completed (list): Tareas completadas
        failed (list): Tareas fallidas
        
    Ejemplo:
        queue = TaskQueue()
        
        # Añadir tareas
        queue.add_task({'image_path': 'photo.jpg', ...})
        
        # Obtener tarea
        task = queue.get_task('worker-1')
        
        # Marcar como completada
        queue.mark_completed(task['id'], result)
    """
    
    def __init__(self):
        """Inicializa la cola de tareas."""
        self.queue = deque()
        self.processing = {}
        self.completed = []
        self.failed = []
        
        # Lock para thread-safety
        self.lock = threading.Lock()
        
        # Contador para IDs de tareas
        self._task_counter = 0
    
    def add_task(self, task: Dict[str, Any]) -> str:
        """
        Añade una tarea a la cola.
        
        Args:
            task: Diccionario con información de la tarea
            
        Returns:
            str: ID de la tarea creada
        """
        with self.lock:
            # Generar ID si no existe
            if 'id' not in task:
                self._task_counter += 1
                task['id'] = f"task-{self._task_counter:04d}"
            
            # Añadir timestamp
            task['created_at'] = time.time()
            task['status'] = 'pending'
            
            # Añadir a la cola
            self.queue.append(task)
            
            return task['id']
    
    def get_task(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la próxima tarea de la cola.
        
        Args:
            worker_id: ID del worker que solicita la tarea
            
        Returns:
            Dict o None: Tarea o None si no hay tareas
        """
        with self.lock:
            if not self.queue:
                return None
            
            # Obtener tarea de la cola
            task = self.queue.popleft()
            
            # Marcar como en procesamiento
            task['status'] = 'processing'
            task['worker_id'] = worker_id
            task['started_at'] = time.time()
            
            # Guardar en diccionario de procesamiento
            self.processing[task['id']] = task
            
            return task
    
    def mark_completed(
        self, 
        task_id: str, 
        result: Optional[Dict[str, Any]] = None
    ):
        """
        Marca una tarea como completada.
        
        Args:
            task_id: ID de la tarea
            result: Resultado del procesamiento (opcional)
        """
        with self.lock:
            if task_id not in self.processing:
                raise ValueError(f"Tarea {task_id} no está en procesamiento")
            
            # Obtener tarea
            task = self.processing.pop(task_id)
            
            # Actualizar información
            task['status'] = 'completed'
            task['completed_at'] = time.time()
            task['processing_time'] = task['completed_at'] - task['started_at']
            if result:
                task['result'] = result
            
            # Mover a completadas
            self.completed.append(task)
    
    def mark_failed(self, task_id: str, error: str):
        """
        Marca una tarea como fallida.
        
        Args:
            task_id: ID de la tarea
            error: Mensaje de error
        """
        with self.lock:
            if task_id not in self.processing:
                raise ValueError(f"Tarea {task_id} no está en procesamiento")
            
            # Obtener tarea
            task = self.processing.pop(task_id)
            
            # Actualizar información
            task['status'] = 'failed'
            task['failed_at'] = time.time()
            task['processing_time'] = task['failed_at'] - task['started_at']
            task['error'] = error
            
            # Mover a fallidas
            self.failed.append(task)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la cola.
        
        Returns:
            Dict: Estadísticas actuales
        """
        with self.lock:
            return {
                'pending': len(self.queue),
                'processing': len(self.processing),
                'completed': len(self.completed),
                'failed': len(self.failed),
                'total': len(self.queue) + len(self.processing) + len(self.completed) + len(self.failed)
            }
    
    def is_empty(self) -> bool:
        """
        Verifica si la cola está vacía.
        
        Returns:
            bool: True si no hay tareas pendientes
        """
        with self.lock:
            return len(self.queue) == 0
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de tareas pendientes.
        
        Returns:
            List: Lista de tareas pendientes
        """
        with self.lock:
            return list(self.queue)
    
    def clear(self):
        """Limpia la cola completamente."""
        with self.lock:
            self.queue.clear()
            self.processing.clear()
            self.completed.clear()
            self.failed.clear()
            self._task_counter = 0
    
    def __len__(self) -> int:
        """Número de tareas pendientes."""
        return len(self.queue)
    
    def __repr__(self) -> str:
        """Representación en string."""
        stats = self.get_stats()
        return (
            f"TaskQueue("
            f"pending={stats['pending']}, "
            f"processing={stats['processing']}, "
            f"completed={stats['completed']}, "
            f"failed={stats['failed']})"
        )

