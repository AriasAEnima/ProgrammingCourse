#!/usr/bin/env python3
"""
Distributed Image Processing Worker

This worker:
1. Connects to Redis queue for task distribution
2. Registers itself in worker registry
3. Processes image tasks using appropriate filters
4. Sends heartbeats for health monitoring
5. Handles graceful shutdown
"""

import os
import sys
import time
import signal
import logging
from typing import Dict, List
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distributed.redis_queue import DistributedTaskQueue
from distributed.worker_registry import WorkerRegistry, HeartbeatManager
from image_api.filters import FilterFactory
from image_api.processors import ImageProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/worker.log') if os.path.exists('/app/logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

class DistributedImageWorker:
    """
    Distributed worker that processes image tasks from Redis queue.
    """
    
    def __init__(self):
        # Get configuration from environment
        self.worker_id = os.getenv('WORKER_ID', f'worker-{int(time.time())}')
        self.worker_name = os.getenv('WORKER_NAME', 'Generic Worker')
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        # Parse capabilities from environment
        capabilities_str = os.getenv('WORKER_CAPABILITIES', 'all')
        if capabilities_str == 'all':
            self.capabilities = ['resize', 'blur', 'brightness', 'sharpen', 'edges']
        else:
            self.capabilities = [cap.strip() for cap in capabilities_str.split(',')]
        
        self.worker_type = os.getenv('WORKER_TYPE', 'general')
        
        # Initialize components
        self.task_queue = DistributedTaskQueue(self.redis_host, self.redis_port, redis_db=0)
        self.registry = WorkerRegistry(self.redis_host, self.redis_port, redis_db=0)
        self.filter_factory = FilterFactory()
        self.processor = ImageProcessor()
        
        # Worker state
        self.running = False
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0,
            'last_task_at': None
        }
        
        # Heartbeat manager
        self.heartbeat_manager = HeartbeatManager(self.registry, self.worker_id)
        # Store capabilities and host for re-registration
        self.heartbeat_manager.capabilities = self.capabilities
        self.heartbeat_manager.host = os.getenv('HOSTNAME', 'container')
        
        logger.info(f"🚀 Initialized worker {self.worker_id} ({self.worker_name})")
        logger.info(f"📋 Capabilities: {self.capabilities}")
        logger.info(f"🎯 Worker type: {self.worker_type}")
    
    def start(self):
        """Start the worker."""
        try:
            # Test Redis connection
            self.task_queue.redis_client.ping()
            self.registry.redis_client.ping()
            logger.info("✅ Redis connection successful")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            return
        
        # Register worker
        logger.info(f"🔄 Attempting to register worker {self.worker_id}")
        success = self.registry.register_worker(
            self.worker_id,
            self.capabilities,
            host=os.getenv('HOSTNAME', 'container')
        )
        
        if not success:
            logger.error("❌ Failed to register worker")
            return
        
        logger.info(f"✅ Worker {self.worker_id} registered successfully")
        
        # Verify registration worked
        active_workers = self.registry.get_active_workers()
        logger.info(f"📊 Active workers count: {len(active_workers)}")
        worker_found = any(w['id'] == self.worker_id for w in active_workers)
        if not worker_found:
            logger.error(f"❌ Worker {self.worker_id} not found in active workers list!")
            return
        logger.info(f"✅ Worker {self.worker_id} verified in active workers list")
        
        # Start heartbeat
        self.heartbeat_manager.start()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Start main processing loop
        self.running = True
        logger.info(f"🎯 Worker {self.worker_id} started, waiting for tasks...")
        
        try:
            self._process_loop()
        except KeyboardInterrupt:
            logger.info("👋 Received interrupt signal")
        finally:
            self._shutdown()
    
    def _process_loop(self):
        """Main processing loop."""
        consecutive_empty_polls = 0
        max_empty_polls = 10
        
        while self.running:
            try:
                # Get next task from queue
                task = self.task_queue.get_task(self.worker_id, timeout=5)
                
                if task is None:
                    consecutive_empty_polls += 1
                    if consecutive_empty_polls >= max_empty_polls:
                        logger.debug(f"💤 No tasks for {max_empty_polls * 5}s, worker {self.worker_id} idle")
                        consecutive_empty_polls = 0
                    continue
                
                consecutive_empty_polls = 0
                
                # Process the task
                logger.info(f"📝 Processing task {task['id']}")
                self._process_task(task)
                
                # Update heartbeat with current stats
                self.heartbeat_manager.update_stats(**self.stats)
                
            except Exception as e:
                logger.error(f"❌ Error in processing loop: {e}")
                time.sleep(1)  # Brief pause before retry
    
    def _make_serializable(self, filter_results):
        """
        Convert filter results to JSON-serializable format by removing PIL Image objects.
        """
        if isinstance(filter_results, dict):
            serializable = {}
            for key, value in filter_results.items():
                if key == 'final_image':
                    # Skip the PIL Image object
                    continue
                elif key == 'filter_results' and isinstance(value, list):
                    # Process list of filter results
                    serializable[key] = []
                    for filter_result in value:
                        if isinstance(filter_result, dict):
                            result_copy = {}
                            for k, v in filter_result.items():
                                if k == 'image':
                                    # Skip PIL Image object, keep only metadata
                                    continue
                                else:
                                    result_copy[k] = v
                            serializable[key].append(result_copy)
                        else:
                            serializable[key].append(filter_result)
                else:
                    serializable[key] = value
            return serializable
        else:
            return filter_results
    
    def _process_task(self, task: Dict):
        """Process a single image task."""
        task_id = task['id']
        task_data = task['data']
        
        start_time = time.time()
        
        try:
            # Extract task parameters
            filters = task_data.get('filters', [])
            filter_params = task_data.get('filter_params', {})
            images = task_data.get('images', [])
            
            if not images:
                # Use default images if none specified - prioritize 20MB image for demo
                images = ['static/images/Clocktower_Panorama_20080622_20mb.jpg', 'static/images/sample_4k.jpg']
            
            logger.info(f"🖼️ Processing {len(images)} images with filters: {filters}")
            
            # Check if this worker can handle all requested filters
            unsupported_filters = [f for f in filters if f not in self.capabilities and 'all' not in self.capabilities]
            if unsupported_filters:
                raise ValueError(f"Worker {self.worker_id} cannot handle filters: {unsupported_filters}")
            
            # Process images
            results = []
            for image_path in images:
                try:
                    # Simulate file I/O (reading image)
                    with open(image_path, 'rb') as f:
                        image_size = len(f.read())
                    
                    logger.debug(f"📂 Loaded image {image_path} ({image_size} bytes)")
                    
                    # Apply filter chain
                    filter_results = self.filter_factory.apply_filter_chain(
                        image_path, filters, filter_params
                    )
                    
                    # Collect results (serialize-safe, no PIL Images)
                    serializable_filter_results = self._make_serializable(filter_results)
                    
                    image_results = {
                        'image_path': image_path,
                        'filters_applied': filters,
                        'filter_results': serializable_filter_results,
                        'worker_id': self.worker_id,
                        'processing_time': time.time() - start_time
                    }
                    
                    results.append(image_results)
                    logger.info(f"✅ Processed {image_path} successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process {image_path}: {e}")
                    results.append({
                        'image_path': image_path,
                        'error': str(e),
                        'worker_id': self.worker_id
                    })
            
            # Check if all images failed (any result has 'error' field)
            failed_images = [r for r in results if 'error' in r]
            successful_images = [r for r in results if 'error' not in r]
            
            processing_time = time.time() - start_time
            result_data = {
                'worker_id': self.worker_id,
                'worker_type': self.worker_type,
                'results': results,
                'total_processing_time': processing_time,
                'images_processed': len(images),
                'images_successful': len(successful_images),
                'images_failed': len(failed_images),
                'filters_applied': filters
            }
            
            # If ALL images failed, mark task as failed
            if len(failed_images) == len(images):
                error_msg = f"All {len(images)} images failed. Errors: {[r['error'] for r in failed_images]}"
                self.task_queue.fail_task(task_id, error_msg)
                
                # Update stats
                self.stats['tasks_failed'] += 1
                
                logger.error(f"❌ Task {task_id} FAILED - all images failed in {processing_time:.2f}s")
                
            else:
                # Mark task as completed (at least some images succeeded)
                self.task_queue.complete_task(task_id, result_data)
                
                # Update stats
                self.stats['tasks_completed'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['last_task_at'] = time.time()
                
                if failed_images:
                    logger.warning(f"⚠️ Task {task_id} completed with {len(failed_images)}/{len(images)} failures in {processing_time:.2f}s")
                else:
                    logger.info(f"✅ Task {task_id} completed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            # Mark task as failed
            self.task_queue.fail_task(task_id, str(e))
            
            # Update stats
            self.stats['tasks_failed'] += 1
            
            logger.error(f"❌ Task {task_id} failed: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    def _shutdown(self):
        """Graceful shutdown process."""
        logger.info(f"🛑 Shutting down worker {self.worker_id}")
        
        # Stop heartbeat
        self.heartbeat_manager.stop()
        
        # Unregister worker
        self.registry.unregister_worker(self.worker_id)
        
        # Log final stats
        logger.info(f"📊 Final stats for {self.worker_id}:")
        logger.info(f"   Tasks completed: {self.stats['tasks_completed']}")
        logger.info(f"   Tasks failed: {self.stats['tasks_failed']}")
        logger.info(f"   Total processing time: {self.stats['total_processing_time']:.2f}s")
        
        if self.stats['tasks_completed'] > 0:
            avg_time = self.stats['total_processing_time'] / self.stats['tasks_completed']
            logger.info(f"   Average task time: {avg_time:.2f}s")
        
        logger.info(f"👋 Worker {self.worker_id} shutdown complete")


def main():
    """Main entry point for distributed worker."""
    worker = DistributedImageWorker()
    
    try:
        worker.start()
    except Exception as e:
        logger.error(f"💥 Worker failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()