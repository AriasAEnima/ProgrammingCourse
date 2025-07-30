"""
📊 Threading vs Multiprocessing Benchmark - DÍA 2

Comparación de rendimiento entre threading y multiprocessing para diferentes tipos de filtros.
"""

import time
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any, Callable
import json
import argparse
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️ psutil not available. Install for detailed system metrics.")

class BenchmarkResult:
    """📊 Resultado de un benchmark"""
    
    def __init__(self, method: str, filter_type: str):
        self.method = method
        self.filter_type = filter_type
        self.start_time = None
        self.end_time = None
        self.total_time = 0.0
        self.items_processed = 0
        self.success_count = 0
        self.error_count = 0
        self.throughput = 0.0  # items/second
        
        # System metrics
        self.cpu_before = 0.0
        self.cpu_after = 0.0
        self.memory_before = 0.0
        self.memory_after = 0.0
        self.max_cpu_during = 0.0
        self.max_memory_during = 0.0
    
    def start(self):
        """🚀 Iniciar benchmark"""
        self.start_time = time.time()
        if PSUTIL_AVAILABLE:
            self.cpu_before = psutil.cpu_percent()
            self.memory_before = psutil.virtual_memory().percent
    
    def end(self):
        """🏁 Finalizar benchmark"""
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time
        
        if self.items_processed > 0:
            self.throughput = self.items_processed / self.total_time
        
        if PSUTIL_AVAILABLE:
            self.cpu_after = psutil.cpu_percent()
            self.memory_after = psutil.virtual_memory().percent
    
    def add_result(self, success: bool):
        """➕ Añadir resultado de procesamiento"""
        self.items_processed += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """📋 Convertir a diccionario"""
        return {
            "method": self.method,
            "filter_type": self.filter_type,
            "total_time": round(self.total_time, 3),
            "items_processed": self.items_processed,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "throughput": round(self.throughput, 2),
            "success_rate": round((self.success_count / max(1, self.items_processed)) * 100, 1),
            "cpu_usage": {
                "before": self.cpu_before,
                "after": self.cpu_after,
                "max_during": self.max_cpu_during
            } if PSUTIL_AVAILABLE else {},
            "memory_usage": {
                "before": self.memory_before,
                "after": self.memory_after,
                "max_during": self.max_memory_during
            } if PSUTIL_AVAILABLE else {}
        }

class FilterSimulator:
    """🎨 Simulador de filtros para benchmarking"""
    
    @staticmethod
    def io_bound_filter(data: str, duration: float = 0.1) -> str:
        """🧵 Filtro I/O bound (simula lectura/escritura)"""
        # Simular I/O con sleep
        time.sleep(duration)
        return f"io_processed_{data}"
    
    @staticmethod
    def cpu_bound_filter(data: str, complexity: int = 100000) -> str:
        """🔄 Filtro CPU bound (simula cálculo intensivo)"""
        # Simular trabajo de CPU
        result = 0
        for i in range(complexity):
            result += i ** 2
        
        return f"cpu_processed_{data}_{result % 1000}"
    
    @staticmethod
    def mixed_filter(data: str, io_duration: float = 0.05, cpu_complexity: int = 50000) -> str:
        """🔀 Filtro mixto (I/O + CPU)"""
        # Parte I/O
        time.sleep(io_duration)
        
        # Parte CPU
        result = 0
        for i in range(cpu_complexity):
            result += i ** 2
        
        return f"mixed_processed_{data}_{result % 1000}"

class PerformanceBenchmark:
    """🏃 Benchmark de rendimiento threading vs multiprocessing"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results: List[BenchmarkResult] = []
        
        # Configuración de test
        self.test_data_sizes = [5, 10, 20]
        self.worker_counts = [2, 4, mp.cpu_count()]
        
        logger.info(f"🏃 PerformanceBenchmark initialized - CPU cores: {mp.cpu_count()}")
    
    def run_sequential_benchmark(self, filter_func: Callable, data: List[str], 
                                filter_type: str) -> BenchmarkResult:
        """🔄 Benchmark secuencial (baseline)"""
        result = BenchmarkResult("sequential", filter_type)
        result.start()
        
        if self.verbose:
            print(f"🔄 Running sequential {filter_type} - {len(data)} items")
        
        for item in data:
            try:
                _ = filter_func(item)
                result.add_result(True)
            except Exception as e:
                if self.verbose:
                    print(f"❌ Sequential error: {e}")
                result.add_result(False)
        
        result.end()
        
        if self.verbose:
            print(f"✅ Sequential completed: {result.total_time:.2f}s, "
                  f"Throughput: {result.throughput:.1f} items/s")
        
        return result
    
    def run_threading_benchmark(self, filter_func: Callable, data: List[str],
                              filter_type: str, max_workers: int = None) -> BenchmarkResult:
        """🧵 Benchmark con ThreadPoolExecutor"""
        max_workers = max_workers or min(len(data), mp.cpu_count())
        result = BenchmarkResult(f"threading_{max_workers}", filter_type)
        result.start()
        
        if self.verbose:
            print(f"🧵 Running threading {filter_type} - {len(data)} items, {max_workers} workers")
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(filter_func, item) for item in data]
                
                for future in futures:
                    try:
                        _ = future.result(timeout=30)
                        result.add_result(True)
                    except Exception as e:
                        if self.verbose:
                            print(f"❌ Threading error: {e}")
                        result.add_result(False)
        
        except Exception as e:
            logger.error(f"❌ Threading benchmark failed: {e}")
        
        result.end()
        
        if self.verbose:
            print(f"✅ Threading completed: {result.total_time:.2f}s, "
                  f"Throughput: {result.throughput:.1f} items/s")
        
        return result
    
    def run_multiprocessing_benchmark(self, filter_func: Callable, data: List[str],
                                    filter_type: str, max_workers: int = None) -> BenchmarkResult:
        """🔄 Benchmark con ProcessPoolExecutor"""
        max_workers = max_workers or min(len(data), mp.cpu_count())
        result = BenchmarkResult(f"multiprocessing_{max_workers}", filter_type)
        result.start()
        
        if self.verbose:
            print(f"🔄 Running multiprocessing {filter_type} - {len(data)} items, {max_workers} workers")
        
        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(filter_func, item) for item in data]
                
                for future in futures:
                    try:
                        _ = future.result(timeout=30)
                        result.add_result(True)
                    except Exception as e:
                        if self.verbose:
                            print(f"❌ Multiprocessing error: {e}")
                        result.add_result(False)
        
        except Exception as e:
            logger.error(f"❌ Multiprocessing benchmark failed: {e}")
        
        result.end()
        
        if self.verbose:
            print(f"✅ Multiprocessing completed: {result.total_time:.2f}s, "
                  f"Throughput: {result.throughput:.1f} items/s")
        
        return result
    
    def run_comprehensive_benchmark(self, data_size: int = 10) -> List[BenchmarkResult]:
        """🎯 Benchmark comprensivo de todos los métodos"""
        print(f"\n🎯 COMPREHENSIVE BENCHMARK - {data_size} items")
        print("=" * 60)
        
        # Preparar datos de test
        test_data = [f"test_image_{i}" for i in range(data_size)]
        
        benchmark_results = []
        
        # Test cases: (filter_func, filter_type, description)
        test_cases = [
            (FilterSimulator.io_bound_filter, "io_bound", "I/O Bound (0.1s sleep)"),
            (FilterSimulator.cpu_bound_filter, "cpu_bound", "CPU Bound (100k iterations)"),
            (FilterSimulator.mixed_filter, "mixed", "Mixed (I/O + CPU)")
        ]
        
        for filter_func, filter_type, description in test_cases:
            print(f"\n📊 Testing: {description}")
            print("-" * 40)
            
            # Sequential baseline
            seq_result = self.run_sequential_benchmark(filter_func, test_data, filter_type)
            benchmark_results.append(seq_result)
            
            # Threading
            threading_result = self.run_threading_benchmark(filter_func, test_data, filter_type)
            benchmark_results.append(threading_result)
            
            # Multiprocessing
            mp_result = self.run_multiprocessing_benchmark(filter_func, test_data, filter_type)
            benchmark_results.append(mp_result)
            
            # Calcular speedups
            seq_time = seq_result.total_time
            threading_speedup = seq_time / threading_result.total_time if threading_result.total_time > 0 else 0
            mp_speedup = seq_time / mp_result.total_time if mp_result.total_time > 0 else 0
            
            print(f"📈 Speedups: Threading {threading_speedup:.2f}x, Multiprocessing {mp_speedup:.2f}x")
            
            # Determinar ganador
            if threading_result.total_time < mp_result.total_time:
                winner = f"🧵 Threading ({threading_speedup:.2f}x faster)"
            else:
                winner = f"🔄 Multiprocessing ({mp_speedup:.2f}x faster)"
            
            print(f"🏆 Winner for {filter_type}: {winner}")
        
        self.results.extend(benchmark_results)
        return benchmark_results
    
    def run_scaling_benchmark(self, filter_type: str = "cpu_bound") -> List[BenchmarkResult]:
        """📈 Benchmark de escalabilidad con diferentes números de workers"""
        print(f"\n📈 SCALING BENCHMARK - {filter_type}")
        print("=" * 50)
        
        # Seleccionar filtro
        filter_funcs = {
            "io_bound": FilterSimulator.io_bound_filter,
            "cpu_bound": FilterSimulator.cpu_bound_filter,
            "mixed": FilterSimulator.mixed_filter
        }
        
        filter_func = filter_funcs.get(filter_type, FilterSimulator.cpu_bound_filter)
        test_data = [f"test_image_{i}" for i in range(20)]  # Dataset fijo
        
        scaling_results = []
        
        # Test con diferentes números de workers
        worker_counts = [1, 2, 4, mp.cpu_count(), mp.cpu_count() * 2]
        
        for workers in worker_counts:
            print(f"\n👥 Testing with {workers} workers")
            
            # Threading
            threading_result = self.run_threading_benchmark(
                filter_func, test_data, f"{filter_type}_scaling", workers
            )
            scaling_results.append(threading_result)
            
            # Multiprocessing (solo hasta CPU count)
            if workers <= mp.cpu_count():
                mp_result = self.run_multiprocessing_benchmark(
                    filter_func, test_data, f"{filter_type}_scaling", workers
                )
                scaling_results.append(mp_result)
        
        self.results.extend(scaling_results)
        return scaling_results
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """📋 Generar reporte detallado de resultados"""
        if not self.results:
            logger.warning("⚠️ No results to report")
            return {}
        
        report = {
            "benchmark_info": {
                "timestamp": time.time(),
                "cpu_count": mp.cpu_count(),
                "python_version": f"{mp.sys.version_info.major}.{mp.sys.version_info.minor}",
                "total_tests": len(self.results)
            },
            "results": [result.to_dict() for result in self.results],
            "summary": self._generate_summary()
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"📄 Report saved to: {output_file}")
            except Exception as e:
                logger.error(f"❌ Failed to save report: {e}")
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """📊 Generar resumen de resultados"""
        if not self.results:
            return {}
        
        # Agrupar por tipo de filtro
        by_filter_type = {}
        for result in self.results:
            filter_type = result.filter_type
            if filter_type not in by_filter_type:
                by_filter_type[filter_type] = []
            by_filter_type[filter_type].append(result)
        
        summary = {}
        
        for filter_type, results in by_filter_type.items():
            # Encontrar el mejor método para cada tipo
            best_result = min(results, key=lambda r: r.total_time)
            worst_result = max(results, key=lambda r: r.total_time)
            
            # Calcular speedup
            baseline = next((r for r in results if r.method == "sequential"), None)
            if baseline:
                speedup = baseline.total_time / best_result.total_time
            else:
                speedup = 1.0
            
            summary[filter_type] = {
                "best_method": best_result.method,
                "best_time": best_result.total_time,
                "best_throughput": best_result.throughput,
                "worst_method": worst_result.method,
                "worst_time": worst_result.total_time,
                "speedup": round(speedup, 2),
                "recommendation": self._get_recommendation(filter_type, results)
            }
        
        return summary
    
    def _get_recommendation(self, filter_type: str, results: List[BenchmarkResult]) -> str:
        """💡 Generar recomendación basada en resultados"""
        threading_results = [r for r in results if "threading" in r.method]
        mp_results = [r for r in results if "multiprocessing" in r.method]
        
        if not threading_results or not mp_results:
            return "Insufficient data for recommendation"
        
        avg_threading_time = sum(r.total_time for r in threading_results) / len(threading_results)
        avg_mp_time = sum(r.total_time for r in mp_results) / len(mp_results)
        
        if filter_type in ["io_bound"]:
            if avg_threading_time < avg_mp_time:
                return "Use Threading - I/O bound workload benefits from threading"
            else:
                return "Use Multiprocessing - Unexpected result, verify GIL behavior"
        
        elif filter_type in ["cpu_bound"]:
            if avg_mp_time < avg_threading_time:
                return "Use Multiprocessing - CPU bound workload bypasses GIL"
            else:
                return "Use Threading - Overhead may be significant for small workloads"
        
        else:  # mixed
            if avg_mp_time < avg_threading_time * 0.8:
                return "Use Multiprocessing - CPU component dominates"
            elif avg_threading_time < avg_mp_time * 0.8:
                return "Use Threading - I/O component dominates"
            else:
                return "Hybrid approach - Use both based on task characteristics"

def run_benchmark(images: int = 10, verbose: bool = True, 
                 output: str = None, scaling: bool = False) -> Dict[str, Any]:
    """🚀 Ejecutar benchmark completo"""
    print("🚀 THREADING VS MULTIPROCESSING BENCHMARK")
    print("=" * 60)
    print(f"🖥️ System: {mp.cpu_count()} CPU cores")
    print(f"🔢 Test size: {images} images")
    print(f"📊 Verbose: {verbose}")
    
    benchmark = PerformanceBenchmark(verbose=verbose)
    
    # Benchmark comprensivo
    benchmark.run_comprehensive_benchmark(data_size=images)
    
    # Benchmark de escalabilidad si se solicita
    if scaling:
        benchmark.run_scaling_benchmark("cpu_bound")
        benchmark.run_scaling_benchmark("io_bound")
    
    # Generar reporte
    report = benchmark.generate_report(output_file=output)
    
    # Mostrar resumen
    print("\n🏆 FINAL SUMMARY")
    print("=" * 40)
    
    if "summary" in report:
        for filter_type, summary in report["summary"].items():
            print(f"\n📊 {filter_type.upper()}:")
            print(f"  🥇 Best: {summary['best_method']} ({summary['best_time']:.2f}s)")
            print(f"  📈 Speedup: {summary['speedup']}x")
            print(f"  💡 Recommendation: {summary['recommendation']}")
    
    return report

def compare_methods():
    """⚔️ Comparación rápida de métodos"""
    print("⚔️ QUICK COMPARISON")
    
    data = ["img1", "img2", "img3", "img4", "img5"]
    
    # Test I/O bound
    print("\n🧵 I/O Bound Test:")
    start = time.time()
    for item in data:
        FilterSimulator.io_bound_filter(item)
    seq_time = time.time() - start
    print(f"  Sequential: {seq_time:.2f}s")
    
    start = time.time()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(FilterSimulator.io_bound_filter, item) for item in data]
        for future in futures:
            future.result()
    threading_time = time.time() - start
    print(f"  Threading: {threading_time:.2f}s (Speedup: {seq_time/threading_time:.1f}x)")
    
    # Test CPU bound
    print("\n🔄 CPU Bound Test:")
    start = time.time()
    for item in data:
        FilterSimulator.cpu_bound_filter(item, complexity=20000)
    seq_time = time.time() - start
    print(f"  Sequential: {seq_time:.2f}s")
    
    start = time.time()
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(FilterSimulator.cpu_bound_filter, item, 20000) for item in data]
        for future in futures:
            future.result()
    mp_time = time.time() - start
    print(f"  Multiprocessing: {mp_time:.2f}s (Speedup: {seq_time/mp_time:.1f}x)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Threading vs Multiprocessing Benchmark")
    parser.add_argument("--images", type=int, default=10, help="Number of test images")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", type=str, help="Output file for results")
    parser.add_argument("--scaling", action="store_true", help="Run scaling benchmarks")
    parser.add_argument("--quick", action="store_true", help="Quick comparison only")
    
    args = parser.parse_args()
    
    if args.quick:
        compare_methods()
    else:
        run_benchmark(
            images=args.images,
            verbose=args.verbose,
            output=args.output,
            scaling=args.scaling
        ) 