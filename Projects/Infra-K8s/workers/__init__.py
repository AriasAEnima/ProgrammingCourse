"""
🔧 Workers Package - DÍA 2: Multiprocessing Workers

Componentes:
- filter_worker.py: ProcessPoolExecutor workers
- queue_manager.py: IPC communication
- monitor.py: Resource monitoring
"""

from .filter_worker import FilterWorker, WorkerPool
from .queue_manager import QueueManager
from .monitor import ResourceMonitor

__all__ = ['FilterWorker', 'WorkerPool', 'QueueManager', 'ResourceMonitor'] 