"""
BaseWorker - Clase base abstracta para todos los workers.

Define la interfaz común y comportamiento compartido.
"""

from abc import ABC, abstractmethod
import time
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)


class BaseWorker(ABC):
    """
    Clase base abstracta para workers.
    
    Todos los workers deben heredar de esta clase e implementar
    el método process_task().
    
    Attributes:
        worker_id (str): Identificador único del worker
        is_running (bool): Estado del worker
        stats (Dict): Estadísticas del worker
        
    Ejemplo:
        class MiWorker(BaseWorker):
            def process_task(self, task):
                # Lógica de procesamiento
                pass
    """
    
    def __init__(self, worker_id: str):
        """
        Inicializa el worker base.
        
        Args:
            worker_id: Identificador único del worker
        """
        self.worker_id = worker_id
        self.is_running = False
        self.current_task = None
        
        # Estadísticas
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0,
            'start_time': None,
            'last_task_at': None
        }
        
        # Logger específico del worker
        self.logger = logging.getLogger(f"Worker-{worker_id}")
    
    @abstractmethod
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una tarea específica.
        
        Este método DEBE ser implementado por las subclases.
        
        Args:
            task: Diccionario con información de la tarea
            
        Returns:
            Dict: Resultado del procesamiento
            
        Raises:
            NotImplementedError: Si no está implementado
        """
        raise NotImplementedError(
            f"La clase {self.__class__.__name__} debe implementar process_task()"
        )
    
    def start(self):
        """
        Inicia el worker.
        
        Este método puede ser sobreescrito por subclases para
        personalizar el comportamiento de inicio.
        """
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.logger.info(f"🚀 Worker {self.worker_id} iniciado")
    
    def stop(self):
        """
        Detiene el worker gracefully.
        
        Termina la tarea actual antes de detenerse.
        """
        self.logger.info(f"🛑 Worker {self.worker_id} recibió señal de parada")
        
        # Si hay tarea en proceso, terminarla
        if self.current_task:
            self.logger.info("Terminando tarea actual...")
        
        self.is_running = False
        self._log_final_stats()
        self.logger.info(f"👋 Worker {self.worker_id} detenido correctamente")
    
    def _log_final_stats(self):
        """Registra estadísticas finales."""
        self.logger.info(f"📊 Estadísticas finales de {self.worker_id}:")
        self.logger.info(f"   Tareas completadas: {self.stats['tasks_completed']}")
        self.logger.info(f"   Tareas fallidas: {self.stats['tasks_failed']}")
        
        if self.stats['tasks_completed'] > 0:
            avg_time = self.stats['total_processing_time'] / self.stats['tasks_completed']
            self.logger.info(f"   Tiempo promedio: {avg_time:.3f}s")
        
        if self.stats['start_time']:
            uptime = time.time() - self.stats['start_time']
            self.logger.info(f"   Tiempo activo: {uptime:.1f}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas actuales del worker.
        
        Returns:
            Dict: Diccionario con estadísticas
        """
        stats = self.stats.copy()
        
        # Calcular tiempo activo
        if stats['start_time']:
            stats['uptime'] = time.time() - stats['start_time']
        
        # Calcular tasa de éxito
        total_tasks = stats['tasks_completed'] + stats['tasks_failed']
        if total_tasks > 0:
            stats['success_rate'] = stats['tasks_completed'] / total_tasks
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def is_healthy(self) -> bool:
        """
        Verifica si el worker está saludable.
        
        Un worker es saludable si:
        - Está corriendo
        - No tiene demasiados fallos
        - Ha procesado tareas recientemente (si aplica)
        
        Returns:
            bool: True si está saludable
        """
        # No está corriendo
        if not self.is_running:
            return False
        
        # Tasa de fallos muy alta
        total_tasks = self.stats['tasks_completed'] + self.stats['tasks_failed']
        if total_tasks > 10:  # Solo verificar después de varias tareas
            failure_rate = self.stats['tasks_failed'] / total_tasks
            if failure_rate > 0.5:  # Más del 50% fallan
                return False
        
        return True
    
    def __repr__(self) -> str:
        """Representación en string del worker."""
        status = "running" if self.is_running else "stopped"
        return (
            f"{self.__class__.__name__}("
            f"id={self.worker_id}, "
            f"status={status}, "
            f"completed={self.stats['tasks_completed']})"
        )

