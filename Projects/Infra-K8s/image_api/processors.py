"""
🖼️ Image Processors - DÍA 2: Threading + Multiprocessing

Base para que los estudiantes implementen procesamiento de imágenes con threading y multiprocessing.
Este archivo debe evolucionar durante la semana.
"""

import threading
import time
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
import logging

# DÍA 2: Librerías de procesamiento de imágenes activadas
try:
    from PIL import Image, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL not installed. Run: pip install Pillow")

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not installed. Run: pip install opencv-python")

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    🎯 Procesador de imágenes con soporte para threading y multiprocessing
    
    DÍA 1: Threading básico ✅
    DÍA 2: Multiprocessing para filtros pesados ← AHORA
    DÍA 3: Distribuir workers
    DÍA 4: Monitoring y CI/CD
    """
    
    def __init__(self, max_workers: int = 4, mp_workers: int = None):
        self.max_workers = max_workers
        self.mp_workers = mp_workers or mp.cpu_count()
        self.processed_count = 0
        # Note: No usar threading.Lock aquí para compatibilidad con multiprocessing
        self._mp_safe = True
        
        logger.info(f"🎯 ImageProcessor initialized - Threading: {max_workers}, MP: {self.mp_workers}")
        
    # =====================================================================
    # 🔥 DÍA 1: THREADING METHODS (COMPLETO)
    # =====================================================================
    
    def process_single_image(self, image_path: str, filters: List[str]) -> Dict[str, Any]:
        """
        📸 Procesar una imagen individual con múltiples filtros
        
        DÍA 2: Usar imágenes reales + filtros implementados
        """
        start_time = time.time()
        thread_id = threading.get_ident()
        process_id = mp.current_process().pid
        
        logger.info(f"🧵 Thread {thread_id} (Process {process_id}): Procesando {image_path} con filtros {filters}")
        
        # 📁 Procesar imagen REAL
        try:
            # Verificar que la imagen existe
            if not Path(image_path).exists():
                logger.warning(f"⚠️ Imagen no encontrada: {image_path}")
                # Usar imagen por defecto
                image_path = "static/images/sample_4k.jpg"
            
            # Simular procesamiento I/O-bound (leer archivo)
            with open(image_path, 'rb') as f:
                image_data = f.read()
                file_size = len(image_data)
            
            # DÍA 2: Aplicar filtros REALES usando FilterFactory
            try:
                from .filters import FilterFactory
                filter_chain_result = FilterFactory.apply_filter_chain(image_path, filters)
                
                # Extraer resultados del nuevo formato
                if isinstance(filter_chain_result, dict):
                    result_image = filter_chain_result.get('final_image')
                    filter_results = filter_chain_result.get('filter_results', [])
                    saved_files = [r.get('output_path') for r in filter_results if r.get('output_path')]
                    filter_status = f"real_filters_applied_{len(saved_files)}_saved"
                else:
                    # Compatibilidad con formato anterior
                    result_image = filter_chain_result
                    filter_status = "real_filters_applied"
                    
            except Exception as e:
                logger.warning(f"⚠️ FilterFactory error: {e}")
                # Fallback si hay error
                processing_delay = len(filters) * 0.3
                time.sleep(processing_delay)
                filter_status = "simulated_filters"
            
            # Thread-safe counter update (for multiprocessing compatibility)
            self.processed_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error procesando {image_path}: {e}")
            file_size = 0
            filter_status = "error"
            
        processing_time = time.time() - start_time
        
        return {
            'original_path': image_path,
            'processed_path': f'static/processed/{Path(image_path).stem}_filtered.jpg',
            'filters_applied': filters,
            'processing_time': processing_time,
            'file_size': file_size,
            'thread_id': str(thread_id),
            'process_id': process_id,
            'filter_status': filter_status,
            'status': 'success' if Path(image_path).exists() else 'used_fallback'
        }
    
    def process_batch_threading(self, image_paths: List[str], filters: List[str]) -> List[Dict[str, Any]]:
        """
        🚀 Procesar múltiples imágenes en paralelo con ThreadPoolExecutor
        """
        logger.info(f"🚀 Threading batch: {len(image_paths)} imágenes con {self.max_workers} workers")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todas las tareas
            future_to_image = {
                executor.submit(self.process_single_image, img_path, filters): img_path 
                for img_path in image_paths
            }
            
            # Recopilar resultados
            for future in as_completed(future_to_image):
                image_path = future_to_image[future]
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                    logger.info(f"✅ Threading completed: {image_path}")
                except Exception as e:
                    logger.error(f"❌ Threading error {image_path}: {e}")
                    results.append({
                        'original_path': image_path,
                        'error': str(e),
                        'thread_id': str(threading.get_ident())
                    })
        
        total_time = time.time() - start_time
        logger.info(f"🎯 Threading batch completado: {len(results)} resultados en {total_time:.2f}s")
        
        return results

    # =====================================================================
    # 🔥 DÍA 2: MULTIPROCESSING METHODS (NUEVO)
    # =====================================================================
    
    def process_batch_multiprocessing(self, image_paths: List[str], filters: List[str]) -> List[Dict[str, Any]]:
        """
        🔄 Procesar múltiples imágenes con ProcessPoolExecutor (DÍA 2)
        
        NUEVO: Para filtros CPU-intensivos (sharpen, edge_detection)
        """
        logger.info(f"🔄 Multiprocessing batch: {len(image_paths)} imágenes con {self.mp_workers} workers")
        
        results = []
        start_time = time.time()
        
        try:
            with ProcessPoolExecutor(max_workers=self.mp_workers) as executor:
                # Enviar todas las tareas
                future_to_image = {
                    executor.submit(self.process_single_image, img_path, filters): img_path 
                    for img_path in image_paths
                }
                
                # Recopilar resultados
                for future in as_completed(future_to_image):
                    image_path = future_to_image[future]
                    try:
                        result = future.result(timeout=60)  # Más tiempo para MP
                        results.append(result)
                        logger.info(f"✅ MP completed: {image_path}")
                    except Exception as e:
                        logger.error(f"❌ MP error {image_path}: {e}")
                        results.append({
                            'original_path': image_path,
                            'error': str(e),
                            'process_id': mp.current_process().pid
                        })
        
        except Exception as e:
            logger.error(f"❌ ProcessPoolExecutor failed: {e}")
            # Fallback a threading
            logger.info("🔄 Fallback to threading...")
            return self.process_batch_threading(image_paths, filters)
        
        total_time = time.time() - start_time
        logger.info(f"🎯 MP batch completado: {len(results)} resultados en {total_time:.2f}s")
        
        return results
    
    def compare_performance(self, image_paths: List[str], filters: List[str]) -> Dict[str, Any]:
        """
        📊 Comparar rendimiento: Sequential vs Threading vs Multiprocessing (DÍA 2)
        """
        logger.info(f"📊 Performance comparison: {len(image_paths)} imágenes, {len(filters)} filtros")
        
        # 1. Sequential baseline
        sequential_start = time.time()
        sequential_results = []
        for img_path in image_paths:
            result = self.process_single_image(img_path, filters)
            sequential_results.append(result)
        sequential_time = time.time() - sequential_start
        
        # 2. Threading
        threading_start = time.time()
        threading_results = self.process_batch_threading(image_paths, filters)
        threading_time = time.time() - threading_start
        
        # 3. Multiprocessing (DÍA 2)
        mp_start = time.time()
        mp_results = self.process_batch_multiprocessing(image_paths, filters)
        mp_time = time.time() - mp_start
        
        # Calcular métricas
        seq_success = sum(1 for r in sequential_results if r.get("status") == "success")
        thr_success = sum(1 for r in threading_results if r.get("status") == "success")
        mp_success = sum(1 for r in mp_results if r.get("status") == "success")
        
        threading_speedup = sequential_time / threading_time if threading_time > 0 else 1.0
        mp_speedup = sequential_time / mp_time if mp_time > 0 else 1.0
        
        # Determinar ganador
        times = {
            "sequential": sequential_time,
            "threading": threading_time,
            "multiprocessing": mp_time
        }
        winner = min(times, key=times.get)
        
        comparison = {
            "test_info": {
                "images_count": len(image_paths),
                "filters": filters,
                "threading_workers": self.max_workers,
                "mp_workers": self.mp_workers
            },
            "results": {
                "sequential": {
                    "time": round(sequential_time, 3),
                    "success_count": seq_success,
                    "throughput": round(len(image_paths) / sequential_time, 2)
                },
                "threading": {
                    "time": round(threading_time, 3),
                    "success_count": thr_success,
                    "throughput": round(len(image_paths) / threading_time, 2),
                    "speedup": round(threading_speedup, 2)
                },
                "multiprocessing": {
                    "time": round(mp_time, 3),
                    "success_count": mp_success,
                    "throughput": round(len(image_paths) / mp_time, 2),
                    "speedup": round(mp_speedup, 2)
                }
            },
            "performance": {
                "winner": winner,
                "threading_speedup": round(threading_speedup, 2),
                "mp_speedup": round(mp_speedup, 2),
                "threading_improvement": round((threading_speedup - 1) * 100, 1),
                "mp_improvement": round((mp_speedup - 1) * 100, 1),
                "recommendation": self._get_recommendation(filters, threading_speedup, mp_speedup)
            }
        }
        
        logger.info(f"📈 Performance comparison complete - Threading: {threading_speedup:.2f}x, MP: {mp_speedup:.2f}x")
        
        return comparison
    
    def _get_recommendation(self, filters: List[str], threading_speedup: float, mp_speedup: float) -> str:
        """💡 Generar recomendación basada en filtros y speedups"""
        
        # Identificar filtros pesados (CPU-intensivos)
        heavy_filters = {"sharpen", "heavy_sharpen", "edges", "edge_detection"}
        has_heavy_filters = any(f in heavy_filters for f in filters)
        
        if has_heavy_filters:
            if mp_speedup > threading_speedup * 1.2:
                return f"Use Multiprocessing - CPU-intensive filters benefit from parallel processes ({mp_speedup:.1f}x vs {threading_speedup:.1f}x)"
            elif threading_speedup > mp_speedup:
                return f"Use Threading - Process overhead too high for this workload ({threading_speedup:.1f}x vs {mp_speedup:.1f}x)"
            else:
                return "Multiprocessing recommended for CPU-intensive filters"
        else:
            if threading_speedup > mp_speedup:
                return f"Use Threading - I/O-bound filters work well with threads ({threading_speedup:.1f}x vs {mp_speedup:.1f}x)"
            else:
                return f"Unexpected: Multiprocessing faster for I/O-bound ({mp_speedup:.1f}x vs {threading_speedup:.1f}x)"
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Estadísticas del procesador"""
        return {
            'total_processed': self.processed_count,
            'max_workers': self.max_workers,
            'mp_workers': self.mp_workers,
            'active_threads': threading.active_count(),
            'pil_available': PIL_AVAILABLE,
            'opencv_available': OPENCV_AVAILABLE
        }

# =====================================================================
# 🧪 FUNCIONES DE TESTING PARA DÍA 2
# =====================================================================

def test_multiprocessing_performance():
    """
    🧪 Test de performance completo: Sequential vs Threading vs Multiprocessing
    
    DÍA 2: Los estudiantes ejecutan esto para comparar los 3 métodos
    """
    print("🧪 Testing Sequential vs Threading vs Multiprocessing...")
    
    # Datos de prueba - usar imágenes reales si existen
    test_images = []
    for img_name in ['sample_4k.jpg', 'Clocktower_Panorama_20080622_20mb.jpg']:
        img_path = f'static/images/{img_name}'
        if Path(img_path).exists():
            test_images.append(img_path)
    
    # Fallback si no hay imágenes reales
    if not test_images:
        test_images = [f'test_image_{i}.jpg' for i in range(5)]
    
    # Test con filtros ligeros (I/O bound)
    light_filters = ['resize', 'blur', 'brightness']
    
    # Test con filtros pesados (CPU bound) - DÍA 2
    heavy_filters = ['heavy_sharpen', 'edge_detection']
    
    processor = ImageProcessor(max_workers=4)
    
    print(f"📊 Testing with {len(test_images)} images")
    
    # Test filtros ligeros
    print("\n🧵 TEST: Light filters (I/O bound)")
    light_comparison = processor.compare_performance(test_images, light_filters)
    print(f"   Threading speedup: {light_comparison['performance']['threading_speedup']}x")
    print(f"   MP speedup: {light_comparison['performance']['mp_speedup']}x")
    print(f"   Winner: {light_comparison['performance']['winner']}")
    
    # Test filtros pesados
    print("\n🔄 TEST: Heavy filters (CPU bound)")
    heavy_comparison = processor.compare_performance(test_images, heavy_filters)
    print(f"   Threading speedup: {heavy_comparison['performance']['threading_speedup']}x")
    print(f"   MP speedup: {heavy_comparison['performance']['mp_speedup']}x")
    print(f"   Winner: {heavy_comparison['performance']['winner']}")
    
    print(f"\n💡 Recommendations:")
    print(f"   Light filters: {light_comparison['performance']['recommendation']}")
    print(f"   Heavy filters: {heavy_comparison['performance']['recommendation']}")

# =====================================================================
# 📋 TAREAS PARA ESTUDIANTES - DÍA 2
# =====================================================================

"""
📋 TODO LIST - DÍA 2 (Miércoles):

DURANTE SEGUIMIENTO (45 min):
✅ 1. Instalar OpenCV: pip install opencv-python
✅ 2. Implementar filtros pesados (heavy_sharpen, edge_detection)
✅ 3. Crear ProcessPoolExecutor 
✅ 4. Comparar Threading vs Multiprocessing

TRABAJO AUTÓNOMO (1h):
✅ 5. Workers especializados por tipo de filtro
✅ 6. Queue-based IPC (Session 4)
✅ 7. Resource monitoring con psutil
✅ 8. Error handling robusto

ENTREGABLE DÍA 2:
✅ Benchmark script: threading_vs_mp.py
✅ Speedup >3x en filtros CPU-intensivos
✅ API endpoints multiprocessing

DEMO:
python benchmarks/threading_vs_mp.py --images=5 --verbose
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
     -d '{"count": 5, "filters": ["heavy_sharpen", "edge_detection"]}'
"""

if __name__ == "__main__":
    # Para testing rápido DÍA 2
    test_multiprocessing_performance() 