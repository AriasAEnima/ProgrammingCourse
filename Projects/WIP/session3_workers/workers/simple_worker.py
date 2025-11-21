"""
SimpleWorker - Worker síncrono para procesamiento de imágenes.

Procesa tareas de manera secuencial (una a la vez).
"""

import time
import os
from typing import Dict, Any
from PIL import Image
import sys

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_worker import BaseWorker
from .task_queue import TaskQueue
from core import FilterPipeline


class SimpleWorker(BaseWorker):
    """
    Worker síncrono que procesa imágenes con un pipeline.
    
    Características:
    - Procesa una tarea a la vez (síncrono)
    - Usa FilterPipeline para aplicar filtros
    - Registra logs detallados
    - Maneja errores gracefully
    
    Attributes:
        worker_id (str): ID del worker
        pipeline (FilterPipeline): Pipeline de filtros
        queue (TaskQueue): Cola de tareas
        
    Ejemplo:
        pipeline = FilterPipeline([BlurFilter(), BrightnessFilter()])
        queue = TaskQueue()
        
        worker = SimpleWorker('worker-1', pipeline, queue)
        worker.start()
        
        # Worker procesará tareas de la cola automáticamente
    """
    
    def __init__(
        self,
        worker_id: str,
        pipeline: FilterPipeline,
        queue: TaskQueue,
        poll_interval: float = 1.0
    ):
        """
        Inicializa el worker.
        
        Args:
            worker_id: Identificador único
            pipeline: Pipeline de filtros a aplicar
            queue: Cola de tareas
            poll_interval: Intervalo de polling en segundos
        """
        super().__init__(worker_id)
        
        if not isinstance(pipeline, FilterPipeline):
            raise TypeError(f"pipeline debe ser FilterPipeline, recibido: {type(pipeline)}")
        
        if not isinstance(queue, TaskQueue):
            raise TypeError(f"queue debe ser TaskQueue, recibido: {type(queue)}")
        
        self.pipeline = pipeline
        self.queue = queue
        self.poll_interval = poll_interval
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una tarea de imagen.
        
        Args:
            task: Diccionario con:
                - image_path: Ruta de la imagen de entrada
                - output_path: Ruta para guardar el resultado
                - (opcional) task_id, metadata, etc.
                
        Returns:
            Dict: Resultado con estadísticas
            
        Raises:
            Exception: Si hay error en el procesamiento
        """
        task_id = task.get('id', 'unknown')
        image_path = task.get('image_path')
        output_path = task.get('output_path')
        
        self.logger.info(f"📝 Procesando tarea {task_id}")
        self.logger.info(f"   Entrada: {image_path}")
        self.logger.info(f"   Salida: {output_path}")
        
        start_time = time.time()
        
        try:
            # 1. Cargar imagen
            self.logger.debug(f"Cargando imagen: {image_path}")
            image = Image.open(image_path)
            load_time = time.time() - start_time
            
            # 2. Aplicar pipeline
            self.logger.debug(f"Aplicando pipeline: {self.pipeline}")
            pipeline_start = time.time()
            result_image, pipeline_stats = self.pipeline.apply(image)
            pipeline_time = time.time() - pipeline_start
            
            if result_image is None:
                raise ValueError("Pipeline retornó None (todos los filtros fallaron)")
            
            # 3. Crear directorio de salida si no existe
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 4. Guardar resultado
            self.logger.debug(f"Guardando resultado: {output_path}")
            save_start = time.time()
            result_image.save(output_path, quality=95)
            save_time = time.time() - save_start
            
            # 5. Calcular tiempo total
            total_time = time.time() - start_time
            
            # 6. Construir resultado
            result = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'status': 'success',
                'input_path': image_path,
                'output_path': output_path,
                'image_size': image.size,
                'times': {
                    'load': load_time,
                    'pipeline': pipeline_time,
                    'save': save_time,
                    'total': total_time
                },
                'pipeline_stats': pipeline_stats
            }
            
            # 7. Actualizar estadísticas del worker
            self.stats['tasks_completed'] += 1
            self.stats['total_processing_time'] += total_time
            self.stats['last_task_at'] = time.time()
            
            self.logger.info(f"✅ Tarea {task_id} completada en {total_time:.3f}s")
            
            return result
            
        except FileNotFoundError as e:
            error_msg = f"Imagen no encontrada: {e}"
            self.logger.error(f"❌ Tarea {task_id} falló: {error_msg}")
            self.stats['tasks_failed'] += 1
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Tarea {task_id} falló: {error_msg}")
            self.stats['tasks_failed'] += 1
            raise
    
    def start(self):
        """
        Inicia el worker y comienza a procesar tareas.
        
        El worker entrará en un loop donde:
        1. Poll a la cola por tareas
        2. Procesa la tarea si hay alguna
        3. Espera un intervalo si no hay tareas
        4. Repite hasta que se detenga
        """
        super().start()  # Llama a BaseWorker.start()
        
        self.logger.info(f"🔍 Worker escuchando cola: {self.queue}")
        self.logger.info(f"🎨 Pipeline: {self.pipeline}")
        self.logger.info(f"⏱️  Poll interval: {self.poll_interval}s")
        
        consecutive_empty_polls = 0
        
        try:
            while self.is_running:
                # Obtener próxima tarea
                task = self.queue.get_task(self.worker_id)
                
                if task is None:
                    # No hay tareas
                    consecutive_empty_polls += 1
                    
                    if consecutive_empty_polls == 1:
                        self.logger.debug("💤 No hay tareas disponibles, esperando...")
                    
                    # Log periódico si hay mucho tiempo sin tareas
                    if consecutive_empty_polls % 10 == 0:
                        self.logger.debug(f"💤 Esperando tareas ({consecutive_empty_polls * self.poll_interval:.0f}s)...")
                    
                    time.sleep(self.poll_interval)
                    continue
                
                # Reset contador
                consecutive_empty_polls = 0
                
                # Procesar tarea
                self.current_task = task
                task_id = task.get('id', 'unknown')
                
                try:
                    result = self.process_task(task)
                    self.queue.mark_completed(task_id, result)
                    
                except Exception as e:
                    error_msg = str(e)
                    self.queue.mark_failed(task_id, error_msg)
                    self.logger.error(f"Tarea {task_id} marcada como fallida")
                
                finally:
                    self.current_task = None
                    
        except KeyboardInterrupt:
            self.logger.info("⚠️  Interrupción de teclado recibida")
            
        finally:
            self.stop()
    
    def __repr__(self) -> str:
        """Representación en string."""
        status = "running" if self.is_running else "stopped"
        return (
            f"SimpleWorker("
            f"id={self.worker_id}, "
            f"status={status}, "
            f"pipeline={len(self.pipeline)} filters, "
            f"completed={self.stats['tasks_completed']})"
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("⚙️  Ejemplo de uso de SimpleWorker")
    print("=" * 70)
    
    print("""
    El SimpleWorker procesa tareas de manera síncrona (una a la vez).
    
    Flujo:
    1. Worker espera tareas en la cola
    2. Obtiene próxima tarea
    3. Procesa imagen con pipeline
    4. Guarda resultado
    5. Marca tarea como completada
    6. Repite
    
    Ejemplo de código:
    """)
    
    print("""
    from workers import SimpleWorker, TaskQueue
    from core import FilterPipeline
    from filters import BlurFilter, BrightnessFilter
    
    # Crear pipeline
    pipeline = FilterPipeline([
        BlurFilter(radius=3),
        BrightnessFilter(factor=1.3)
    ])
    
    # Crear cola
    queue = TaskQueue()
    
    # Añadir tareas
    queue.add_task({
        'image_path': 'images/photo1.jpg',
        'output_path': 'output/photo1.jpg'
    })
    
    # Crear y iniciar worker
    worker = SimpleWorker('worker-1', pipeline, queue)
    worker.start()  # Procesa tareas hasta que se detenga
    """)

