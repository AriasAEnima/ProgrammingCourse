"""
AsyncWorker - Worker asíncrono para procesamiento concurrente.

Procesa múltiples tareas de manera concurrente usando asyncio.
Ideal para tareas I/O bound (lectura/escritura de imágenes).
"""

import asyncio
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


class AsyncWorker(BaseWorker):
    """
    Worker asíncrono que procesa imágenes concurrentemente.
    
    Características:
    - Procesa múltiples tareas concurrentemente (no bloquea en I/O)
    - Usa asyncio para operaciones asíncronas
    - Más eficiente que SimpleWorker para I/O-bound tasks
    - Puede manejar mayor throughput
    
    Attributes:
        worker_id (str): ID del worker
        pipeline (FilterPipeline): Pipeline de filtros
        queue (TaskQueue): Cola de tareas
        max_concurrent (int): Máximo de tareas concurrentes
        
    Ejemplo:
        pipeline = FilterPipeline([BlurFilter(), BrightnessFilter()])
        queue = TaskQueue()
        
        worker = AsyncWorker('async-worker-1', pipeline, queue, max_concurrent=3)
        asyncio.run(worker.start())  # Procesa hasta 3 tareas a la vez
    """
    
    def __init__(
        self,
        worker_id: str,
        pipeline: FilterPipeline,
        queue: TaskQueue,
        poll_interval: float = 1.0,
        max_concurrent: int = 5
    ):
        """
        Inicializa el worker asíncrono.
        
        Args:
            worker_id: Identificador único
            pipeline: Pipeline de filtros a aplicar
            queue: Cola de tareas
            poll_interval: Intervalo de polling en segundos
            max_concurrent: Máximo de tareas concurrentes
        """
        super().__init__(worker_id)
        
        if not isinstance(pipeline, FilterPipeline):
            raise TypeError(f"pipeline debe ser FilterPipeline, recibido: {type(pipeline)}")
        
        if not isinstance(queue, TaskQueue):
            raise TypeError(f"queue debe ser TaskQueue, recibido: {type(queue)}")
        
        self.pipeline = pipeline
        self.queue = queue
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        
        # Semáforo para limitar concurrencia
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def load_image_async(self, image_path: str) -> Image.Image:
        """
        Carga una imagen de forma asíncrona.
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Image: Imagen cargada
        """
        # PIL no es async nativo, pero podemos ejecutarlo en thread pool
        loop = asyncio.get_event_loop()
        image = await loop.run_in_executor(None, Image.open, image_path)
        return image
    
    async def save_image_async(self, image: Image.Image, output_path: str):
        """
        Guarda una imagen de forma asíncrona.
        
        Args:
            image: Imagen a guardar
            output_path: Ruta de salida
        """
        # Crear directorio si no existe
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Guardar en thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: image.save(output_path, quality=95)
        )
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método síncrono requerido por BaseWorker.
        
        Este método NO se usa en AsyncWorker.
        Usar process_task_async() en su lugar.
        """
        raise NotImplementedError(
            "AsyncWorker usa process_task_async(). "
            "No uses process_task() directamente."
        )
    
    async def process_task_async(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una tarea de forma asíncrona.
        
        Args:
            task: Diccionario con información de la tarea
            
        Returns:
            Dict: Resultado del procesamiento
        """
        task_id = task.get('id', 'unknown')
        image_path = task.get('image_path')
        output_path = task.get('output_path')
        
        self.logger.info(f"📝 [Async] Procesando tarea {task_id}")
        self.logger.debug(f"   Entrada: {image_path}")
        self.logger.debug(f"   Salida: {output_path}")
        
        start_time = time.time()
        
        try:
            # 1. Cargar imagen (async)
            load_start = time.time()
            image = await self.load_image_async(image_path)
            load_time = time.time() - load_start
            self.logger.debug(f"   Imagen cargada en {load_time:.3f}s")
            
            # 2. Aplicar pipeline (en thread pool, no es CPU-bound crítico)
            pipeline_start = time.time()
            loop = asyncio.get_event_loop()
            result_image, pipeline_stats = await loop.run_in_executor(
                None, 
                self.pipeline.apply, 
                image
            )
            pipeline_time = time.time() - pipeline_start
            
            if result_image is None:
                raise ValueError("Pipeline retornó None")
            
            # 3. Guardar resultado (async)
            save_start = time.time()
            await self.save_image_async(result_image, output_path)
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
                'image_size': image.size,
                'times': {
                    'load': load_time,
                    'pipeline': pipeline_time,
                    'save': save_time,
                    'total': total_time
                },
                'pipeline_stats': pipeline_stats
            }
            
            # 6. Actualizar estadísticas
            self.stats['tasks_completed'] += 1
            self.stats['total_processing_time'] += total_time
            self.stats['last_task_at'] = time.time()
            
            self.logger.info(f"✅ [Async] Tarea {task_id} completada en {total_time:.3f}s")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ [Async] Tarea {task_id} falló: {error_msg}")
            self.stats['tasks_failed'] += 1
            raise
    
    async def worker_loop(self):
        """
        Loop principal del worker que procesa tareas.
        """
        consecutive_empty_polls = 0
        
        while self.is_running:
            # Obtener próxima tarea
            task = self.queue.get_task(self.worker_id)
            
            if task is None:
                consecutive_empty_polls += 1
                
                if consecutive_empty_polls == 1:
                    self.logger.debug("💤 No hay tareas disponibles")
                
                await asyncio.sleep(self.poll_interval)
                continue
            
            # Reset contador
            consecutive_empty_polls = 0
            
            # Procesar tarea con semáforo (limitar concurrencia)
            async with self.semaphore:
                task_id = task.get('id', 'unknown')
                self.current_task = task
                
                try:
                    result = await self.process_task_async(task)
                    self.queue.mark_completed(task_id, result)
                    
                except Exception as e:
                    error_msg = str(e)
                    self.queue.mark_failed(task_id, error_msg)
                    
                finally:
                    self.current_task = None
    
    async def start(self):
        """
        Inicia el worker asíncrono.
        
        Crea múltiples coroutines para procesar tareas concurrentemente.
        """
        super().start()  # Llama a BaseWorker.start()
        
        self.logger.info(f"🔍 [Async] Worker escuchando cola: {self.queue}")
        self.logger.info(f"🎨 Pipeline: {self.pipeline}")
        self.logger.info(f"⚡ Max concurrencia: {self.max_concurrent} tareas")
        
        try:
            await self.worker_loop()
            
        except asyncio.CancelledError:
            self.logger.info("⚠️  Worker cancelado")
            
        except KeyboardInterrupt:
            self.logger.info("⚠️  Interrupción de teclado")
            
        finally:
            self.stop()
    
    def __repr__(self) -> str:
        """Representación en string."""
        status = "running" if self.is_running else "stopped"
        return (
            f"AsyncWorker("
            f"id={self.worker_id}, "
            f"status={status}, "
            f"max_concurrent={self.max_concurrent}, "
            f"completed={self.stats['tasks_completed']})"
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("⚡ Ejemplo de uso de AsyncWorker")
    print("=" * 70)
    
    print("""
    El AsyncWorker procesa tareas de manera asíncrona (concurrente).
    
    Ventajas sobre SimpleWorker:
    - ✓ No bloquea en I/O (carga/guardado de imágenes)
    - ✓ Puede procesar múltiples tareas a la vez
    - ✓ Mayor throughput para tareas I/O-bound
    - ✓ Mejor uso de recursos
    
    Ejemplo de código:
    """)
    
    print("""
    import asyncio
    from workers import AsyncWorker, TaskQueue
    from core import FilterPipeline
    from filters import BlurFilter, BrightnessFilter
    
    # Crear pipeline
    pipeline = FilterPipeline([
        BlurFilter(radius=3),
        BrightnessFilter(factor=1.3)
    ])
    
    # Crear cola con múltiples tareas
    queue = TaskQueue()
    for i in range(10):
        queue.add_task({
            'image_path': f'images/photo{i}.jpg',
            'output_path': f'output/photo{i}.jpg'
        })
    
    # Crear worker asíncrono (procesa hasta 5 a la vez)
    worker = AsyncWorker('async-worker-1', pipeline, queue, max_concurrent=5)
    
    # Iniciar (async)
    asyncio.run(worker.start())
    """)
    
    print("\n🎯 Cuándo usar AsyncWorker:")
    print("""
    ✓ Muchas imágenes pequeñas (I/O-bound)
    ✓ Necesitas alto throughput
    ✓ Tienes múltiples CPUs disponibles
    ✓ Procesamiento en red o servicios remotos
    
    ⚠️  Cuándo NO usar AsyncWorker:
    ✗ Pocas imágenes grandes (SimpleWorker es suficiente)
    ✗ Pipeline es muy CPU-intensive
    ✗ Simplicidad es más importante que performance
    """)

