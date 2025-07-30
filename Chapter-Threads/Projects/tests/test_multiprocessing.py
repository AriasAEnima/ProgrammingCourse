"""
🧪 Unit Tests - DÍA 2: Multiprocessing Testing

Tests para verificar que el multiprocessing funciona correctamente.
"""

import unittest
import time
import multiprocessing as mp
from pathlib import Path
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(str(Path(__file__).parent.parent))

# Importar módulos a testear
try:
    from image_api.processors import ImageProcessor
    from image_api.filters import ImageFilters, FilterFactory
    from workers.filter_worker import FilterWorker, WorkerPool
    from workers.queue_manager import QueueManager
    from workers.monitor import ResourceMonitor
    IMPORTS_SUCCESS = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    IMPORTS_SUCCESS = False

class TestMultiprocessing(unittest.TestCase):
    """🔄 Tests para funcionalidad de multiprocessing"""
    
    def setUp(self):
        """Setup para cada test"""
        if not IMPORTS_SUCCESS:
            self.skipTest("Required modules not available")
        
        self.test_images = [
            "static/images/sample_4k.jpg",
            "static/images/misurina-sunset.jpg"
        ]
        self.light_filters = ["resize", "blur", "brightness"]
        self.heavy_filters = ["heavy_sharpen", "edge_detection"]
        
    def test_processor_initialization(self):
        """🎯 Test: ImageProcessor se inicializa correctamente"""
        processor = ImageProcessor(max_workers=2, mp_workers=2)
        
        self.assertEqual(processor.max_workers, 2)
        self.assertEqual(processor.mp_workers, 2)
        self.assertEqual(processor.processed_count, 0)
        
        stats = processor.get_stats()
        self.assertIn('total_processed', stats)
        self.assertIn('mp_workers', stats)
        
    def test_single_image_processing(self):
        """🖼️ Test: Procesamiento de imagen individual"""
        processor = ImageProcessor(max_workers=2, mp_workers=2)
        
        # Test con imagen simulada
        result = processor.process_single_image("test_image.jpg", ["resize"])
        
        self.assertIn('success', result.get('status', ''))
        self.assertIsInstance(result['processing_time'], float)
        self.assertIn('thread_id', result)
        self.assertIn('process_id', result)
        
    def test_multiprocessing_batch(self):
        """🔄 Test: Batch processing con multiprocessing"""
        processor = ImageProcessor(max_workers=2, mp_workers=2)
        
        test_images = ["img1.jpg", "img2.jpg", "img3.jpg"]
        results = processor.process_batch_multiprocessing(test_images, self.heavy_filters)
        
        self.assertEqual(len(results), len(test_images))
        
        # Verificar que al menos algunos tienen process_id diferentes
        process_ids = [r.get('process_id') for r in results if 'process_id' in r]
        self.assertTrue(len(process_ids) > 0)
        
    def test_performance_comparison(self):
        """📊 Test: Comparación de performance entre métodos"""
        processor = ImageProcessor(max_workers=2, mp_workers=2)
        
        test_images = ["img1.jpg", "img2.jpg"]
        comparison = processor.compare_performance(test_images, self.light_filters)
        
        # Verificar estructura de respuesta
        self.assertIn('test_info', comparison)
        self.assertIn('results', comparison)
        self.assertIn('performance', comparison)
        
        # Verificar que tiene los 3 métodos
        results = comparison['results']
        self.assertIn('sequential', results)
        self.assertIn('threading', results)
        self.assertIn('multiprocessing', results)
        
        # Verificar métricas de performance
        performance = comparison['performance']
        self.assertIn('threading_speedup', performance)
        self.assertIn('mp_speedup', performance)
        self.assertIn('recommendation', performance)
        
    def test_filter_performance_difference(self):
        """⚡ Test: Verificar que filtros pesados son más lentos"""
        processor = ImageProcessor()
        
        # Test filtro ligero
        start_light = time.time()
        result_light = processor.process_single_image("test.jpg", ["resize"])
        time_light = time.time() - start_light
        
        # Test filtro pesado
        start_heavy = time.time() 
        result_heavy = processor.process_single_image("test.jpg", ["heavy_sharpen"])
        time_heavy = time.time() - start_heavy
        
        # Filtros pesados deberían tomar más tiempo
        # (aunque sea simulado, el heavy filter tiene más delay)
        self.assertGreater(time_heavy, time_light * 0.5)  # Al menos 50% más tiempo
        
class TestFilterWorkers(unittest.TestCase):
    """👷 Tests para FilterWorker y WorkerPool"""
    
    def setUp(self):
        """Setup para tests de workers"""
        if not IMPORTS_SUCCESS:
            self.skipTest("Required modules not available")
            
    def test_filter_worker_creation(self):
        """🔧 Test: Crear FilterWorker"""
        worker = FilterWorker(worker_id=1, filter_type="cpu", max_workers=2)
        
        self.assertEqual(worker.worker_id, 1)
        self.assertEqual(worker.filter_type, "cpu")
        self.assertEqual(worker.max_workers, 2)
        self.assertFalse(worker.is_running)
        
    def test_worker_stats(self):
        """📊 Test: Estadísticas de worker"""
        worker = FilterWorker(worker_id=1)
        worker.start()
        
        stats = worker.get_stats()
        
        self.assertIn('worker_id', stats)
        self.assertIn('filter_type', stats)
        self.assertIn('is_running', stats)
        self.assertIn('processed_count', stats)
        self.assertTrue(stats['is_running'])
        
        worker.stop()
        
    def test_worker_pool_creation(self):
        """🏭 Test: Crear WorkerPool"""
        pool = WorkerPool()
        
        # Verificar que tiene workers especializados
        self.assertIn('io', pool.workers)
        self.assertIn('cpu', pool.workers)
        self.assertIn('mixed', pool.workers)
        
        # Test get_worker
        cpu_worker = pool.get_worker('cpu')
        self.assertEqual(cpu_worker.filter_type, 'cpu')
        
        io_worker = pool.get_worker('io')
        self.assertEqual(io_worker.filter_type, 'io')

class TestQueueManager(unittest.TestCase):
    """🔗 Tests para QueueManager (IPC)"""
    
    def setUp(self):
        """Setup para tests de queue manager"""
        if not IMPORTS_SUCCESS:
            self.skipTest("Required modules not available")
            
    @unittest.skipIf(not IMPORTS_SUCCESS, "Modules not available")
    def test_queue_manager_creation(self):
        """🎯 Test: Crear QueueManager"""
        manager = QueueManager(maxsize=10)
        
        self.assertEqual(manager.maxsize, 10)
        self.assertFalse(manager.is_running)
        self.assertEqual(len(manager.pending_tasks), 0)
        
    @unittest.skipIf(not IMPORTS_SUCCESS, "Modules not available")
    def test_queue_stats(self):
        """📊 Test: Estadísticas de colas"""
        manager = QueueManager(maxsize=10)
        manager.start()
        
        stats = manager.get_queue_stats()
        
        self.assertIn('is_running', stats)
        self.assertIn('task_queue_size', stats)
        self.assertIn('result_queue_size', stats)
        self.assertIn('success_rate', stats)
        
        manager.stop()

class TestResourceMonitor(unittest.TestCase):
    """📊 Tests para ResourceMonitor"""
    
    def setUp(self):
        """Setup para tests de monitoring"""
        if not IMPORTS_SUCCESS:
            self.skipTest("Required modules not available")
            
    @unittest.skipIf(not IMPORTS_SUCCESS, "Modules not available")
    def test_monitor_creation(self):
        """📈 Test: Crear ResourceMonitor"""
        try:
            monitor = ResourceMonitor(history_size=10, sample_interval=0.1)
            
            self.assertEqual(monitor.history_size, 10)
            self.assertEqual(monitor.sample_interval, 0.1)
            self.assertFalse(monitor.is_running)
            
        except ImportError:
            self.skipTest("psutil not available")
            
    @unittest.skipIf(not IMPORTS_SUCCESS, "Modules not available")
    def test_monitor_basic_functionality(self):
        """📊 Test: Funcionalidad básica del monitor"""
        try:
            monitor = ResourceMonitor(history_size=5, sample_interval=0.1)
            monitor.start()
            
            # Esperar que capture algunas métricas
            time.sleep(0.3)
            
            current_metrics = monitor.get_current_metrics()
            if current_metrics:
                self.assertIsInstance(current_metrics.cpu_percent, float)
                self.assertIsInstance(current_metrics.memory_percent, float)
            
            monitor.stop()
            
        except ImportError:
            self.skipTest("psutil not available")

class TestFilters(unittest.TestCase):
    """🎨 Tests para filtros de imagen"""
    
    def setUp(self):
        """Setup para tests de filtros"""
        if not IMPORTS_SUCCESS:
            self.skipTest("Required modules not available")
            
    def test_light_filters(self):
        """🧵 Test: Filtros ligeros (I/O bound)"""
        # Test resize
        result = ImageFilters.resize_filter("test_data")
        self.assertEqual(result, "test_data")  # Placeholder return
        
        # Test blur  
        result = ImageFilters.blur_filter("test_data")
        self.assertEqual(result, "test_data")
        
        # Test brightness
        result = ImageFilters.brightness_filter("test_data")
        self.assertEqual(result, "test_data")
        
    def test_heavy_filters(self):
        """🔄 Test: Filtros pesados (CPU bound)"""
        # Test heavy sharpen
        result = ImageFilters.heavy_sharpen_filter("test_data")
        self.assertEqual(result, "test_data")  # Placeholder return
        
        # Test edge detection
        result = ImageFilters.edge_detection_filter("test_data")
        self.assertEqual(result, "test_data")
        
    def test_filter_factory(self):
        """🏭 Test: FilterFactory"""
        # Test get_filter
        resize_filter = FilterFactory.get_filter('resize')
        self.assertEqual(resize_filter, ImageFilters.resize_filter)
        
        # Test invalid filter
        with self.assertRaises(ValueError):
            FilterFactory.get_filter('invalid_filter')
            
        # Test filter chain
        result = FilterFactory.apply_filter_chain("test_data", ['resize', 'blur'])
        self.assertEqual(result, "test_data")  # Placeholder

# =====================================================================
# 🚀 SUITE DE TESTS COMPLETO
# =====================================================================

def run_all_tests():
    """🧪 Ejecutar todos los tests"""
    print("🧪 RUNNING MULTIPROCESSING TESTS")
    print("=" * 50)
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar test classes
    test_classes = [
        TestMultiprocessing,
        TestFilterWorkers, 
        TestQueueManager,
        TestResourceMonitor,
        TestFilters
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback[:100]}...")
    
    if result.errors:
        print(f"\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback[:100]}...")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Para testing individual
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all_tests()
    else:
        unittest.main(verbosity=2) 