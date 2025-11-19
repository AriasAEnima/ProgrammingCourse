"""
🖼️ Image API Views

Views para servir imágenes 4K y demostrar operaciones I/O-bound.
Perfecto para testing con Threading vs Multiprocessing.
"""

import os
import time
import json
import logging
import threading
import random
import traceback
from pathlib import Path

from django.http import HttpResponse, JsonResponse, Http404
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

# Import distributed components
from distributed.redis_queue import DistributedTaskQueue

logger = logging.getLogger(__name__)

def get_available_images():
    """🖼️ UTILITY: Get available images dynamically - NO MORE HARDCODED LISTS!"""
    static_images_path = Path('static/images')
    if static_images_path.exists():
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        images = []
        for img_path in static_images_path.glob('*'):
            if img_path.suffix.lower() in valid_extensions:
                images.append(str(img_path))
        return images
    return ["static/images/sample_4k.jpg"]  # Fallback

# ============================================================================
# 🏠 HEALTH CHECK ENDPOINT
# ============================================================================

@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        "status": "healthy",
        "service": "Django Image Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/",
            "4k_image": "/api/image/4k/",
            "image_info": "/api/image/info/",
            "slow_image": "/api/image/slow/"
        }
    })

@require_http_methods(["GET"])
def task_status(request, task_id):
    """
    📋 Get individual task status - distingue entre job failure vs worker failure
    
    Args:
        task_id: UUID del task a consultar
        
    Returns:
        Detailed task status with failure reasons
    """
    try:
        import os
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        task_queue = DistributedTaskQueue(redis_host, redis_port)
        
        task_status = task_queue.get_task_status(task_id)
        
        if not task_status:
            return JsonResponse({
                "error": f"Task {task_id} not found",
                "suggestion": "Verifique que el task_id sea correcto"
            }, status=404)
        
        # Parse task data for better presentation
        status_info = {
            "task_id": task_id,
            "status": task_status.get('status', 'unknown'),
            "created_at": task_status.get('created_at'),
            "started_at": task_status.get('started_at'),
            "completed_at": task_status.get('completed_at'),
        }
        
        # Add timing information
        if status_info['created_at'] and status_info['completed_at']:
            status_info['total_duration'] = status_info['completed_at'] - status_info['created_at']
        
        # Add result or error information
        if task_status.get('status') == 'completed':
            result_raw = task_status.get('result', '{}')
            try:
                status_info['result'] = json.loads(result_raw)
            except:
                status_info['result_raw'] = result_raw
                
        elif task_status.get('status') == 'failed':
            status_info['error'] = task_status.get('error', 'Unknown error')
            status_info['failure_type'] = 'job_failure'  # vs worker_failure
            
            # Analyze error type
            error_msg = status_info['error'].lower()
            if 'cannot handle filters' in error_msg:
                status_info['failure_reason'] = 'worker_capability_mismatch'
                status_info['explanation'] = 'Worker tomó task pero no puede manejar el filtro requerido'
            elif 'connection' in error_msg or 'timeout' in error_msg:
                status_info['failure_reason'] = 'communication_error'
                status_info['explanation'] = 'Error de comunicación con Redis o worker'
            else:
                status_info['failure_reason'] = 'processing_error'
                status_info['explanation'] = 'Error durante el procesamiento de la imagen'
        
        # Add raw task data for debugging
        status_info['raw_task_data'] = task_status
        
        return JsonResponse(status_info)
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Error getting task status: {e}")
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)

# ============================================================================
# 🖼️ IMAGE SERVING ENDPOINTS
# ============================================================================

@require_http_methods(["GET"])
def serve_4k_image(request):
    """
    🖼️ Endpoint principal: Sirve imagen 4K
    
    Este endpoint demuestra una operación I/O-bound típica:
    - Lee archivo grande del disco (4K image)
    - Envía respuesta HTTP
    - Perfecto para testing con concurrencia
    """
    start_time = time.time()
    
    # Path de la imagen 4K
    image_path = Path(settings.STATICFILES_DIRS[0]) / "images" / "sample_4k.jpg"
    
    logger.info(f"📸 Sirviendo imagen 4K: {image_path}")
    
    # Verificar que existe la imagen
    if not image_path.exists():
        logger.error(f"❌ Imagen no encontrada: {image_path}")
        return JsonResponse({
            "error": "Imagen 4K no encontrada",
            "message": "Por favor coloca tu imagen 4K en: static/images/sample_4k.jpg",
            "expected_path": str(image_path)
        }, status=404)
    
    try:
        # 📖 I/O OPERATION: Leer archivo del disco
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        # Calcular estadísticas
        file_size_mb = len(image_data) / (1024 * 1024)
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Imagen servida: {file_size_mb:.2f}MB en {processing_time:.3f}s")
        
        # Crear respuesta HTTP con la imagen
        response = HttpResponse(image_data, content_type='image/jpeg')
        response['Content-Length'] = len(image_data)
        response['X-File-Size-MB'] = f"{file_size_mb:.2f}"
        response['X-Processing-Time'] = f"{processing_time:.3f}"
        response['X-IO-Type'] = "I/O-bound"
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error sirviendo imagen: {e}")
        return JsonResponse({
            "error": "Error al servir imagen",
            "message": str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_image_info(request):
    """
    📊 Endpoint de información: Datos sobre la imagen sin enviarla
    
    Útil para:
    - Verificar que la imagen existe
    - Obtener metadata sin transferir datos
    - Testing rápido
    """
    image_path = Path(settings.STATICFILES_DIRS[0]) / "images" / "sample_4k.jpg"
    
    if not image_path.exists():
        return JsonResponse({
            "error": "Imagen no encontrada",
            "expected_path": str(image_path),
            "instructions": "Coloca tu imagen 4K en static/images/sample_4k.jpg"
        }, status=404)
    
    try:
        # Obtener estadísticas del archivo
        stat_info = image_path.stat()
        file_size_bytes = stat_info.st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        return JsonResponse({
            "status": "found",
            "filename": image_path.name,
            "path": str(image_path),
            "size_bytes": file_size_bytes,
            "size_mb": round(file_size_mb, 2),
            "is_4k_size": file_size_mb > 5,  # Rough estimate for 4K image
            "endpoints": {
                "download": "/api/image/4k/",
                "slow_version": "/api/image/slow/"
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "error": "Error accediendo imagen",
            "message": str(e)
        }, status=500)

@require_http_methods(["GET"])
def serve_slow_image(request):
    """
    🐌 Endpoint "lento": Simula procesamiento + I/O
    
    Útil para:
    - Demostrar diferencias dramáticas con threading
    - Simular operaciones más complejas
    - Testing de timeouts
    """
    start_time = time.time()
    
    # Simular procesamiento (podría ser resize, filters, etc.)
    delay = float(request.GET.get('delay', 2.0))
    logger.info(f"🐌 Simulando procesamiento por {delay}s...")
    time.sleep(delay)
    
    # Luego servir la imagen normalmente
    image_path = Path(settings.STATICFILES_DIRS[0]) / "images" / "sample_4k.jpg"
    
    if not image_path.exists():
        return JsonResponse({
            "error": "Imagen no encontrada para procesamiento lento",
            "expected_path": str(image_path)
        }, status=404)
    
    try:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        total_time = time.time() - start_time
        file_size_mb = len(image_data) / (1024 * 1024)
        
        logger.info(f"🐌 Imagen 'procesada' y servida: {total_time:.2f}s total")
        
        response = HttpResponse(image_data, content_type='image/jpeg')
        response['X-Processing-Time'] = f"{total_time:.3f}"
        response['X-Simulated-Delay'] = f"{delay:.1f}"
        response['X-File-Size-MB'] = f"{file_size_mb:.2f}"
        response['X-IO-Type'] = "I/O-bound + Processing"
        
        return response
        
    except Exception as e:
        return JsonResponse({
            "error": "Error en procesamiento lento",
            "message": str(e)
        }, status=500)

# ============================================================================
# 📊 STATISTICS ENDPOINT
# ============================================================================

@require_http_methods(["GET"])
def get_server_stats(request):
    """
    📊 Estadísticas del servidor
    
    Útil para monitoring durante load testing
    """
    import psutil
    import threading
    import multiprocessing
    
    # Información del sistema
    cpu_count = multiprocessing.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Información de threading (aproximada)
    active_threads = threading.active_count()
    
    return JsonResponse({
        "system": {
            "cpu_cores": cpu_count,
            "cpu_usage_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_percent": memory.percent,
            "active_threads": active_threads
        },
        "recommendations": {
            "threading": "Perfecto para este servidor (I/O-bound)",
            "multiprocessing": f"Máximo recomendado: {cpu_count} workers",
            "async": "Excelente para alta concurrencia"
        }
    })

# ============================================================================
# 🚀 PROJECT DAY 1: BATCH PROCESSING ENDPOINTS
# ============================================================================

import json
from django.views.decorators.csrf import csrf_exempt
from .processors import ImageProcessor
from .filters import FilterFactory

@csrf_exempt
@require_http_methods(["POST"])
def process_batch_sequential(request):
    """
    🐌 Procesamiento secuencial (LENTO) - para comparar con threading
    
    Demo de Day 1: Procesa múltiples filtros secuencialmente
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', ['resize', 'blur', 'brightness'])
        count = data.get('count', 5)
        
        start_time = time.time()
        
        # Procesamiento SECUENCIAL usando imágenes REALES
        processor = ImageProcessor()
        results = []
        
        # 🎯 IMPROVED: Get images dynamically
        available_images = get_available_images()
        
        for i in range(count):
            # Alternar entre las imágenes disponibles
            image_path = available_images[i % len(available_images)]
            result = processor.process_single_image(image_path, filters)
            results.append(result)
        
        total_time = time.time() - start_time
        
        return JsonResponse({
            "method": "sequential",
            "processed_count": len(results),
            "filters_used": filters,
            "total_time": round(total_time, 3),
            "avg_time_per_image": round(total_time / count, 3),
            "performance": "🐌 LENTO - sin concurrencia"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_batch_threading(request):
    """
    🚀 Procesamiento con THREADING (RÁPIDO) - objetivo Day 1
    
    Demo de Day 1: Muestra el speedup con threading
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', ['resize', 'blur', 'brightness'])
        count = data.get('count', 5)
        
        start_time = time.time()
        
        # Procesamiento con THREADING usando imágenes REALES
        processor = ImageProcessor()
        
        # 🎯 IMPROVED: Get images dynamically
        available_images = get_available_images()
        
        # Generar lista de imágenes reales para procesar
        real_images = [available_images[i % len(available_images)] for i in range(count)]
        results = processor.process_batch_threading(real_images, filters)
        
        total_time = time.time() - start_time
        
        return JsonResponse({
            "method": "threading",
            "processed_count": len(results),
            "filters_used": filters,
            "total_time": round(total_time, 3),
            "avg_time_per_image": round(total_time / count, 3),
            "speedup_estimate": "🚀 2-3x más rápido que secuencial",
            "performance": "⚡ RÁPIDO - con threading"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt 
@require_http_methods(["POST"])
def compare_performance(request):
    """
    📊 DEMO PRINCIPAL Day 1: Compara secuencial vs threading
    
    Este es el endpoint estrella para mostrar el speedup
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', ['resize', 'blur', 'brightness'])
        count = data.get('count', 5)
        
        processor = ImageProcessor()
        
        # Usar imágenes reales para ambos tests
        available_images = [
            "static/images/sample_4k.jpg",
            "static/images/Clocktower_Panorama_20080622_20mb.jpg"
        ]
        
        # Test SECUENCIAL con imágenes REALES
        start_seq = time.time()
        results_seq = []
        for i in range(count):
            image_path = available_images[i % len(available_images)]
            result = processor.process_single_image(image_path, filters)
            results_seq.append(result)
        time_sequential = time.time() - start_seq
        
        # Test THREADING con imágenes REALES
        start_thr = time.time()
        real_images = [available_images[i % len(available_images)] for i in range(count)]
        results_threading = processor.process_batch_threading(real_images, filters)
        time_threading = time.time() - start_thr
        
        # Calcular speedup
        speedup = round(time_sequential / time_threading, 2)
        
        return JsonResponse({
            "comparison": {
                "sequential": {
                    "time": round(time_sequential, 3),
                    "method": "🐌 Uno por uno",
                    "processed": len(results_seq)
                },
                "threading": {
                    "time": round(time_threading, 3), 
                    "method": "🚀 Paralelo",
                    "processed": len(results_threading)
                }
            },
            "results": {
                "speedup": f"{speedup}x",
                "improvement": f"{((speedup-1)*100):.1f}% más rápido",
                "recommendation": "🎯 Threading es perfecto para I/O-bound operations"
            },
            "filters_tested": filters,
            "images_processed": count
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# =====================================================================
# 🔥 DÍA 2: MULTIPROCESSING ENDPOINTS (NUEVO)
# =====================================================================

@csrf_exempt
@require_http_methods(["POST"])
def process_batch_multiprocessing(request):
    """
    🔄 Procesar lote de imágenes usando MULTIPROCESSING (DÍA 2)
    
    NUEVO para filtros CPU-intensivos como heavy_sharpen, edge_detection.
    Usa ProcessPoolExecutor para bypassed el GIL de Python.
    
    POST body: {"count": 3, "filters": ["heavy_sharpen", "edge_detection"]}
    """
    try:
        # Parse request
        data = json.loads(request.body)
        count = data.get('count', 3)
        filters = data.get('filters', ['heavy_sharpen', 'edge_detection'])
        
        # Validar filtros pesados
        heavy_filters = {"heavy_sharpen", "edge_detection", "sharpen", "edges"}
        if not any(f in heavy_filters for f in filters):
            logger.warning(f"⚠️ No heavy filters detected in {filters}, MP may not show advantage")
        
        # Imágenes disponibles
        static_dir = Path(settings.STATICFILES_DIRS[0])
        image_dir = static_dir / "images"
        
        available_images = []
        for img_file in image_dir.glob("*.jpg"):
            if img_file.stat().st_size > 100000:  # > 100KB
                available_images.append(str(img_file))
        
        if not available_images:
            return JsonResponse({
                "error": "No hay imágenes disponibles para procesamiento",
                "instructions": "Coloca imágenes .jpg en static/images/"
            }, status=404)
        
        from .processors import ImageProcessor
        processor = ImageProcessor(max_workers=4)
        
        # Test MULTIPROCESSING con imágenes REALES
        start_mp = time.time()
        real_images = [available_images[i % len(available_images)] for i in range(count)]
        results_mp = processor.process_batch_multiprocessing(real_images, filters)
        time_mp = time.time() - start_mp
        
        # Contar resultados exitosos
        success_count = sum(1 for r in results_mp if r.get('status') == 'success')
        
        return JsonResponse({
            "method": "🔄 Multiprocessing",
            "results": {
                "time": round(time_mp, 3),
                "processed": len(results_mp),
                "success_count": success_count,
                "success_rate": f"{(success_count/len(results_mp)*100):.1f}%",
                "throughput": f"{count/time_mp:.2f} images/sec"
            },
            "filters_tested": filters,
            "images_processed": count,
            "process_info": {
                "mp_workers": processor.mp_workers,
                "cpu_cores": processor.mp_workers,
                "filter_type": "CPU-intensive" if any(f in heavy_filters for f in filters) else "I/O-bound"
            },
            "recommendation": "🎯 Multiprocessing bypasses GIL for CPU-intensive work"
        })
        
    except Exception as e:
        logger.error(f"❌ Multiprocessing error: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt  
@require_http_methods(["POST"])
def compare_all_methods(request):
    """
    📊 Comparar ALL: Sequential vs Threading vs Multiprocessing (DÍA 2)
    
    NUEVO endpoint que ejecuta los 3 métodos y compara resultados.
    Muestra cuándo usar cada uno.
    
    POST body: {"count": 5, "filters": ["heavy_sharpen", "edge_detection"]}
    """
    try:
        # Parse request
        data = json.loads(request.body)
        count = data.get('count', 5)
        filters = data.get('filters', ['heavy_sharpen', 'edge_detection'])
        
        # Imágenes disponibles
        static_dir = Path(settings.STATICFILES_DIRS[0])
        image_dir = static_dir / "images"
        
        available_images = []
        for img_file in image_dir.glob("*.jpg"):
            if img_file.stat().st_size > 100000:  # > 100KB
                available_images.append(str(img_file))
        
        if not available_images:
            return JsonResponse({
                "error": "No hay imágenes disponibles",
                "instructions": "Coloca imágenes .jpg en static/images/"
            }, status=404)
        
        from .processors import ImageProcessor
        processor = ImageProcessor(max_workers=4)
        
        # Preparar imágenes para test
        test_images = [available_images[i % len(available_images)] for i in range(count)]
        
        # Ejecutar comparación completa usando el método del processor
        comparison = processor.compare_performance(test_images, filters)
        
        # Agregar información adicional para la respuesta
        comparison["api_info"] = {
            "endpoint": "/api/process-batch/compare-all/",
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "available_images": len(available_images),
            "images_used": test_images
        }
        
        return JsonResponse(comparison)
        
    except Exception as e:
        logger.error(f"❌ Compare all methods error: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])  
def stress_test(request):
    """
    🔥 Stress test: Procesar muchas imágenes simultáneamente (DÍA 2)
    
    NUEVO: Test de estrés para ver los límites del sistema.
    Usa multiprocessing para manejar cargas altas.
    
    POST body: {"count": 20, "filters": ["heavy_sharpen", "edge_detection", "resize"]}
    """
    try:
        # Parse request
        data = json.loads(request.body)
        count = data.get('count', 20)
        filters = data.get('filters', ['heavy_sharpen', 'edge_detection', 'resize'])
        
        # Validaciones de seguridad
        max_count = 50  # Límite para evitar sobrecargar el sistema
        if count > max_count:
            return JsonResponse({
                "error": f"Límite excedido. Máximo permitido: {max_count}",
                "requested": count
            }, status=400)
        
        # Imágenes disponibles
        static_dir = Path(settings.STATICFILES_DIRS[0])
        image_dir = static_dir / "images"
        
        available_images = []
        for img_file in image_dir.glob("*.jpg"):
            available_images.append(str(img_file))
        
        if not available_images:
            return JsonResponse({
                "error": "No hay imágenes disponibles para stress test"
            }, status=404)
        
        from .processors import ImageProcessor
        processor = ImageProcessor(max_workers=4)
        
        # Stress test con multiprocessing
        start_stress = time.time()
        test_images = [available_images[i % len(available_images)] for i in range(count)]
        
        # Usar multiprocessing para el stress test
        logger.info(f"🔥 Starting stress test: {count} images with filters {filters}")
        results = processor.process_batch_multiprocessing(test_images, filters)
        
        stress_time = time.time() - start_stress
        
        # Calcular estadísticas del stress test
        success_count = sum(1 for r in results if r.get('status') == 'success')
        error_count = len(results) - success_count
        avg_processing_time = sum(r.get('processing_time', 0) for r in results) / len(results)
        
        return JsonResponse({
            "stress_test_results": {
                "total_time": round(stress_time, 3),
                "images_processed": len(results),
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": f"{(success_count/len(results)*100):.1f}%",
                "throughput": f"{count/stress_time:.2f} images/sec",
                "avg_processing_time": round(avg_processing_time, 3)
            },
            "system_info": {
                "method": "Multiprocessing",
                "workers": processor.mp_workers,
                "filters_applied": filters,
                "stress_level": "HIGH" if count > 10 else "MEDIUM"
            },
            "performance_analysis": {
                "cpu_utilization": "High (multiprocessing)",
                "memory_usage": "Distributed across processes",
                "bottleneck": "CPU for heavy filters, I/O for light filters"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Stress test error: {e}")
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================================
# 🌐 DISTRIBUTED PROCESSING ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def process_batch_distributed(request):
    """
    🌐 Distributed batch processing using Redis queue and workers
    
    Distribuye tareas entre múltiples workers containerizados.
    """
    import json
    from distributed.redis_queue import DistributedTaskQueue
    from distributed.worker_registry import WorkerRegistry
    
    try:
        data = json.loads(request.body)
        filters = data.get('filters', ['resize'])
        filter_params = data.get('filter_params', {})
        count = data.get('count', 2)
        
        # Initialize distributed components with Docker environment variables
        import os
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        task_queue = DistributedTaskQueue(redis_host, redis_port)
        registry = WorkerRegistry(redis_host, redis_port, redis_db=0)
        
        # Check available workers
        active_workers = registry.get_active_workers()
        if not active_workers:
            return JsonResponse({
                "error": "No active workers available",
                "suggestion": "Start workers with: docker-compose up -d"
            }, status=503)
        
        # Prepare image list - Use real images
        image_paths = []
        static_dir = Path(settings.BASE_DIR) / 'static' / 'images'
        available_images = [
            'sample_4k.jpg',
            'Clocktower_Panorama_20080622_20mb.jpg'
        ]
        
        for i in range(count):
            image_path = static_dir / available_images[i % len(available_images)]
            image_paths.append(str(image_path))
        
        # Enqueue task for distributed processing
        task_data = {
            'filters': filters,
            'filter_params': filter_params,
            'images': image_paths,
            'distributed': True
        }
        
        start_time = time.time()
        task_id = task_queue.enqueue_task(task_data)
        
        # Return task ID immediately (ASYNC pattern)
        total_time = time.time() - start_time
        
        return JsonResponse({
            "success": True,
            "method": "distributed",
            "task_id": task_id,
            "processing_time": round(total_time, 3),
            "worker_info": {
                "active_workers": len(active_workers)
            },
            "status": "enqueued",
            "message": "Task queued successfully - check status with /api/task-status/{task_id}",
            "distributed_stats": {
                "queue_used": True,
                "fault_tolerant": True,
                "scalable": True
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        import traceback
        logger.error(f"❌ Distributed processing error: {e}")
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def workers_status(request):
    """
    👥 Get status of all distributed workers
    
    Endpoint para monitorear el estado de workers distribuidos.
    """
    try:
        import os
        from distributed.redis_queue import DistributedTaskQueue
        from distributed.worker_registry import WorkerRegistry
        
        # Use Docker environment variables for Redis connection
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        registry = WorkerRegistry(redis_host, redis_port, redis_db=0)
        task_queue = DistributedTaskQueue(redis_host, redis_port)
        
        # Get active workers
        active_workers = registry.get_active_workers()
        
        # Get registry and queue statistics
        registry_stats = registry.get_registry_stats()
        queue_stats = task_queue.get_queue_stats()
        
        # Format worker information
        workers_info = []
        for worker in active_workers:
            worker_info = {
                "id": worker['id'],
                "status": worker.get('status', 'unknown'),
                "capabilities": worker.get('capabilities', []),
                "last_heartbeat": worker.get('time_since_heartbeat', 0),
                "tasks_completed": worker.get('tasks_completed', 0),
                "tasks_failed": worker.get('tasks_failed', 0),
                "uptime": time.time() - worker.get('registered_at', time.time()),
                "health": "healthy" if worker.get('time_since_heartbeat', 0) < 60 else "warning"
            }
            workers_info.append(worker_info)
        
        return JsonResponse({
            "success": True,
            "timestamp": time.time(),
            "system_status": "healthy" if active_workers else "no_workers",
            "workers": {
                "active_count": len(active_workers),
                "total_registered": registry_stats['total_workers'],
                "workers_detail": workers_info
            },
            "queue_stats": {
                "pending_tasks": queue_stats['queue_length'],
                "total_tasks_processed": queue_stats['total_tasks'],
                "task_status_breakdown": queue_stats['status_breakdown']
            },
            "system_capabilities": registry_stats['available_capabilities'],
            "performance": {
                "total_tasks_completed": registry_stats['total_tasks_completed'],
                "total_failures": registry_stats['total_failures'],
                "success_rate": f"{registry_stats['success_rate']:.1f}%"
            },
            "recommendations": {
                "scaling": "Add more workers if queue_length > 10",
                "monitoring": "Check worker health if any show 'warning' status",
                "maintenance": "Consider restarting workers with high failure rates"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Workers status error: {e}")
        return JsonResponse({
            "error": str(e),
            "system_status": "error",
            "suggestion": "Check Redis connection and worker containers"
        }, status=500)

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'message': 'Django Image Processing API is running'
    })


@require_http_methods(["GET"])
def simple_metrics(request):
    """
    Simple metrics endpoint - Real metrics + Educational recommendations
    
    ⚠️  IMPORTANT: Scaling recommendations are educational only
    ⚠️  No automatic scaling is performed
    """
    try:
        # Import here to avoid errors if simple_monitoring not available
        from simple_monitoring.metrics_collector import SimpleMetricsCollector
        from simple_monitoring.recommendations import ScalingRecommendations
        
        # Get Redis connection info from environment
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        # Collect metrics
        collector = SimpleMetricsCollector(redis_host, redis_port)
        metrics = collector.collect_metrics()
        
        # Get scaling recommendations (educational)
        recommender = ScalingRecommendations()
        recommendation = recommender.analyze_metrics(metrics)
        scaling_config = recommender.get_scaling_config()
        
        return JsonResponse({
            'status': 'success',
            'metrics': metrics,
            'scaling_recommendation': {
                'action': recommendation.action,
                'current_workers': recommendation.current_workers,
                'recommended_workers': recommendation.recommended_workers,
                'reason': recommendation.reason,
                'confidence': recommendation.confidence,
                'urgency': recommendation.urgency,
                'note': '⚠️ Educational recommendations only - No automatic execution'
            },
            'scaling_config': scaling_config,
            'timestamp': time.time()
        })
        
    except ImportError:
        return JsonResponse({
            'status': 'error',
            'message': 'Simple monitoring system not available',
            'suggestion': 'Install psutil: pip install psutil',
            'timestamp': time.time()
        }, status=503)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to collect metrics: {str(e)}',
            'timestamp': time.time()
        }, status=500)

