"""
🎨 Image Filters - DÍA 1: Filtros básicos con threading

Implementación de filtros de imagen que evoluciona durante la semana.
"""

import time
import threading
import multiprocessing as mp
from typing import Tuple, Any
from pathlib import Path
import uuid
from datetime import datetime

# DÍA 2: Implementación real con PIL y OpenCV
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

class ImageFilters:
    
    @staticmethod
    def _get_output_path(original_path: str, filter_name: str, suffix: str = "") -> str:
        """
        📁 Generar ruta única para imagen procesada
        Ejemplo: sample_4k.jpg + resize -> sample_4k_resize_20250730_103045_abc123.jpg
        """
        original_path = Path(original_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:6]
        
        filename = f"{original_path.stem}_{filter_name}{suffix}_{timestamp}_{unique_id}{original_path.suffix}"
        output_path = Path("static/processed") / filename
        
        # Crear directorio si no existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return str(output_path)
    """
    🎨 Colección de filtros para procesamiento de imágenes
    
    DÍA 1: Filtros básicos con PIL
    DÍA 2: Filtros pesados con OpenCV
    DÍA 3: Filtros distribuidos
    """
    
    @staticmethod
    def resize_filter(image_data: Any, size: Tuple[int, int] = (800, 600)) -> dict:
        """
        📏 Redimensionar imagen
        
        DÍA 2: Implementación real con PIL + guardado de resultado
        Args:
            image_data: PIL Image object o path de imagen
            size: Nueva dimensión (ancho, alto)
        Returns:
            Dict con imagen procesada y metadata
        """
        print(f"🧵 Thread {threading.get_ident()}: Aplicando resize filter")
        start_time = time.time()
        
        try:
            if PIL_AVAILABLE:
                output_path = None
                # Si es un path, cargar imagen
                if isinstance(image_data, (str, Path)):
                    with Image.open(image_data) as img:
                        resized = img.resize(size, Image.Resampling.LANCZOS)
                        # 💾 Guardar imagen procesada
                        output_path = ImageFilters._get_output_path(str(image_data), "resize", f"_{size[0]}x{size[1]}")
                        resized.save(output_path, quality=95)
                        processing_time = time.time() - start_time
                        print(f"✅ Resize completed in {processing_time:.3f}s")
                        print(f"💾 Saved to: {output_path}")
                        return {
                            "image": resized,
                            "output_path": output_path,
                            "filter": "resize",
                            "duration": processing_time,
                            "size": size
                        }
                # Si ya es una imagen PIL
                elif hasattr(image_data, 'resize'):
                    resized = image_data.resize(size, Image.Resampling.LANCZOS)
                    processing_time = time.time() - start_time
                    print(f"✅ Resize completed in {processing_time:.3f}s")
                    return {
                        "image": resized,
                        "output_path": None,
                        "filter": "resize", 
                        "duration": processing_time,
                        "size": size
                    }
            
            # Fallback: simular procesamiento
            time.sleep(0.2)
            processing_time = time.time() - start_time
            print(f"⚠️ Resize simulated in {processing_time:.3f}s (PIL not available)")
            return {
                "image": image_data,
                "output_path": None,
                "filter": "resize",
                "duration": processing_time,
                "size": size
            }
            
        except Exception as e:
            print(f"❌ Resize error: {e}")
            time.sleep(0.2)  # Simular tiempo incluso en error
            return {
                "image": image_data,
                "output_path": None,
                "filter": "resize",
                "duration": 0.2,
                "size": size,
                "error": str(e)
            }
    
    @staticmethod
    def blur_filter(image_data: Any, radius: float = 2.0) -> dict:
        """
        🌫️ Aplicar efecto blur
        
        DÍA 2: Implementación real con PIL + guardado de resultado
        Args:
            image_data: PIL Image object o path de imagen
            radius: Intensidad del blur
        Returns:
            Dict con imagen procesada y metadata
        """
        print(f"🧵 Thread {threading.get_ident()}: Aplicando blur filter")
        start_time = time.time()
        
        try:
            if PIL_AVAILABLE:
                output_path = None
                # Si es un path, cargar imagen
                if isinstance(image_data, (str, Path)):
                    with Image.open(image_data) as img:
                        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
                        # 💾 Guardar imagen procesada
                        output_path = ImageFilters._get_output_path(str(image_data), "blur", f"_r{radius}")
                        blurred.save(output_path, quality=95)
                        processing_time = time.time() - start_time
                        print(f"✅ Blur completed in {processing_time:.3f}s")
                        print(f"💾 Saved to: {output_path}")
                        return {
                            "image": blurred,
                            "output_path": output_path,
                            "filter": "blur",
                            "duration": processing_time,
                            "radius": radius
                        }
                # Si ya es una imagen PIL
                elif hasattr(image_data, 'filter'):
                    blurred = image_data.filter(ImageFilter.GaussianBlur(radius=radius))
                    processing_time = time.time() - start_time
                    print(f"✅ Blur completed in {processing_time:.3f}s")
                    return {
                        "image": blurred,
                        "output_path": None,
                        "filter": "blur",
                        "duration": processing_time,
                        "radius": radius
                    }
            
            # Fallback: simular procesamiento
            time.sleep(0.3)
            processing_time = time.time() - start_time
            print(f"⚠️ Blur simulated in {processing_time:.3f}s (PIL not available)")
            return {
                "image": image_data,
                "output_path": None,
                "filter": "blur",
                "duration": processing_time,
                "radius": radius
            }
            
        except Exception as e:
            print(f"❌ Blur error: {e}")
            time.sleep(0.3)  # Simular tiempo incluso en error
            return {
                "image": image_data,
                "output_path": None,
                "filter": "blur",
                "duration": 0.3,
                "radius": radius,
                "error": str(e)
            }
    
    @staticmethod
    def brightness_filter(image_data: Any, factor: float = 1.2) -> dict:
        """
        ☀️ Ajustar brillo
        
        DÍA 2: Implementación real con PIL + guardado de resultado
        Args:
            image_data: PIL Image object o path de imagen
            factor: Factor de brillo (1.0 = sin cambio)
        Returns:
            Dict con imagen procesada y metadata
        """
        print(f"🧵 Thread {threading.get_ident()}: Aplicando brightness filter")
        start_time = time.time()
        
        try:
            if PIL_AVAILABLE:
                output_path = None
                # Si es un path, cargar imagen
                if isinstance(image_data, (str, Path)):
                    with Image.open(image_data) as img:
                        enhancer = ImageEnhance.Brightness(img)
                        brightened = enhancer.enhance(factor)
                        # 💾 Guardar imagen procesada
                        output_path = ImageFilters._get_output_path(str(image_data), "brightness", f"_f{factor}")
                        brightened.save(output_path, quality=95)
                        processing_time = time.time() - start_time
                        print(f"✅ Brightness completed in {processing_time:.3f}s")
                        print(f"💾 Saved to: {output_path}")
                        return {
                            "image": brightened,
                            "output_path": output_path,
                            "filter": "brightness",
                            "duration": processing_time,
                            "factor": factor
                        }
                # Si ya es una imagen PIL
                elif hasattr(image_data, 'mode'):  # PIL Image check
                    enhancer = ImageEnhance.Brightness(image_data)
                    brightened = enhancer.enhance(factor)
                    processing_time = time.time() - start_time
                    print(f"✅ Brightness completed in {processing_time:.3f}s")
                    return {
                        "image": brightened,
                        "output_path": None,
                        "filter": "brightness",
                        "duration": processing_time,
                        "factor": factor
                    }
            
            # Fallback: simular procesamiento
            time.sleep(0.1)
            processing_time = time.time() - start_time
            print(f"⚠️ Brightness simulated in {processing_time:.3f}s (PIL not available)")
            return {
                "image": image_data,
                "output_path": None,
                "filter": "brightness",
                "duration": processing_time,
                "factor": factor
            }
            
        except Exception as e:
            print(f"❌ Brightness error: {e}")
            time.sleep(0.1)  # Simular tiempo incluso en error
            return {
                "image": image_data,
                "output_path": None,
                "filter": "brightness",
                "duration": 0.1,
                "factor": factor,
                "error": str(e)
            }

    # =====================================================================
    # 🔥 DÍA 2: FILTROS PESADOS PARA MULTIPROCESSING  
    # =====================================================================
    
    @staticmethod
    def heavy_sharpen_filter(image_data: Any, intensity: int = 3) -> dict:
        """
        ⚡ Filtro pesado para DÍA 2 - requiere multiprocessing
        
        DÍA 2: Implementación real con OpenCV (CPU intensivo) + guardado de resultado
        Args:
            image_data: Imagen o path
            intensity: Intensidad del sharpening (1-5)
        Returns:
            Dict con imagen procesada y metadata
        """
        process_id = mp.current_process().pid
        print(f"🔄 Process {process_id}: Heavy sharpen filter (intensity={intensity})")
        start_time = time.time()
        
        try:
            if OPENCV_AVAILABLE and PIL_AVAILABLE:
                output_path = None
                # Cargar imagen
                if isinstance(image_data, (str, Path)):
                    # Leer con OpenCV
                    img_cv = cv2.imread(str(image_data))
                    if img_cv is None:
                        raise ValueError(f"Could not load image: {image_data}")
                elif hasattr(image_data, 'mode'):  # PIL Image
                    # Convertir PIL a OpenCV
                    img_cv = cv2.cvtColor(np.array(image_data), cv2.COLOR_RGB2BGR)
                else:
                    raise ValueError("Unsupported image format")
                
                # Aplicar sharpening kernel múltiples veces (CPU intensivo)
                kernel = np.array([[-1, -1, -1],
                                 [-1,  9, -1], 
                                 [-1, -1, -1]], dtype=np.float32)
                
                sharpened = img_cv.copy()
                for i in range(intensity):
                    sharpened = cv2.filter2D(sharpened, -1, kernel)
                    # Añadir trabajo extra CPU-intensivo
                    _ = np.sum(sharpened ** 2)  # Operación costosa
                
                # Convertir de vuelta a PIL
                sharpened_pil = Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
                
                # 💾 Guardar imagen procesada
                if isinstance(image_data, (str, Path)):
                    output_path = ImageFilters._get_output_path(str(image_data), "heavy_sharpen", f"_i{intensity}")
                    sharpened_pil.save(output_path, quality=95)
                
                processing_time = time.time() - start_time
                print(f"✅ Heavy sharpen completed in {processing_time:.3f}s (Process {process_id})")
                if output_path:
                    print(f"💾 Saved to: {output_path}")
                
                return {
                    "image": sharpened_pil,
                    "output_path": output_path,
                    "filter": "heavy_sharpen",
                    "duration": processing_time,
                    "intensity": intensity,
                    "process_id": process_id
                }
            
            # Fallback: simular procesamiento pesado
            time.sleep(2.0)
            processing_time = time.time() - start_time
            print(f"⚠️ Heavy sharpen simulated in {processing_time:.3f}s (OpenCV not available)")
            return {
                "image": image_data,
                "output_path": None,
                "filter": "heavy_sharpen",
                "duration": processing_time,
                "intensity": intensity,
                "process_id": process_id
            }
            
        except Exception as e:
            print(f"❌ Heavy sharpen error: {e}")
            time.sleep(2.0)  # Simular tiempo incluso en error
            return {
                "image": image_data,
                "output_path": None,
                "filter": "heavy_sharpen", 
                "duration": 2.0,
                "intensity": intensity,
                "process_id": process_id,
                "error": str(e)
            }
    
    @staticmethod
    def edge_detection_filter(image_data: Any, threshold1: int = 100, threshold2: int = 200) -> dict:
        """
        🔍 Detección de bordes - CPU intensivo
        
        DÍA 2: Implementación real con OpenCV (Canny edge detection) + guardado de resultado
        Args:
            image_data: Imagen o path
            threshold1: Primer threshold para Canny
            threshold2: Segundo threshold para Canny
        Returns:
            Dict con imagen procesada y metadata
        """
        process_id = mp.current_process().pid
        print(f"🔄 Process {process_id}: Edge detection filter")
        start_time = time.time()
        
        try:
            if OPENCV_AVAILABLE and PIL_AVAILABLE:
                output_path = None
                # Cargar imagen
                if isinstance(image_data, (str, Path)):
                    img_cv = cv2.imread(str(image_data))
                    if img_cv is None:
                        raise ValueError(f"Could not load image: {image_data}")
                elif hasattr(image_data, 'mode'):  # PIL Image
                    img_cv = cv2.cvtColor(np.array(image_data), cv2.COLOR_RGB2BGR)
                else:
                    raise ValueError("Unsupported image format")
                
                # Convertir a escala de grises
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                # Aplicar filtro Gaussiano (suavizado)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Detección de bordes Canny (CPU intensivo)
                edges = cv2.Canny(blurred, threshold1, threshold2)
                
                # Operaciones adicionales CPU-intensivas
                # Morphological operations para limpiar bordes
                kernel = np.ones((3, 3), np.uint8)
                edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
                
                # Añadir trabajo extra CPU-intensivo
                for i in range(5):
                    _ = np.fft.fft2(edges)  # Transformada de Fourier costosa
                
                # Convertir edges a imagen RGB para compatibilidad
                edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                edges_pil = Image.fromarray(edges_rgb)
                
                # 💾 Guardar imagen procesada
                if isinstance(image_data, (str, Path)):
                    output_path = ImageFilters._get_output_path(str(image_data), "edge_detection", f"_t{threshold1}_{threshold2}")
                    edges_pil.save(output_path, quality=95)
                
                processing_time = time.time() - start_time
                print(f"✅ Edge detection completed in {processing_time:.3f}s (Process {process_id})")
                if output_path:
                    print(f"💾 Saved to: {output_path}")
                
                return {
                    "image": edges_pil,
                    "output_path": output_path,
                    "filter": "edge_detection",
                    "duration": processing_time,
                    "threshold1": threshold1,
                    "threshold2": threshold2,
                    "process_id": process_id
                }
            
            # Fallback: simular procesamiento pesado
            time.sleep(1.5)
            processing_time = time.time() - start_time
            print(f"⚠️ Edge detection simulated in {processing_time:.3f}s (OpenCV not available)")
            return {
                "image": image_data,
                "output_path": None,
                "filter": "edge_detection",
                "duration": processing_time,
                "threshold1": threshold1,
                "threshold2": threshold2,
                "process_id": process_id
            }
            
        except Exception as e:
            print(f"❌ Edge detection error: {e}")
            time.sleep(1.5)  # Simular tiempo incluso en error
            return {
                "image": image_data,
                "output_path": None,
                "filter": "edge_detection",
                "duration": 1.5,
                "threshold1": threshold1,
                "threshold2": threshold2,
                "process_id": process_id,
                "error": str(e)
            }

# =====================================================================
# 🎯 FACTORY PATTERN PARA FILTROS
# =====================================================================

class FilterFactory:
    """🏭 Factory para crear filtros según tipo"""
    
    AVAILABLE_FILTERS = {
        # DÍA 1: Filtros básicos (threading)
        'resize': ImageFilters.resize_filter,
        'blur': ImageFilters.blur_filter,
        'brightness': ImageFilters.brightness_filter,
        
        # DÍA 2: Filtros pesados (multiprocessing)
        'sharpen': ImageFilters.heavy_sharpen_filter,
        'edges': ImageFilters.edge_detection_filter,
    }
    
    @classmethod
    def get_filter(cls, filter_name: str):
        """Obtener función de filtro por nombre"""
        if filter_name not in cls.AVAILABLE_FILTERS:
            raise ValueError(f"Filter '{filter_name}' not available. "
                           f"Available: {list(cls.AVAILABLE_FILTERS.keys())}")
        
        return cls.AVAILABLE_FILTERS[filter_name]
    
    @classmethod
    def apply_filter_chain(cls, image_data: Any, filter_names: list) -> Any:
        """
        🔗 Aplicar cadena de filtros secuencialmente
        
        DÍA 2: Actualizado para manejar dict return format con guardado de imágenes
        """
        result = image_data
        all_results = []
        
        for filter_name in filter_names:
            filter_func = cls.get_filter(filter_name)
            filter_result = filter_func(result)
            
            # Los filtros ahora devuelven dict con metadata
            if isinstance(filter_result, dict) and 'image' in filter_result:
                result = filter_result['image']  # Extraer imagen para siguiente filtro
                all_results.append(filter_result)  # Guardar metadata completa
                print(f"✅ Applied {filter_name}")
                if filter_result.get('output_path'):
                    print(f"💾 Saved: {filter_result['output_path']}")
            else:
                # Fallback para compatibilidad con filtros antiguos
                result = filter_result
                print(f"✅ Applied {filter_name}")
        
        # Retornar la imagen final + metadata de todos los filtros
        return {
            "final_image": result,
            "filter_results": all_results,
            "filters_applied": filter_names
        }

# =====================================================================
# 📋 EJEMPLO DE USO PARA ESTUDIANTES
# =====================================================================

def demo_filters():
    """🎭 Demo de filtros para testing"""
    print("🎨 DEMO: Image Filters")
    
    # Simular imagen
    fake_image = "test_image_data"
    
    # Test filtros individuales
    print("\n1. Filtros individuales:")
    result1 = ImageFilters.resize_filter(fake_image)
    result2 = ImageFilters.blur_filter(fake_image)
    result3 = ImageFilters.brightness_filter(fake_image)
    
    # Test cadena de filtros
    print("\n2. Cadena de filtros:")
    filter_chain = ['resize', 'blur', 'brightness']
    result_chain = FilterFactory.apply_filter_chain(fake_image, filter_chain)
    
    print("✅ Demo completado")

if __name__ == "__main__":
    demo_filters() 