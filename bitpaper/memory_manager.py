import gc
import weakref
import threading
from typing import Dict, Any, Optional
from collections import deque
import psutil
import os

class UltraFastMemoryManager:
    """Ultra-fast memory management with object pooling and smart GC"""
    
    def __init__(self, max_pool_size=100, gc_threshold_mb=500):
        self.max_pool_size = max_pool_size
        self.gc_threshold_mb = gc_threshold_mb
        self.object_pools = {}
        self.memory_monitor = MemoryMonitor()
        self.lock = threading.Lock()
        
        # Initialize object pools
        self._init_pools()
    
    def _init_pools(self):
        """Initialize object pools for common types"""
        self.object_pools.update({
            'bytearray': deque(maxlen=self.max_pool_size),
            'numpy_array': deque(maxlen=self.max_pool_size),
            'pil_image': deque(maxlen=self.max_pool_size),
            'bitstream': deque(maxlen=self.max_pool_size)
        })
    
    def get_object(self, obj_type: str, size: Optional[int] = None) -> Any:
        """Get object from pool or create new one"""
        with self.lock:
            pool = self.object_pools.get(obj_type)
            if pool and pool:
                return pool.popleft()
            
            # Create new object
            if obj_type == 'bytearray':
                return bytearray(size or 1024)
            elif obj_type == 'numpy_array':
                import numpy as np
                return np.zeros((size or 1000,), dtype=np.uint8)
            elif obj_type == 'pil_image':
                from PIL import Image
                return Image.new('L', (2480, 3508), 255)
            elif obj_type == 'bitstream':
                return ['0'] * (size or 1000)
            else:
                raise ValueError(f"Unknown object type: {obj_type}")
    
    def return_object(self, obj_type: str, obj: Any):
        """Return object to pool for reuse"""
        with self.lock:
            pool = self.object_pools.get(obj_type)
            if pool and len(pool) < self.max_pool_size:
                # Clear object before returning
                if obj_type == 'bytearray':
                    obj.clear()
                elif obj_type == 'numpy_array':
                    obj.fill(0)
                elif obj_type == 'pil_image':
                    obj = obj.convert('L')
                elif obj_type == 'bitstream':
                    obj.clear()
                
                pool.append(obj)
    
    def smart_gc(self, force: bool = False):
        """Smart garbage collection based on memory usage"""
        current_memory = self.memory_monitor.get_memory_usage()
        
        if force or current_memory > self.gc_threshold_mb:
            # Use different GC strategies based on memory pressure
            if current_memory > self.gc_threshold_mb * 2:
                # Aggressive GC for high memory usage
                gc.collect(2)  # Full collection
            else:
                # Light GC for moderate usage
                gc.collect(0)  # Young generation only
            
            return True
        return False
    
    def cleanup_pools(self):
        """Clean up object pools to free memory"""
        with self.lock:
            for pool in self.object_pools.values():
                pool.clear()
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get detailed memory statistics"""
        return self.memory_monitor.get_detailed_stats()

class MemoryMonitor:
    """Real-time memory monitoring"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.memory_history = deque(maxlen=100)
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.memory_history.append(memory_mb)
        return memory_mb
    
    def get_detailed_stats(self) -> Dict[str, float]:
        """Get detailed memory statistics"""
        memory_info = self.process.memory_info()
        return {
            'current_mb': memory_info.rss / 1024 / 1024,
            'peak_mb': memory_info.peak_wset / 1024 / 1024,
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'total_mb': psutil.virtual_memory().total / 1024 / 1024,
            'usage_percent': psutil.virtual_memory().percent
        }

# Global memory manager instance
memory_manager = UltraFastMemoryManager()

def optimized_memory_context():
    """Context manager for optimized memory operations"""
    class MemoryContext:
        def __enter__(self):
            # Pre-allocate common objects
            self.encoder = None
            self.decoder = None
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Clean up and return objects to pool
            if self.encoder:
                memory_manager.return_object('encoder', self.encoder)
            if self.decoder:
                memory_manager.return_object('decoder', self.decoder)
            
            # Smart GC if needed
            memory_manager.smart_gc()
    
    return MemoryContext() 