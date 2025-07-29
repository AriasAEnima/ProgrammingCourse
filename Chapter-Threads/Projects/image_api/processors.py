"""
🖼️ Image Processors - DÍA 1: Threading + Image Processing

Base para que los estudiantes implementen procesamiento de imágenes con threading.
Este archivo debe evolucionar durante la semana.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
import logging

# TODO DÍA 1: Importar librerías de procesamiento de imágenes
# from PIL import Image, ImageFilter, ImageEnhance
# import cv2
# import numpy as np

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    🎯 Procesador de imágenes con soporte para threading
    
    DÍA 1: Implementar threading básico
    DÍA 2: Migrar a multiprocessing para filtros pesados
    DÍA 3: Distribuir workers
    DÍA 4: Monitoring y CI/CD
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.processed_count = 0
        self.processing_lock = threading.Lock()
        
    # =====================================================================
    # 🔥 DÍA 1: IMPLEMENTAR ESTOS MÉTODOS CON THREADING
    # =====================================================================
    
    def process_single_image(self, image_path: str, filters: List[str]) -> Dict[str, Any]:
        """
        📸 Procesar una imagen individual con múltiples filtros
        
        DÍA 1: Usar imágenes reales de static/images/
        1. Cargar imagen real con PIL/basic processing
        2. Aplicar filtros básicos 
        3. Simular I/O processing time
        4. Retornar metadata real
        
        Args:
            image_path: Ruta de la imagen original (ej: static/images/sample_4k.jpg)
            filters: Lista de filtros a aplicar ['resize', 'blur', 'brightness']
            
        Returns:
            {
                'original_path': str,
                'processed_path': str,
                'filters_applied': List[str],
                'processing_time': float,
                'file_size': int,
                'thread_id': str
            }
        """
        start_time = time.time()
        thread_id = threading.get_ident()
        
        logger.info(f"🧵 Thread {thread_id}: Procesando {image_path} con filtros {filters}")
        
        # 📁 Procesar imagen REAL
        try:
            # Verificar que la imagen existe
            if not Path(image_path).exists():
                logger.warning(f"⚠️ Imagen no encontrada: {image_path}")
                # Usar imagen por defecto
                image_path = "static/images/sample_4k.jpg"
            
            # Simular procesamiento I/O-bound (leer, procesar, escribir)
            with open(image_path, 'rb') as f:
                image_data = f.read()
                file_size = len(image_data)
            
            # Simular filtros aplicados (tiempo de procesamiento realista)
            processing_delay = len(filters) * 0.3  # 0.3s por filtro
            time.sleep(processing_delay)
            
            # TODO DÍA 1: Los estudiantes implementarán filtros reales aquí
            # from .filters import FilterFactory
            # for filter_name in filters:
            #     image_data = FilterFactory.apply_filter(image_data, filter_name)
            
            with self.processing_lock:
                self.processed_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error procesando {image_path}: {e}")
            file_size = 0
            processing_delay = 0.1
            
        processing_time = time.time() - start_time
        
        return {
            'original_path': image_path,
            'processed_path': f'static/processed/{Path(image_path).stem}_filtered.jpg',
            'filters_applied': filters,
            'processing_time': processing_time,
            'file_size': file_size,
            'thread_id': str(thread_id),
            'status': 'success' if Path(image_path).exists() else 'used_fallback'
        }
    
    def process_batch_threading(self, image_paths: List[str], filters: List[str]) -> List[Dict[str, Any]]:
        """
        🚀 Procesar múltiples imágenes en paralelo con ThreadPoolExecutor
        
        TODO DÍA 1:
        1. Usar ThreadPoolExecutor
        2. Procesar imágenes en paralelo
        3. Recopilar resultados
        4. Manejar errores
        
        Args:
            image_paths: Lista de rutas de imágenes
            filters: Filtros a aplicar a todas
            
        Returns:
            Lista de resultados de procesamiento
        """
        logger.info(f"🚀 Iniciando procesamiento en lote: {len(image_paths)} imágenes")
        
        results = []
        start_time = time.time()
        
        # TODO DÍA 1: Implementar ThreadPoolExecutor aquí
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
                    result = future.result()
                    results.append(result)
                    logger.info(f"✅ Completado: {image_path}")
                except Exception as e:
                    logger.error(f"❌ Error procesando {image_path}: {e}")
                    results.append({
                        'original_path': image_path,
                        'error': str(e),
                        'thread_id': str(threading.get_ident())
                    })
        
        total_time = time.time() - start_time
        logger.info(f"🎯 Lote completado: {len(results)} resultados en {total_time:.2f}s")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Estadísticas del procesador"""
        return {
            'total_processed': self.processed_count,
            'max_workers': self.max_workers,
            'active_threads': threading.active_count()
        }

# =====================================================================
# 🧪 FUNCIONES DE TESTING PARA DÍA 1
# =====================================================================

def test_threading_performance():
    """
    🧪 Test de performance threading vs secuencial
    
    TODO DÍA 1: Los estudiantes ejecutan esto para comparar
    """
    import time
    
    # Datos de prueba
    test_images = [f'test_image_{i}.jpg' for i in range(10)]
    test_filters = ['resize', 'blur', 'brightness']
    
    processor = ImageProcessor(max_workers=4)
    
    print("🧪 Testing Threading vs Sequential...")
    
    # Test secuencial
    start = time.time()
    sequential_results = []
    for img in test_images:
        result = processor.process_single_image(img, test_filters)
        sequential_results.append(result)
    sequential_time = time.time() - start
    
    # Test threading
    start = time.time()
    threaded_results = processor.process_batch_threading(test_images, test_filters)
    threaded_time = time.time() - start
    
    # Resultados
    speedup = sequential_time / threaded_time
    print(f"📊 RESULTADOS:")
    print(f"   Sequential: {sequential_time:.2f}s")
    print(f"   Threading:  {threaded_time:.2f}s")
    print(f"   Speedup:    {speedup:.1f}x")
    print(f"   Efficiency: {speedup/processor.max_workers*100:.1f}%")

# =====================================================================
# 📋 TAREAS PARA ESTUDIANTES - DÍA 1
# =====================================================================

"""
📋 TODO LIST - DÍA 1 (Martes):

DURANTE SEGUIMIENTO (45 min):
✅ 1. Instalar PIL: pip install Pillow
✅ 2. Implementar carga de imagen básica
✅ 3. Crear primer filtro (resize)
✅ 4. Probar ThreadPoolExecutor

TRABAJO AUTÓNOMO (1h):
✅ 5. Implementar filtros: blur, brightness  
✅ 6. Crear carpeta static/processed/
✅ 7. Ejecutar test_threading_performance()
✅ 8. Documentar resultados

ENTREGABLE DÍA 1:
✅ API endpoint que procese imagen con 3 filtros en paralelo
✅ Comparación performance: sequential vs threading

DEMO:
curl -X POST -F "image=@test.jpg" http://localhost:8000/api/process/
"""

if __name__ == "__main__":
    # Para testing rápido
    test_threading_performance() 