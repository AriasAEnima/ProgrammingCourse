"""
🔧 Filter Worker - DÍA 2: Multiprocessing Workers

Implementación de workers con ProcessPoolExecutor para filtros CPU-intensivos.
"""

import time
import threading
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilterWorker:
    """
    🔄 Worker individual para procesar filtros en procesos separados
    
    Cada worker maneja un tipo específico de filtro (I/O vs CPU bound)
    """
    
    def __init__(self, worker_id: int, filter_type: str = "cpu", max_workers: int = None):
        """
        Inicializar worker
        
        Args:
            worker_id: ID único del worker
            filter_type: Tipo de filtro ("cpu" or "io")
            max_workers: Número máximo de procesos (default: CPU count)
        """
        self.worker_id = worker_id
        self.filter_type = filter_type
        self.max_workers = max_workers or mp.cpu_count()
        self.is_running = False
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None
        
        logger.info(f"🔧 Worker {worker_id} initialized - Type: {filter_type}, Max workers: {self.max_workers}")
    
    def process_single(self, filter_func: Callable, image_data: Any, **kwargs) -> Dict[str, Any]:
        """
        🎯 Procesar una imagen con función de filtro específica
        
        Args:
            filter_func: Función de filtro a aplicar
            image_data: Datos de la imagen
            **kwargs: Argumentos adicionales para el filtro
            
        Returns:
            Dict con resultado y métricas
        """
        start_time = time.time()
        process_id = mp.current_process().pid
        
        try:
            logger.info(f"🔄 Worker {self.worker_id} - Process {process_id}: Starting filter")
            
            # Aplicar filtro
            result = filter_func(image_data, **kwargs)
            
            # Métricas
            processing_time = time.time() - start_time
            self.processed_count += 1
            
            logger.info(f"✅ Worker {self.worker_id} - Process {process_id}: Completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "processing_time": processing_time,
                "worker_id": self.worker_id,
                "process_id": process_id
            }
            
        except Exception as e:
            self.error_count += 1
            error_time = time.time() - start_time
            
            logger.error(f"❌ Worker {self.worker_id} - Process {process_id}: Error after {error_time:.2f}s - {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": error_time,
                "worker_id": self.worker_id,
                "process_id": process_id
            }
    
    def process_batch(self, filter_func: Callable, batch_data: List[Any], **kwargs) -> List[Dict[str, Any]]:
        """
        🔥 Procesar lote de imágenes usando ProcessPoolExecutor
        
        Args:
            filter_func: Función de filtro
            batch_data: Lista de datos de imágenes
            **kwargs: Argumentos para el filtro
            
        Returns:
            Lista de resultados
        """
        if not self.is_running:
            self.start()
        
        results = []
        batch_start = time.time()
        
        logger.info(f"🚀 Worker {self.worker_id}: Processing batch of {len(batch_data)} items")
        
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Enviar trabajos a pool
                future_to_data = {
                    executor.submit(self.process_single, filter_func, data, **kwargs): data 
                    for data in batch_data
                }
                
                # Recoger resultados
                for future in as_completed(future_to_data):
                    try:
                        result = future.result(timeout=30)  # 30s timeout
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "success": False,
                            "error": f"Future failed: {str(e)}",
                            "worker_id": self.worker_id
                        })
        
        except Exception as e:
            logger.error(f"❌ Worker {self.worker_id}: Batch processing failed - {str(e)}")
            # Fallback: procesar secuencialmente
            for data in batch_data:
                result = self.process_single(filter_func, data, **kwargs)
                results.append(result)
        
        batch_time = time.time() - batch_start
        success_count = sum(1 for r in results if r.get("success", False))
        
        logger.info(f"✅ Worker {self.worker_id}: Batch completed - {success_count}/{len(batch_data)} successful in {batch_time:.2f}s")
        
        return results
    
    def start(self):
        """🚀 Iniciar worker"""
        self.is_running = True
        self.start_time = time.time()
        logger.info(f"🚀 Worker {self.worker_id} started")
    
    def stop(self):
        """🛑 Detener worker"""
        self.is_running = False
        uptime = time.time() - (self.start_time or time.time())
        logger.info(f"🛑 Worker {self.worker_id} stopped - Uptime: {uptime:.2f}s, Processed: {self.processed_count}, Errors: {self.error_count}")
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Obtener estadísticas del worker"""
        uptime = time.time() - (self.start_time or time.time()) if self.is_running else 0
        
        return {
            "worker_id": self.worker_id,
            "filter_type": self.filter_type,
            "max_workers": self.max_workers,
            "is_running": self.is_running,
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "uptime": uptime,
            "success_rate": (self.processed_count / max(1, self.processed_count + self.error_count)) * 100
        }

class WorkerPool:
    """
    🏭 Pool de workers especializados por tipo de filtro
    
    Gestiona múltiples FilterWorkers para diferentes tipos de operaciones
    """
    
    def __init__(self):
        """Inicializar pool de workers"""
        self.workers: Dict[str, FilterWorker] = {}
        self.worker_counter = 0
        
        # Crear workers especializados
        self._create_specialized_workers()
        
        logger.info(f"🏭 WorkerPool initialized with {len(self.workers)} workers")
    
    def _create_specialized_workers(self):
        """🎯 Crear workers especializados por tipo de operación"""
        
        # Worker para filtros I/O bound (threading-friendly)
        io_worker = FilterWorker(
            worker_id=self._get_next_id(),
            filter_type="io",
            max_workers=min(4, mp.cpu_count())  # Limitado para I/O
        )
        self.workers["io"] = io_worker
        
        # Worker para filtros CPU bound (multiprocessing-heavy)
        cpu_worker = FilterWorker(
            worker_id=self._get_next_id(),
            filter_type="cpu", 
            max_workers=mp.cpu_count()  # Usar todos los cores
        )
        self.workers["cpu"] = cpu_worker
        
        # Worker para filtros mixtos
        mixed_worker = FilterWorker(
            worker_id=self._get_next_id(),
            filter_type="mixed",
            max_workers=mp.cpu_count() // 2  # Balance
        )
        self.workers["mixed"] = mixed_worker
    
    def _get_next_id(self) -> int:
        """🔢 Obtener siguiente ID de worker"""
        self.worker_counter += 1
        return self.worker_counter
    
    def get_worker(self, filter_type: str = "cpu") -> FilterWorker:
        """
        🎯 Obtener worker apropiado para tipo de filtro
        
        Args:
            filter_type: Tipo de filtro ("io", "cpu", "mixed")
            
        Returns:
            FilterWorker apropiado
        """
        if filter_type not in self.workers:
            logger.warning(f"⚠️ Filter type '{filter_type}' not found, using 'cpu' worker")
            filter_type = "cpu"
        
        return self.workers[filter_type]
    
    def process_with_best_worker(self, filter_name: str, filter_func: Callable, 
                                batch_data: List[Any], **kwargs) -> List[Dict[str, Any]]:
        """
        🧠 Seleccionar el mejor worker para un filtro específico
        
        Args:
            filter_name: Nombre del filtro
            filter_func: Función de filtro
            batch_data: Datos a procesar
            **kwargs: Argumentos adicionales
            
        Returns:
            Resultados del procesamiento
        """
        # Mapeo de filtros a tipos de worker
        filter_to_worker_type = {
            # I/O bound filters
            "resize": "io",
            "blur": "io", 
            "brightness": "io",
            
            # CPU bound filters
            "sharpen": "cpu",
            "edges": "cpu",
            "heavy_sharpen": "cpu",
            "edge_detection": "cpu",
            
            # Mixed filters
            "complex": "mixed"
        }
        
        worker_type = filter_to_worker_type.get(filter_name, "cpu")
        worker = self.get_worker(worker_type)
        
        logger.info(f"🎯 Using {worker_type} worker (ID: {worker.worker_id}) for filter: {filter_name}")
        
        return worker.process_batch(filter_func, batch_data, **kwargs)
    
    def start_all(self):
        """🚀 Iniciar todos los workers"""
        for worker in self.workers.values():
            worker.start()
        logger.info("🚀 All workers started")
    
    def stop_all(self):
        """🛑 Detener todos los workers"""
        for worker in self.workers.values():
            worker.stop()
        logger.info("🛑 All workers stopped")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """📊 Obtener estadísticas del pool completo"""
        stats = {
            "total_workers": len(self.workers),
            "workers": {}
        }
        
        for worker_type, worker in self.workers.items():
            stats["workers"][worker_type] = worker.get_stats()
        
        # Estadísticas agregadas
        total_processed = sum(w.processed_count for w in self.workers.values())
        total_errors = sum(w.error_count for w in self.workers.values())
        
        stats["aggregate"] = {
            "total_processed": total_processed,
            "total_errors": total_errors,
            "overall_success_rate": (total_processed / max(1, total_processed + total_errors)) * 100
        }
        
        return stats

# =====================================================================
# 🧪 DEMO Y TESTING
# =====================================================================

def demo_filter_worker():
    """🎭 Demo de FilterWorker para testing"""
    print("🔧 DEMO: FilterWorker")
    
    # Función de filtro simulada
    def dummy_heavy_filter(data):
        """Simular filtro CPU-intensivo"""
        time.sleep(1.0)  # Simular trabajo pesado
        return f"processed_{data}"
    
    # Test worker individual
    worker = FilterWorker(worker_id=1, filter_type="cpu", max_workers=2)
    worker.start()
    
    # Test batch processing
    test_data = ["img1", "img2", "img3", "img4"]
    results = worker.process_batch(dummy_heavy_filter, test_data)
    
    print(f"📊 Results: {len(results)} processed")
    for i, result in enumerate(results):
        status = "✅" if result.get("success") else "❌"
        time_taken = result.get("processing_time", 0)
        print(f"  {status} Item {i+1}: {time_taken:.2f}s")
    
    # Stats
    stats = worker.get_stats()
    print(f"📈 Worker Stats: {stats}")
    
    worker.stop()
    print("✅ Demo completed")

def demo_worker_pool():
    """🏭 Demo de WorkerPool"""
    print("\n🏭 DEMO: WorkerPool")
    
    def light_filter(data):
        time.sleep(0.1)
        return f"light_{data}"
    
    def heavy_filter(data):
        time.sleep(0.5)
        return f"heavy_{data}"
    
    # Setup pool
    pool = WorkerPool()
    pool.start_all()
    
    # Test diferentes tipos de filtros
    test_data = ["img1", "img2"]
    
    print("🧵 Testing I/O bound filter...")
    io_results = pool.process_with_best_worker("resize", light_filter, test_data)
    
    print("🔄 Testing CPU bound filter...")
    cpu_results = pool.process_with_best_worker("sharpen", heavy_filter, test_data)
    
    # Pool stats
    stats = pool.get_pool_stats()
    print(f"📊 Pool Stats: {stats}")
    
    pool.stop_all()
    print("✅ Pool demo completed")

if __name__ == "__main__":
    # Demo individual worker
    demo_filter_worker()
    
    # Demo worker pool
    demo_worker_pool() 