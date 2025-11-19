"""
🔗 Queue Manager - DÍA 2: IPC Communication

Gestión de comunicación entre procesos usando multiprocessing.Queue
"""

import time
import uuid
import threading
import multiprocessing as mp
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from queue import Empty, Full
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskMessage:
    """📨 Mensaje de tarea para workers"""
    task_id: str
    task_type: str
    filter_name: str
    image_data: Any
    parameters: Dict[str, Any]
    timestamp: float
    priority: int = 1
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskMessage':
        """Crear desde diccionario"""
        return cls(**data)

@dataclass
class ResultMessage:
    """📤 Mensaje de resultado de workers"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0
    worker_id: Optional[int] = None
    process_id: Optional[int] = None
    timestamp: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResultMessage':
        """Crear desde diccionario"""
        return cls(**data)

class QueueManager:
    """
    🎯 Gestor de colas para comunicación IPC
    
    Maneja task distribution y result collection usando multiprocessing.Queue
    """
    
    def __init__(self, maxsize: int = 100):
        """
        Inicializar manager de colas
        
        Args:
            maxsize: Tamaño máximo de colas
        """
        self.maxsize = maxsize
        
        # Colas principales
        self.task_queue = mp.Queue(maxsize=maxsize)
        self.result_queue = mp.Queue(maxsize=maxsize)
        
        # Colas especializadas por prioridad
        self.high_priority_queue = mp.Queue(maxsize=maxsize // 4)
        self.low_priority_queue = mp.Queue(maxsize=maxsize // 2)
        
        # Estado del manager
        self.is_running = False
        self.pending_tasks: Dict[str, TaskMessage] = {}
        self.completed_tasks: Dict[str, ResultMessage] = {}
        self.failed_tasks: Dict[str, ResultMessage] = {}
        
        # Métricas
        self.tasks_sent = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.start_time = None
        
        # Threading para monitoring
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        logger.info(f"🔗 QueueManager initialized - Max size: {maxsize}")
    
    def start(self):
        """🚀 Iniciar el manager"""
        self.is_running = True
        self.start_time = time.time()
        
        # Iniciar thread de monitoring
        self._start_monitoring()
        
        logger.info("🚀 QueueManager started")
    
    def stop(self):
        """🛑 Detener el manager"""
        self.is_running = False
        self._stop_monitoring.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
        
        # Limpiar colas
        self._clear_queues()
        
        uptime = time.time() - (self.start_time or time.time())
        logger.info(f"🛑 QueueManager stopped - Uptime: {uptime:.2f}s")
    
    def _start_monitoring(self):
        """🔍 Iniciar thread de monitoring de colas"""
        self._monitor_thread = threading.Thread(
            target=self._monitor_queues,
            name="QueueMonitor",
            daemon=True
        )
        self._monitor_thread.start()
    
    def _monitor_queues(self):
        """📊 Monitorear estado de colas en background"""
        while not self._stop_monitoring.is_set():
            try:
                # Log del estado cada 10 segundos
                if self._stop_monitoring.wait(10):
                    break
                
                stats = self.get_queue_stats()
                logger.debug(f"📊 Queue Stats: {stats}")
                
                # Alertas si las colas están llenas
                if stats["task_queue_size"] >= self.maxsize * 0.9:
                    logger.warning("⚠️ Task queue nearly full!")
                
                if stats["result_queue_size"] >= self.maxsize * 0.9:
                    logger.warning("⚠️ Result queue nearly full!")
                    
            except Exception as e:
                logger.error(f"❌ Queue monitoring error: {e}")
    
    def send_task(self, filter_name: str, image_data: Any, 
                  parameters: Dict[str, Any] = None, priority: int = 1,
                  timeout: float = 5.0) -> str:
        """
        📤 Enviar tarea a workers
        
        Args:
            filter_name: Nombre del filtro a aplicar
            image_data: Datos de la imagen
            parameters: Parámetros adicionales
            priority: Prioridad (1=alta, 2=normal, 3=baja)
            timeout: Timeout para envío
            
        Returns:
            Task ID único
        """
        if not self.is_running:
            raise RuntimeError("QueueManager not running")
        
        # Crear mensaje de tarea
        task_id = str(uuid.uuid4())
        task = TaskMessage(
            task_id=task_id,
            task_type="filter",
            filter_name=filter_name,
            image_data=image_data,
            parameters=parameters or {},
            timestamp=time.time(),
            priority=priority
        )
        
        # Seleccionar cola según prioridad
        target_queue = self._select_queue_by_priority(priority)
        
        try:
            # Enviar a cola (con timeout)
            target_queue.put(task, timeout=timeout)
            
            # Trackear tarea
            self.pending_tasks[task_id] = task
            self.tasks_sent += 1
            
            logger.info(f"📤 Task sent: {task_id} - Filter: {filter_name}, Priority: {priority}")
            return task_id
            
        except Full:
            logger.error(f"❌ Queue full - couldn't send task: {task_id}")
            raise RuntimeError("Queue full")
        except Exception as e:
            logger.error(f"❌ Failed to send task {task_id}: {e}")
            raise
    
    def _select_queue_by_priority(self, priority: int) -> mp.Queue:
        """🎯 Seleccionar cola según prioridad"""
        if priority == 1:
            return self.high_priority_queue
        elif priority == 3:
            return self.low_priority_queue
        else:
            return self.task_queue
    
    def get_next_task(self, timeout: float = 1.0) -> Optional[TaskMessage]:
        """
        📥 Obtener siguiente tarea (para workers)
        
        Args:
            timeout: Timeout para esperar tarea
            
        Returns:
            TaskMessage o None si no hay tareas
        """
        # Prioridad: alta -> normal -> baja
        queues_by_priority = [
            self.high_priority_queue,
            self.task_queue,
            self.low_priority_queue
        ]
        
        for queue in queues_by_priority:
            try:
                task = queue.get_nowait()
                logger.info(f"📥 Task retrieved: {task.task_id}")
                return task
            except Empty:
                continue
        
        # Si no hay tareas inmediatas, esperar en cola principal
        try:
            task = self.task_queue.get(timeout=timeout)
            logger.info(f"📥 Task retrieved (waited): {task.task_id}")
            return task
        except Empty:
            return None
    
    def send_result(self, result: ResultMessage, timeout: float = 5.0):
        """
        📨 Enviar resultado (desde workers)
        
        Args:
            result: Mensaje de resultado
            timeout: Timeout para envío
        """
        try:
            self.result_queue.put(result, timeout=timeout)
            logger.info(f"📨 Result sent: {result.task_id} - Success: {result.success}")
        except Full:
            logger.error(f"❌ Result queue full - couldn't send result: {result.task_id}")
            raise RuntimeError("Result queue full")
        except Exception as e:
            logger.error(f"❌ Failed to send result {result.task_id}: {e}")
            raise
    
    def get_result(self, task_id: str = None, timeout: float = 1.0) -> Optional[ResultMessage]:
        """
        📬 Obtener resultado
        
        Args:
            task_id: ID específico de tarea (None para cualquier resultado)
            timeout: Timeout para esperar
            
        Returns:
            ResultMessage o None
        """
        try:
            result = self.result_queue.get(timeout=timeout)
            
            # Mover de pending a completed/failed
            if result.task_id in self.pending_tasks:
                del self.pending_tasks[result.task_id]
            
            if result.success:
                self.completed_tasks[result.task_id] = result
                self.tasks_completed += 1
            else:
                self.failed_tasks[result.task_id] = result
                self.tasks_failed += 1
            
            logger.info(f"📬 Result received: {result.task_id} - Success: {result.success}")
            return result
            
        except Empty:
            return None
    
    def wait_for_result(self, task_id: str, timeout: float = 30.0) -> Optional[ResultMessage]:
        """
        ⏳ Esperar resultado específico de una tarea
        
        Args:
            task_id: ID de la tarea
            timeout: Timeout total
            
        Returns:
            ResultMessage o None si timeout
        """
        start_time = time.time()
        
        # Primero verificar si ya está completado
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        if task_id in self.failed_tasks:
            return self.failed_tasks[task_id]
        
        # Esperar resultado
        while time.time() - start_time < timeout:
            result = self.get_result(timeout=min(1.0, timeout - (time.time() - start_time)))
            if result and result.task_id == task_id:
                return result
        
        logger.warning(f"⏳ Timeout waiting for result: {task_id}")
        return None
    
    def process_batch_sync(self, filter_name: str, batch_data: List[Any],
                          parameters: Dict[str, Any] = None, 
                          timeout: float = 60.0) -> List[ResultMessage]:
        """
        🔄 Procesar lote de tareas síncronamente
        
        Args:
            filter_name: Nombre del filtro
            batch_data: Lista de datos a procesar
            parameters: Parámetros del filtro
            timeout: Timeout total
            
        Returns:
            Lista de resultados
        """
        if not self.is_running:
            raise RuntimeError("QueueManager not running")
        
        # Enviar todas las tareas
        task_ids = []
        for data in batch_data:
            task_id = self.send_task(filter_name, data, parameters)
            task_ids.append(task_id)
        
        logger.info(f"🔄 Batch sent: {len(task_ids)} tasks for filter: {filter_name}")
        
        # Esperar todos los resultados
        results = []
        start_time = time.time()
        
        for task_id in task_ids:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time <= 0:
                logger.warning(f"⏳ Batch timeout - got {len(results)}/{len(task_ids)} results")
                break
                
            result = self.wait_for_result(task_id, timeout=remaining_time)
            if result:
                results.append(result)
            else:
                # Crear resultado de timeout
                timeout_result = ResultMessage(
                    task_id=task_id,
                    success=False,
                    error="Timeout waiting for result",
                    timestamp=time.time()
                )
                results.append(timeout_result)
        
        batch_time = time.time() - start_time
        success_count = sum(1 for r in results if r.success)
        
        logger.info(f"✅ Batch completed: {success_count}/{len(results)} successful in {batch_time:.2f}s")
        return results
    
    def _clear_queues(self):
        """🧹 Limpiar todas las colas"""
        queues = [
            self.task_queue,
            self.result_queue, 
            self.high_priority_queue,
            self.low_priority_queue
        ]
        
        for queue in queues:
            try:
                while True:
                    queue.get_nowait()
            except Empty:
                pass
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """📊 Obtener estadísticas de colas"""
        uptime = time.time() - (self.start_time or time.time()) if self.is_running else 0
        
        return {
            "is_running": self.is_running,
            "uptime": uptime,
            "task_queue_size": self.task_queue.qsize(),
            "result_queue_size": self.result_queue.qsize(),
            "high_priority_queue_size": self.high_priority_queue.qsize(),
            "low_priority_queue_size": self.low_priority_queue.qsize(),
            "pending_tasks": len(self.pending_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "tasks_sent": self.tasks_sent,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "success_rate": (self.tasks_completed / max(1, self.tasks_sent)) * 100
        }

# =====================================================================
# 🧪 DEMO Y TESTING
# =====================================================================

def demo_basic_queue():
    """🎭 Demo básico de QueueManager"""
    print("🔗 DEMO: Basic Queue Operations")
    
    # Setup manager
    manager = QueueManager(maxsize=50)
    manager.start()
    
    # Enviar algunas tareas
    print("\n📤 Sending tasks...")
    task_ids = []
    for i in range(3):
        task_id = manager.send_task(
            filter_name="test_filter",
            image_data=f"test_image_{i}",
            parameters={"param1": f"value_{i}"},
            priority=1 if i == 0 else 2
        )
        task_ids.append(task_id)
    
    # Simular worker obteniendo tareas
    print("\n📥 Worker getting tasks...")
    for i in range(3):
        task = manager.get_next_task(timeout=2.0)
        if task:
            print(f"  📋 Got task: {task.task_id} - {task.filter_name}")
            
            # Simular procesamiento
            time.sleep(0.1)
            
            # Enviar resultado
            result = ResultMessage(
                task_id=task.task_id,
                success=True,
                result=f"processed_{task.image_data}",
                processing_time=0.1,
                worker_id=1,
                timestamp=time.time()
            )
            manager.send_result(result)
    
    # Obtener resultados
    print("\n📬 Getting results...")
    for task_id in task_ids:
        result = manager.wait_for_result(task_id, timeout=5.0)
        if result:
            status = "✅" if result.success else "❌"
            print(f"  {status} Result: {task_id} - {result.result}")
    
    # Stats
    stats = manager.get_queue_stats()
    print(f"\n📊 Final Stats: {stats}")
    
    manager.stop()
    print("✅ Demo completed")

def demo_batch_processing():
    """🔄 Demo de procesamiento en lote"""
    print("\n🔄 DEMO: Batch Processing")
    
    manager = QueueManager()
    manager.start()
    
    # Simular worker en background
    def worker_simulation():
        """Simular worker procesando tareas"""
        while manager.is_running:
            task = manager.get_next_task(timeout=1.0)
            if task:
                # Simular procesamiento
                time.sleep(0.2)
                
                result = ResultMessage(
                    task_id=task.task_id,
                    success=True,
                    result=f"processed_{task.image_data}",
                    processing_time=0.2,
                    worker_id=99,
                    timestamp=time.time()
                )
                manager.send_result(result)
    
    # Iniciar worker simulado
    worker_thread = threading.Thread(target=worker_simulation, daemon=True)
    worker_thread.start()
    
    # Procesar lote
    batch_data = [f"image_{i}" for i in range(5)]
    results = manager.process_batch_sync(
        filter_name="batch_filter",
        batch_data=batch_data,
        timeout=10.0
    )
    
    # Mostrar resultados
    print(f"📊 Batch Results: {len(results)} items")
    for i, result in enumerate(results):
        status = "✅" if result.success else "❌"
        print(f"  {status} Item {i+1}: {result.result}")
    
    manager.stop()
    print("✅ Batch demo completed")

if __name__ == "__main__":
    # Demo básico
    demo_basic_queue()
    
    # Demo batch
    demo_batch_processing() 