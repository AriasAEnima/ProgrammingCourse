"""
🌐 Distributed Processing Module

This module contains components for distributed image processing:
- Redis-based task queue
- Worker registry with health monitoring
- Distributed worker implementation
"""

__version__ = "1.0.0"

from .redis_queue import DistributedTaskQueue
from .worker_registry import WorkerRegistry, HeartbeatManager

__all__ = [
    'DistributedTaskQueue',
    'WorkerRegistry', 
    'HeartbeatManager'
]