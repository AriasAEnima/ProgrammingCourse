"""
RedisWorker - Worker que procesa tareas de una cola de Redis.

Extiende el patrón Worker de la Sesión 3 para usar Redis
como cola distribuida.
"""

import os
import sys
import time
import logging
from typing import Dict, Any
from PIL import Image

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .redis_task_queue import RedisTaskQueue
from core import FilterPipeline


class RedisWorker:
    """
    Worker que procesa tareas de una cola de Redis.
    
    Similar a SimpleWorker de Sesión 3, pero usa RedisTaskQueue
    en lugar de TaskQueue en memoria.
    
    Características:
    - Puede correr en diferentes máquinas
    - Procesa tareas de Redis de forma atómica
    - Logging estructurado
    - Estadísticas y health checks
    - Graceful shutdown
    
    Attributes:
        worker_id (str): ID único del worker
        pipeline (FilterPipeline): Pipeline de filtros
        queue (RedisTaskQueue): Cola de Redis
        
    Ejemplo:
        queue = RedisTaskQueue(host='localhost')
        pipeline = FilterPipeline([BlurFilter(), BrightnessFilter()])
        
        worker = RedisWorker('worker-1', pipeline, queue)
        worker.start()  # Procesa hasta que la cola esté vacía
    """
    
    def __init__(
        self,
        worker_id: str,
        pipeline: FilterPipeline,
        queue: RedisTaskQueue,
        poll_interval: float = 1.0
    ):
        """
        Inicializa el worker.
        
        Args:
            worker_id: Identificador único del worker
            pipeline: Pipeline de filtros a aplicar
            queue: Cola de Redis
            poll_interval: Intervalo de polling en segundos
        """
        self.worker_id = worker_id
        
        if not isinstance(pipeline, FilterPipeline):
            raise TypeError(f"pipeline debe ser FilterPipeline, recibido: {type(pipeline)}")
        
        if not isinstance(queue, RedisTaskQueue):
            raise TypeError(f"queue debe ser RedisTaskQueue, recibido: {type(queue)}")
        
        self.pipeline = pipeline
        self.queue = queue
        self.poll_interval = poll_interval
        
        # Estado
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
        
        # Logger
        self.logger = logging.getLogger(f"Worker-{worker_id}")
        self.logger.setLevel(logging.INFO)
        
        # Handler si no existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una tarea de procesamiento de imagen.
        
        Args:
            task: Diccionario con información de la tarea
            
        Returns:
            Dict: Resultado del procesamiento
        """
        task_id = task.get('id', 'unknown')
        image_path = task.get('image_path')
        output_path = task.get('output_path')
        
        self.logger.info(f"📝 Procesando tarea {task_id}")
        self.logger.debug(f"   Entrada: {image_path}")
        self.logger.debug(f"   Salida: {output_path}")
        
        start_time = time.time()
        
        try:
            # 1. Cargar imagen
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
            
            load_start = time.time()
            image = Image.open(image_path)
            load_time = time.time() - load_start
            self.logger.debug(f"   Imagen cargada en {load_time:.3f}s")
            
            # 2. Aplicar pipeline
            pipeline_start = time.time()
            result_image, pipeline_stats = self.pipeline.apply(image)
            pipeline_time = time.time() - pipeline_start
            
            if result_image is None:
                raise ValueError("Pipeline retornó None")
            
            # 3. Guardar resultado
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            save_start = time.time()
            result_image.save(output_path, quality=95)
            save_time = time.time() - save_start
            
            # 4. Calcular tiempo total
            total_time = time.time() - start_time
            
            # 5. Construir resultado
            result = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'status': 'success',
                'input_path': image_path,
                'output_path': output_path,
                'image_size': f"{image.size[0]}x{image.size[1]}",
                'load_time': f"{load_time:.3f}s",
                'pipeline_time': f"{pipeline_time:.3f}s",
                'save_time': f"{save_time:.3f}s",
                'total_time': f"{total_time:.3f}s"
            }
            
            # 6. Actualizar estadísticas
            self.stats['tasks_completed'] += 1
            self.stats['total_processing_time'] += total_time
            self.stats['last_task_at'] = time.time()
            
            self.logger.info(f"✅ Tarea {task_id} completada en {total_time:.3f}s")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Tarea {task_id} falló: {error_msg}")
            self.stats['tasks_failed'] += 1
            raise
    
    def start(self):
        """
        Inicia el worker y procesa tareas hasta que la cola esté vacía.
        """
        self.is_running = True
        self.stats['start_time'] = time.time()
        
        self.logger.info(f"🚀 Worker {self.worker_id} iniciado")
        self.logger.info(f"🔍 Escuchando cola: {self.queue}")
        self.logger.info(f"🎨 Pipeline: {self.pipeline}")
        
        consecutive_empty_polls = 0
        
        try:
            while self.is_running:
                # Obtener próxima tarea
                task = self.queue.get_task(self.worker_id)
                
                if task is None:
                    consecutive_empty_polls += 1
                    
                    if consecutive_empty_polls == 1:
                        self.logger.debug("💤 No hay tareas disponibles")
                    
                    # Si no hay tareas pendientes ni en proceso, terminar
                    stats = self.queue.get_stats()
                    if stats['pending'] == 0 and stats['processing'] <= 1:
                        # processing <= 1 porque nuestra tarea actual cuenta
                        self.logger.info("✨ Cola vacía, terminando")
                        break
                    
                    time.sleep(self.poll_interval)
                    continue
                
                # Reset contador
                consecutive_empty_polls = 0
                
                # Procesar tarea
                task_id = task.get('id', 'unknown')
                self.current_task = task
                
                try:
                    result = self.process_task(task)
                    self.queue.mark_completed(task_id, result)
                    
                except Exception as e:
                    error_msg = str(e)
                    self.queue.mark_failed(task_id, error_msg)
                    
                finally:
                    self.current_task = None
        
        except KeyboardInterrupt:
            self.logger.info("⚠️  Interrupción de teclado")
        
        finally:
            self.stop()
    
    def stop(self):
        """
        Detiene el worker de forma controlada.
        """
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info(f"🛑 Worker {self.worker_id} recibió señal de parada")
        
        # Mostrar estadísticas finales
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        
        self.logger.info(f"📊 Estadísticas finales de {self.worker_id}:")
        self.logger.info(f"   Tareas completadas: {self.stats['tasks_completed']}")
        self.logger.info(f"   Tareas fallidas: {self.stats['tasks_failed']}")
        self.logger.info(f"   Tiempo activo: {uptime:.1f}s")
        
        if self.stats['tasks_completed'] > 0:
            avg_time = self.stats['total_processing_time'] / self.stats['tasks_completed']
            self.logger.info(f"   Tiempo promedio: {avg_time:.3f}s por tarea")
        
        self.logger.info(f"👋 Worker {self.worker_id} detenido correctamente")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas del worker.
        
        Returns:
            Dict: Estadísticas actuales
        """
        stats = self.stats.copy()
        
        # Calcular tasa de éxito
        total_tasks = stats['tasks_completed'] + stats['tasks_failed']
        stats['success_rate'] = (
            stats['tasks_completed'] / total_tasks if total_tasks > 0 else 0.0
        )
        
        # Calcular uptime
        if stats['start_time']:
            stats['uptime'] = time.time() - stats['start_time']
        else:
            stats['uptime'] = 0.0
        
        return stats
    
    def is_healthy(self) -> bool:
        """
        Verifica si el worker está saludable.
        
        Returns:
            bool: True si el worker está saludable
        """
        # Worker está saludable si:
        # 1. Está corriendo
        # 2. No ha tenido demasiados fallos
        if not self.is_running:
            return False
        
        total_tasks = self.stats['tasks_completed'] + self.stats['tasks_failed']
        if total_tasks == 0:
            return True  # Recién iniciado
        
        success_rate = self.stats['tasks_completed'] / total_tasks
        return success_rate >= 0.5  # Al menos 50% de éxito
    
    def __repr__(self) -> str:
        """Representación en string."""
        status = "running" if self.is_running else "stopped"
        return (
            f"RedisWorker("
            f"id={self.worker_id}, "
            f"status={status}, "
            f"completed={self.stats['tasks_completed']})"
        )

