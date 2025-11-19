import redis
import json
import uuid
import time
from typing import Dict, List, Optional

class DistributedTaskQueue:
    """
    Redis-based distributed task queue for image processing tasks.
    Handles task enqueueing, dequeueing, and status tracking.
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db, 
            decode_responses=True
        )
        self.task_queue = 'image_tasks'
        self.result_queue = 'image_results'
        
    def enqueue_task(self, task_data: Dict) -> str:
        """
        Enqueue a new image processing task.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            task_id: Unique identifier for the task
        """
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'data': task_data,
            'status': 'pending',
            'created_at': time.time(),
            'worker_id': None,
            'started_at': None,
            'completed_at': None
        }
        
        # Add to task queue
        self.redis_client.lpush(self.task_queue, json.dumps(task))
        
        # Store task metadata for tracking (convert all values to strings)
        task_str = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in task.items()}
        self.redis_client.hset(f'task:{task_id}', mapping=task_str)
        
        return task_id
    
    def get_task(self, worker_id: str, timeout: int = 5) -> Optional[Dict]:
        """
        Get next available task from queue (blocking operation).
        
        Args:
            worker_id: ID of the worker requesting the task
            timeout: Timeout in seconds for blocking pop
            
        Returns:
            Task dictionary or None if timeout
        """
        result = self.redis_client.brpop(self.task_queue, timeout=timeout)
        if not result:
            return None
            
        task = json.loads(result[1])
        task_id = task['id']
        
        # Mark task as started
        task['status'] = 'processing'
        task['worker_id'] = worker_id
        task['started_at'] = time.time()
        
        # Update task metadata (convert all values to strings)
        task_str = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in task.items()}
        self.redis_client.hset(f'task:{task_id}', mapping=task_str)
        
        return task
    
    def complete_task(self, task_id: str, result: Dict):
        """
        Mark task as completed and store result.
        
        Args:
            task_id: Task identifier
            result: Processing result data
        """
        task_key = f'task:{task_id}'
        task_data = self.redis_client.hgetall(task_key)
        
        if task_data:
            # Update task status
            updates = {
                'status': 'completed',
                'completed_at': str(time.time()),
                'result': json.dumps(result)
            }
            self.redis_client.hset(task_key, mapping=updates)
            
            # Store result for retrieval
            result_data = {
                'task_id': task_id,
                'result': result,
                'completed_at': time.time()
            }
            self.redis_client.lpush(self.result_queue, json.dumps(result_data))
    
    def fail_task(self, task_id: str, error: str):
        """
        Mark task as failed.
        
        Args:
            task_id: Task identifier
            error: Error message
        """
        task_key = f'task:{task_id}'
        updates = {
            'status': 'failed',
            'completed_at': str(time.time()),
            'error': error
        }
        self.redis_client.hset(task_key, mapping=updates)
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get current status of a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status dictionary or None if not found
        """
        task_data = self.redis_client.hgetall(f'task:{task_id}')
        if not task_data:
            return None
            
        # Convert numeric fields back to proper types
        if 'created_at' in task_data and task_data['created_at'] and task_data['created_at'] != 'None':
            task_data['created_at'] = float(task_data['created_at'])
        if 'started_at' in task_data and task_data['started_at'] and task_data['started_at'] != 'None':
            task_data['started_at'] = float(task_data['started_at'])
        if 'completed_at' in task_data and task_data['completed_at'] and task_data['completed_at'] != 'None':
            task_data['completed_at'] = float(task_data['completed_at'])
            
        return task_data
    
    def get_queue_stats(self) -> Dict:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        pending_tasks = self.redis_client.llen(self.task_queue)
        
        # Count tasks by status
        task_keys = self.redis_client.keys('task:*')
        status_counts = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}
        
        for key in task_keys:
            task_data = self.redis_client.hgetall(key)
            status = task_data.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
        
        return {
            'queue_length': pending_tasks,
            'total_tasks': len(task_keys),
            'status_breakdown': status_counts
        }
    
    def clear_completed_tasks(self, older_than_seconds: int = 3600):
        """
        Clean up completed tasks older than specified time.
        
        Args:
            older_than_seconds: Age threshold in seconds
        """
        current_time = time.time()
        task_keys = self.redis_client.keys('task:*')
        
        for key in task_keys:
            task_data = self.redis_client.hgetall(key)
            if (task_data.get('status') in ['completed', 'failed'] and 
                task_data.get('completed_at') and
                current_time - float(task_data['completed_at']) > older_than_seconds):
                self.redis_client.delete(key)


def test_redis_connection():
    """Test Redis connection and basic operations."""
    try:
        queue = DistributedTaskQueue()
        
        # Test connection
        queue.redis_client.ping()
        print("✅ Redis connection successful")
        
        # Test enqueue/dequeue
        task_id = queue.enqueue_task({
            'test': 'data',
            'filters': ['resize'],
            'image_path': 'test.jpg'
        })
        print(f"✅ Task enqueued: {task_id}")
        
        task = queue.get_task('test_worker', timeout=1)
        if task:
            print(f"✅ Task dequeued: {task['id']}")
            queue.complete_task(task_id, {'success': True})
            print("✅ Task completed")
        
        stats = queue.get_queue_stats()
        print(f"✅ Queue stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False


if __name__ == "__main__":
    test_redis_connection()