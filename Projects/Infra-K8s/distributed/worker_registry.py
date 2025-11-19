import redis
import json
import time
import threading
from typing import Dict, List, Optional

class WorkerRegistry:
    """
    Redis-based service discovery and health monitoring for distributed workers.
    Handles worker registration, heartbeats, and failure detection.
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db, 
            decode_responses=True
        )
        self.workers_key = 'workers'
        self.heartbeat_interval = 30  # seconds
        self.worker_timeout = 90  # seconds (3 missed heartbeats)
        
    def register_worker(self, worker_id: str, capabilities: List[str], 
                       host: str = 'localhost', port: int = None) -> bool:
        """
        Register a new worker in the registry.
        
        Args:
            worker_id: Unique identifier for the worker
            capabilities: List of filter types this worker can handle
            host: Worker host address
            port: Worker port (if applicable)
            
        Returns:
            True if registration successful
        """
        worker_data = {
            'id': worker_id,
            'capabilities': json.dumps(capabilities),
            'host': host,
            'port': port or '',
            'status': 'active',
            'registered_at': time.time(),
            'last_heartbeat': time.time(),
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0
        }
        
        try:
            # Convert all values to strings for Redis storage
            worker_data_str = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in worker_data.items()}
            self.redis_client.hset(self.workers_key, worker_id, json.dumps(worker_data))
            print(f"✅ Worker {worker_id} registered successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to register worker {worker_id}: {e}")
            return False
    
    def unregister_worker(self, worker_id: str) -> bool:
        """
        Remove worker from registry.
        
        Args:
            worker_id: Worker to remove
            
        Returns:
            True if removal successful
        """
        try:
            result = self.redis_client.hdel(self.workers_key, worker_id)
            if result:
                print(f"✅ Worker {worker_id} unregistered")
                return True
            else:
                print(f"⚠️ Worker {worker_id} was not found in registry")
                return False
        except Exception as e:
            print(f"❌ Failed to unregister worker {worker_id}: {e}")
            return False
    
    def heartbeat(self, worker_id: str, stats: Optional[Dict] = None) -> bool:
        """
        Update worker heartbeat and optional stats.
        
        Args:
            worker_id: Worker sending heartbeat
            stats: Optional performance statistics
            
        Returns:
            True if heartbeat recorded successfully
        """
        try:
            worker_data_json = self.redis_client.hget(self.workers_key, worker_id)
            if not worker_data_json:
                print(f"⚠️ Worker {worker_id} not found in registry")
                return False
            
            worker_data = json.loads(worker_data_json)
            worker_data['last_heartbeat'] = time.time()
            worker_data['status'] = 'active'
            
            # Update stats if provided
            if stats:
                worker_data.update(stats)
            
            self.redis_client.hset(self.workers_key, worker_id, json.dumps(worker_data))
            return True
            
        except Exception as e:
            print(f"❌ Failed to record heartbeat for {worker_id}: {e}")
            return False
    
    def get_worker_info(self, worker_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific worker.
        
        Args:
            worker_id: Worker to query
            
        Returns:
            Worker data dictionary or None if not found
        """
        try:
            worker_data_json = self.redis_client.hget(self.workers_key, worker_id)
            if not worker_data_json:
                return None
                
            worker_data = json.loads(worker_data_json)
            
            # Convert numeric fields
            numeric_fields = ['registered_at', 'last_heartbeat', 'tasks_completed', 
                            'tasks_failed', 'total_processing_time']
            for field in numeric_fields:
                if field in worker_data and worker_data[field]:
                    if field in ['tasks_completed', 'tasks_failed']:
                        worker_data[field] = int(worker_data[field])
                    else:
                        worker_data[field] = float(worker_data[field])
            
            # Parse capabilities back to list
            if 'capabilities' in worker_data:
                worker_data['capabilities'] = json.loads(worker_data['capabilities'])
            
            return worker_data
            
        except Exception as e:
            print(f"❌ Failed to get worker info for {worker_id}: {e}")
            return None
    
    def get_active_workers(self) -> List[Dict]:
        """
        Get list of all active workers (recent heartbeat).
        
        Returns:
            List of active worker data dictionaries
        """
        current_time = time.time()
        active_workers = []
        
        try:
            all_workers = self.redis_client.hgetall(self.workers_key)
            
            for worker_id, worker_data_json in all_workers.items():
                worker_data = json.loads(worker_data_json)
                last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                
                # Check if worker is considered active
                if current_time - last_heartbeat <= self.worker_timeout:
                    worker_data['id'] = worker_id
                    worker_data['is_active'] = True
                    worker_data['time_since_heartbeat'] = current_time - last_heartbeat
                    
                    # Parse capabilities
                    if 'capabilities' in worker_data:
                        worker_data['capabilities'] = json.loads(worker_data['capabilities'])
                    
                    active_workers.append(worker_data)
                else:
                    # Mark as inactive but don't remove (for debugging)
                    worker_data['status'] = 'inactive'
                    self.redis_client.hset(self.workers_key, worker_id, json.dumps(worker_data))
            
            return active_workers
            
        except Exception as e:
            print(f"❌ Failed to get active workers: {e}")
            return []
    
    def get_workers_by_capability(self, capability: str) -> List[Dict]:
        """
        Get workers that can handle a specific filter type.
        
        Args:
            capability: Filter type (e.g., 'resize', 'sharpen')
            
        Returns:
            List of matching worker data dictionaries
        """
        active_workers = self.get_active_workers()
        matching_workers = []
        
        for worker in active_workers:
            capabilities = worker.get('capabilities', [])
            if capability in capabilities or 'all' in capabilities:
                matching_workers.append(worker)
        
        return matching_workers
    
    def get_least_busy_worker(self, capability: str = None) -> Optional[Dict]:
        """
        Get the worker with the least number of completed tasks.
        
        Args:
            capability: Optional filter to workers with specific capability
            
        Returns:
            Worker data dictionary of least busy worker
        """
        if capability:
            workers = self.get_workers_by_capability(capability)
        else:
            workers = self.get_active_workers()
        
        if not workers:
            return None
        
        # Sort by tasks_completed (ascending)
        least_busy = min(workers, key=lambda w: w.get('tasks_completed', 0))
        return least_busy
    
    def cleanup_inactive_workers(self) -> int:
        """
        Remove workers that haven't sent heartbeat in a long time.
        
        Returns:
            Number of workers removed
        """
        current_time = time.time()
        removed_count = 0
        
        try:
            all_workers = self.redis_client.hgetall(self.workers_key)
            
            for worker_id, worker_data_json in all_workers.items():
                worker_data = json.loads(worker_data_json)
                last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                
                # Remove workers inactive for more than 5 minutes
                if current_time - last_heartbeat > 300:
                    self.redis_client.hdel(self.workers_key, worker_id)
                    removed_count += 1
                    print(f"🧹 Removed inactive worker: {worker_id}")
            
            return removed_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup inactive workers: {e}")
            return 0
    
    def get_registry_stats(self) -> Dict:
        """
        Get overall registry statistics.
        
        Returns:
            Dictionary with registry stats
        """
        active_workers = self.get_active_workers()
        all_workers = self.redis_client.hgetall(self.workers_key)
        
        total_tasks = sum(int(w.get('tasks_completed', 0)) for w in active_workers)
        total_failures = sum(int(w.get('tasks_failed', 0)) for w in active_workers)
        
        # Count capabilities
        capabilities = set()
        for worker in active_workers:
            worker_caps = worker.get('capabilities', [])
            capabilities.update(worker_caps)
        
        return {
            'total_workers': len(all_workers),
            'active_workers': len(active_workers),
            'total_tasks_completed': total_tasks,
            'total_failures': total_failures,
            'available_capabilities': list(capabilities),
            'success_rate': (total_tasks / (total_tasks + total_failures) * 100) if (total_tasks + total_failures) > 0 else 100
        }


class HeartbeatManager:
    """
    Manages automatic heartbeat sending for a worker.
    """
    
    def __init__(self, registry: WorkerRegistry, worker_id: str):
        self.registry = registry
        self.worker_id = worker_id
        self.running = False
        self.thread = None
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0
        }
    
    def start(self):
        """Start automatic heartbeat sending."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()
        print(f"❤️ Started heartbeat for worker {self.worker_id}")
    
    def stop(self):
        """Stop automatic heartbeat sending."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print(f"💔 Stopped heartbeat for worker {self.worker_id}")
    
    def update_stats(self, **kwargs):
        """Update worker statistics."""
        self.stats.update(kwargs)
    
    def _heartbeat_loop(self):
        """Internal heartbeat loop with auto-reregistration."""
        while self.running:
            try:
                # Check if worker is still registered
                worker_info = self.registry.get_worker_info(self.worker_id)
                if not worker_info:
                    print(f"⚠️ Worker {self.worker_id} not found in registry, re-registering...")
                    # Re-register with stored capabilities  
                    if hasattr(self, 'capabilities'):
                        success = self.registry.register_worker(
                            self.worker_id,
                            self.capabilities,
                            host=getattr(self, 'host', 'container')
                        )
                        if success:
                            print(f"✅ Worker {self.worker_id} re-registered successfully")
                        else:
                            print(f"❌ Failed to re-register worker {self.worker_id}")
                
                # Send heartbeat
                self.registry.heartbeat(self.worker_id, self.stats)
                time.sleep(self.registry.heartbeat_interval)
            except Exception as e:
                print(f"❌ Heartbeat failed for {self.worker_id}: {e}")
                time.sleep(5)  # Wait before retry


def test_worker_registry():
    """Test worker registry functionality."""
    try:
        registry = WorkerRegistry()
        
        # Test worker registration
        worker_id = "test_worker_1"
        capabilities = ["resize", "blur", "sharpen"]
        
        success = registry.register_worker(worker_id, capabilities)
        if success:
            print("✅ Worker registration successful")
        
        # Test heartbeat
        registry.heartbeat(worker_id, {'tasks_completed': 5})
        print("✅ Heartbeat sent")
        
        # Test getting active workers
        active = registry.get_active_workers()
        print(f"✅ Active workers: {len(active)}")
        
        # Test capability filtering
        resize_workers = registry.get_workers_by_capability("resize")
        print(f"✅ Workers with resize capability: {len(resize_workers)}")
        
        # Test stats
        stats = registry.get_registry_stats()
        print(f"✅ Registry stats: {stats}")
        
        # Cleanup
        registry.unregister_worker(worker_id)
        print("✅ Worker unregistered")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker registry test failed: {e}")
        return False


if __name__ == "__main__":
    test_worker_registry()