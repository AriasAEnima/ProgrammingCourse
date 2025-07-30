"""
🖼️ URLs para Image API

Endpoints para demostrar operaciones I/O-bound:
- Servir imágenes 4K
- Información de imágenes  
- Procesamiento lento simulado
- Estadísticas del servidor
"""

from django.urls import path
from . import views

urlpatterns = [
    # 🏠 Health check
    path('', views.health_check, name='health_check'),
    
    # 🖼️ Endpoints de imágenes
    path('image/4k/', views.serve_4k_image, name='serve_4k_image'),
    path('image/info/', views.get_image_info, name='get_image_info'),
    path('image/slow/', views.serve_slow_image, name='serve_slow_image'),
    
    # 📊 Estadísticas del servidor
    path('stats/', views.get_server_stats, name='get_server_stats'),
    
    # 🚀 PROJECT DAY 1: Batch processing endpoints
    path('process-batch/sequential/', views.process_batch_sequential, name='process_batch_sequential'),
    path('process-batch/threading/', views.process_batch_threading, name='process_batch_threading'),
    path('process-batch/compare/', views.compare_performance, name='compare_performance'),
    
    # 🔥 PROJECT DAY 2: Multiprocessing endpoints
    path('process-batch/multiprocessing/', views.process_batch_multiprocessing, name='process_batch_multiprocessing'),
    path('process-batch/compare-all/', views.compare_all_methods, name='compare_all_methods'),
    path('process-batch/stress/', views.stress_test, name='stress_test'),
] 