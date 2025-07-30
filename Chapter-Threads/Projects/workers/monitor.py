"""
📊 Resource Monitor - DÍA 2: System Monitoring

Monitoreo de recursos del sistema (CPU, memoria) y health de workers
"""

import time
import threading
import multiprocessing as mp
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, asdict
from collections import deque
import logging
import json

try:
    import psutil
except ImportError:
    psutil = None
    print("⚠️ psutil not installed. Run: pip install psutil")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """📊 Métricas del sistema en un momento dado"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    cpu_count: int
    active_processes: int
    load_average: Optional[float] = None  # Unix only
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)

@dataclass
class WorkerMetrics:
    """👷 Métricas específicas de un worker/proceso"""
    worker_id: int
    process_id: int
    cpu_percent: float
    memory_mb: float
    status: str  # running, sleeping, zombie, etc.
    num_threads: int
    create_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)

class ResourceMonitor:
    """
    📊 Monitor de recursos del sistema y workers
    
    Trackea CPU, memoria, disco y health de procesos en tiempo real
    """
    
    def __init__(self, history_size: int = 100, sample_interval: float = 1.0):
        """
        Inicializar monitor
        
        Args:
            history_size: Cantidad de métricas históricas a mantener
            sample_interval: Intervalo entre muestras (segundos)
        """
        if not psutil:
            raise ImportError("psutil required for monitoring. Install with: pip install psutil")
        
        self.history_size = history_size
        self.sample_interval = sample_interval
        
        # Historial de métricas
        self.system_history: deque = deque(maxlen=history_size)
        self.worker_history: Dict[int, deque] = {}
        
        # Configuración de alertas
        self.alert_thresholds = {
            "cpu_high": 85.0,
            "memory_high": 90.0,
            "disk_high": 95.0
        }
        
        # Estado del monitor
        self.is_running = False
        self.start_time = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Callbacks para alertas
        self.alert_callbacks: List[Callable] = []
        
        # Procesos tracked
        self.tracked_pids: set = set()
        
        logger.info(f"📊 ResourceMonitor initialized - History: {history_size}, Interval: {sample_interval}s")
    
    def start(self):
        """🚀 Iniciar monitoreo"""
        if self.is_running:
            logger.warning("⚠️ Monitor already running")
            return
        
        self.is_running = True
        self.start_time = time.time()
        self._stop_event.clear()
        
        # Iniciar thread de monitoreo
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="ResourceMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("🚀 ResourceMonitor started")
    
    def stop(self):
        """🛑 Detener monitoreo"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        uptime = time.time() - (self.start_time or time.time())
        logger.info(f"🛑 ResourceMonitor stopped - Uptime: {uptime:.2f}s")
    
    def _monitoring_loop(self):
        """🔄 Loop principal de monitoreo"""
        logger.info("📊 Monitoring loop started")
        
        while not self._stop_event.is_set():
            try:
                # Capturar métricas del sistema
                system_metrics = self._capture_system_metrics()
                self.system_history.append(system_metrics)
                
                # Capturar métricas de workers
                self._capture_worker_metrics()
                
                # Verificar alertas
                self._check_alerts(system_metrics)
                
                # Log periódico (cada 10 muestras)
                if len(self.system_history) % 10 == 0:
                    logger.debug(f"📊 System: CPU {system_metrics.cpu_percent:.1f}%, "
                               f"Memory {system_metrics.memory_percent:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
            
            # Esperar próximo sample
            if self._stop_event.wait(self.sample_interval):
                break
        
        logger.info("📊 Monitoring loop stopped")
    
    def _capture_system_metrics(self) -> SystemMetrics:
        """📸 Capturar métricas del sistema"""
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Load average (Unix only)
        load_avg = None
        try:
            load_avg = psutil.getloadavg()[0]  # 1-minute load average
        except (AttributeError, OSError):
            pass  # Windows doesn't have load average
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            cpu_count=psutil.cpu_count(),
            active_processes=len(psutil.pids()),
            load_average=load_avg
        )
    
    def _capture_worker_metrics(self):
        """👷 Capturar métricas de workers específicos"""
        for pid in list(self.tracked_pids):  # Copy to avoid modification during iteration
            try:
                process = psutil.Process(pid)
                
                # Verificar si el proceso sigue existiendo
                if not process.is_running():
                    self.tracked_pids.discard(pid)
                    logger.info(f"🗑️ Removed dead process: {pid}")
                    continue
                
                # Capturar métricas
                worker_metrics = WorkerMetrics(
                    worker_id=pid,  # Usar PID como worker_id por simplicidad
                    process_id=pid,
                    cpu_percent=process.cpu_percent(),
                    memory_mb=process.memory_info().rss / 1024 / 1024,  # MB
                    status=process.status(),
                    num_threads=process.num_threads(),
                    create_time=process.create_time()
                )
                
                # Añadir a historial
                if pid not in self.worker_history:
                    self.worker_history[pid] = deque(maxlen=self.history_size)
                
                self.worker_history[pid].append(worker_metrics)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                # Proceso terminado o sin permisos
                self.tracked_pids.discard(pid)
                logger.debug(f"🗑️ Process {pid} no longer accessible: {e}")
            except Exception as e:
                logger.error(f"❌ Error monitoring process {pid}: {e}")
    
    def track_process(self, pid: int):
        """🎯 Empezar a trackear un proceso específico"""
        try:
            process = psutil.Process(pid)
            if process.is_running():
                self.tracked_pids.add(pid)
                logger.info(f"🎯 Now tracking process: {pid}")
            else:
                logger.warning(f"⚠️ Process {pid} is not running")
        except psutil.NoSuchProcess:
            logger.error(f"❌ Process {pid} does not exist")
        except Exception as e:
            logger.error(f"❌ Error tracking process {pid}: {e}")
    
    def untrack_process(self, pid: int):
        """🗑️ Dejar de trackear un proceso"""
        self.tracked_pids.discard(pid)
        if pid in self.worker_history:
            del self.worker_history[pid]
        logger.info(f"🗑️ Stopped tracking process: {pid}")
    
    def track_current_process(self):
        """🎯 Trackear el proceso actual"""
        current_pid = mp.current_process().pid
        self.track_process(current_pid)
    
    def _check_alerts(self, metrics: SystemMetrics):
        """🚨 Verificar condiciones de alerta"""
        alerts = []
        
        # CPU alert
        if metrics.cpu_percent > self.alert_thresholds["cpu_high"]:
            alerts.append({
                "type": "cpu_high",
                "message": f"High CPU usage: {metrics.cpu_percent:.1f}%",
                "value": metrics.cpu_percent,
                "threshold": self.alert_thresholds["cpu_high"]
            })
        
        # Memory alert
        if metrics.memory_percent > self.alert_thresholds["memory_high"]:
            alerts.append({
                "type": "memory_high", 
                "message": f"High memory usage: {metrics.memory_percent:.1f}%",
                "value": metrics.memory_percent,
                "threshold": self.alert_thresholds["memory_high"]
            })
        
        # Disk alert
        if metrics.disk_percent > self.alert_thresholds["disk_high"]:
            alerts.append({
                "type": "disk_high",
                "message": f"High disk usage: {metrics.disk_percent:.1f}%",
                "value": metrics.disk_percent,
                "threshold": self.alert_thresholds["disk_high"]
            })
        
        # Disparar callbacks de alerta
        for alert in alerts:
            logger.warning(f"🚨 ALERT: {alert['message']}")
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"❌ Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """📞 Añadir callback para alertas"""
        self.alert_callbacks.append(callback)
        logger.info(f"📞 Alert callback added: {callback.__name__}")
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """📊 Obtener métricas actuales del sistema"""
        if not self.system_history:
            return None
        return self.system_history[-1]
    
    def get_worker_metrics(self, pid: int) -> Optional[WorkerMetrics]:
        """👷 Obtener métricas actuales de un worker"""
        if pid not in self.worker_history or not self.worker_history[pid]:
            return None
        return self.worker_history[pid][-1]
    
    def get_system_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """📈 Obtener resumen de métricas del sistema"""
        if not self.system_history:
            return {}
        
        # Filtrar por ventana de tiempo
        cutoff_time = time.time() - (window_minutes * 60)
        recent_metrics = [m for m in self.system_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            recent_metrics = list(self.system_history)[-10:]  # Últimas 10 si no hay recientes
        
        # Calcular estadísticas
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            "window_minutes": window_minutes,
            "sample_count": len(recent_metrics),
            "cpu": {
                "current": cpu_values[-1] if cpu_values else 0,
                "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0
            },
            "memory": {
                "current": memory_values[-1] if memory_values else 0,
                "average": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0
            },
            "system": {
                "cpu_count": recent_metrics[-1].cpu_count if recent_metrics else 0,
                "active_processes": recent_metrics[-1].active_processes if recent_metrics else 0,
                "load_average": recent_metrics[-1].load_average if recent_metrics else None
            }
        }
    
    def get_worker_summary(self, pid: int) -> Dict[str, Any]:
        """👷 Obtener resumen de un worker específico"""
        if pid not in self.worker_history:
            return {}
        
        metrics = list(self.worker_history[pid])
        if not metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_mb for m in metrics]
        
        return {
            "worker_id": pid,
            "sample_count": len(metrics),
            "status": metrics[-1].status,
            "uptime": time.time() - metrics[-1].create_time,
            "cpu": {
                "current": cpu_values[-1],
                "average": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "current_mb": memory_values[-1],
                "average_mb": sum(memory_values) / len(memory_values),
                "max_mb": max(memory_values),
                "min_mb": min(memory_values)
            },
            "threads": metrics[-1].num_threads
        }
    
    def export_metrics(self, filename: str):
        """💾 Exportar métricas a archivo JSON"""
        data = {
            "export_time": time.time(),
            "monitor_uptime": time.time() - (self.start_time or time.time()),
            "system_metrics": [m.to_dict() for m in self.system_history],
            "worker_metrics": {
                str(pid): [m.to_dict() for m in metrics]
                for pid, metrics in self.worker_history.items()
            },
            "summary": self.get_system_summary()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Metrics exported to: {filename}")
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")

# =====================================================================
# 🧪 DEMO Y TESTING
# =====================================================================

def demo_basic_monitoring():
    """📊 Demo básico de monitoreo"""
    print("📊 DEMO: Basic Resource Monitoring")
    
    # Setup monitor
    monitor = ResourceMonitor(history_size=50, sample_interval=0.5)
    
    # Alert callback
    def alert_handler(alert):
        print(f"🚨 ALERT: {alert['message']}")
    
    monitor.add_alert_callback(alert_handler)
    monitor.start()
    
    # Trackear proceso actual
    monitor.track_current_process()
    
    # Simular algo de carga
    print("🔥 Generating some load...")
    
    def cpu_load():
        """Generar carga de CPU"""
        end_time = time.time() + 3
        while time.time() < end_time:
            _ = [i**2 for i in range(1000)]
    
    # Ejecutar carga en thread separado
    import threading
    load_thread = threading.Thread(target=cpu_load)
    load_thread.start()
    
    # Monitorear por unos segundos
    time.sleep(5)
    
    # Mostrar métricas
    current = monitor.get_current_metrics()
    if current:
        print(f"📊 Current: CPU {current.cpu_percent:.1f}%, Memory {current.memory_percent:.1f}%")
    
    summary = monitor.get_system_summary(window_minutes=1)
    print(f"📈 Summary: {summary}")
    
    # Worker metrics si hay
    for pid in monitor.tracked_pids:
        worker_summary = monitor.get_worker_summary(pid)
        print(f"👷 Worker {pid}: {worker_summary}")
    
    monitor.stop()
    load_thread.join()
    print("✅ Basic monitoring demo completed")

def demo_stress_monitoring():
    """🔥 Demo con stress testing"""
    print("\n🔥 DEMO: Stress Monitoring")
    
    monitor = ResourceMonitor(sample_interval=0.2)
    monitor.start()
    
    # Crear workers simulados
    def heavy_worker():
        """Worker que consume CPU"""
        pid = mp.current_process().pid
        print(f"🔄 Heavy worker started: PID {pid}")
        
        # Trabajo pesado por 3 segundos
        end_time = time.time() + 3
        while time.time() < end_time:
            _ = [i**3 for i in range(5000)]
        
        print(f"✅ Heavy worker finished: PID {pid}")
    
    # Lanzar múltiples workers
    processes = []
    for i in range(2):
        p = mp.Process(target=heavy_worker)
        p.start()
        processes.append(p)
        monitor.track_process(p.pid)
        time.sleep(0.1)  # Stagger startup
    
    # Monitorear durante ejecución
    print("📊 Monitoring workers...")
    time.sleep(4)
    
    # Esperar que terminen
    for p in processes:
        p.join()
    
    # Mostrar resumen final
    print("\n📈 Final Summary:")
    summary = monitor.get_system_summary()
    print(f"System Summary: {summary}")
    
    # Export metrics
    monitor.export_metrics("stress_test_metrics.json")
    
    monitor.stop()
    print("✅ Stress monitoring demo completed")

if __name__ == "__main__":
    if not psutil:
        print("❌ psutil not available. Install with: pip install psutil")
        exit(1)
    
    # Demo básico
    demo_basic_monitoring()
    
    # Demo con stress
    demo_stress_monitoring() 