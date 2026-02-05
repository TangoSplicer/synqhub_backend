"""
SynQ Standard Library - Performance Module

Provides SIMD operations, vectorization, and parallelization support.
"""

import numpy as np
from typing import List, Callable, TypeVar, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing


T = TypeVar('T')


# ============================================================================
# SIMD Vector Types and Operations
# ============================================================================

class Vec4f:
    """4-element float32 SIMD vector."""
    
    def __init__(self, *values):
        """Create SIMD vector."""
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            self.data = np.array(values[0], dtype=np.float32)
        else:
            self.data = np.array(values, dtype=np.float32)
        if len(self.data) != 4:
            raise ValueError("Vec4f requires exactly 4 elements")
    
    def add(self, other: 'Vec4f') -> 'Vec4f':
        """Element-wise addition."""
        return Vec4f(self.data + other.data)
    
    def sub(self, other: 'Vec4f') -> 'Vec4f':
        """Element-wise subtraction."""
        return Vec4f(self.data - other.data)
    
    def mul(self, other: 'Vec4f') -> 'Vec4f':
        """Element-wise multiplication."""
        return Vec4f(self.data * other.data)
    
    def div(self, other: 'Vec4f') -> 'Vec4f':
        """Element-wise division."""
        return Vec4f(self.data / other.data)
    
    def dot(self, other: 'Vec4f') -> float:
        """Dot product."""
        return float(np.dot(self.data, other.data))
    
    def magnitude(self) -> float:
        """Vector magnitude."""
        return float(np.linalg.norm(self.data))
    
    def normalize(self) -> 'Vec4f':
        """Normalize vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vec4f(0, 0, 0, 0)
        return Vec4f(self.data / mag)
    
    def __repr__(self) -> str:
        return f"Vec4f({self.data})"


class Vec8f:
    """8-element float32 SIMD vector."""
    
    def __init__(self, *values):
        """Create SIMD vector."""
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            self.data = np.array(values[0], dtype=np.float32)
        else:
            self.data = np.array(values, dtype=np.float32)
        if len(self.data) != 8:
            raise ValueError("Vec8f requires exactly 8 elements")
    
    def add(self, other: 'Vec8f') -> 'Vec8f':
        """Element-wise addition."""
        return Vec8f(self.data + other.data)
    
    def sub(self, other: 'Vec8f') -> 'Vec8f':
        """Element-wise subtraction."""
        return Vec8f(self.data - other.data)
    
    def mul(self, other: 'Vec8f') -> 'Vec8f':
        """Element-wise multiplication."""
        return Vec8f(self.data * other.data)
    
    def div(self, other: 'Vec8f') -> 'Vec8f':
        """Element-wise division."""
        return Vec8f(self.data / other.data)
    
    def dot(self, other: 'Vec8f') -> float:
        """Dot product."""
        return float(np.dot(self.data, other.data))
    
    def __repr__(self) -> str:
        return f"Vec8f({self.data})"


class Vec4d:
    """4-element float64 SIMD vector."""
    
    def __init__(self, *values):
        """Create SIMD vector."""
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            self.data = np.array(values[0], dtype=np.float64)
        else:
            self.data = np.array(values, dtype=np.float64)
        if len(self.data) != 4:
            raise ValueError("Vec4d requires exactly 4 elements")
    
    def add(self, other: 'Vec4d') -> 'Vec4d':
        """Element-wise addition."""
        return Vec4d(self.data + other.data)
    
    def sub(self, other: 'Vec4d') -> 'Vec4d':
        """Element-wise subtraction."""
        return Vec4d(self.data - other.data)
    
    def mul(self, other: 'Vec4d') -> 'Vec4d':
        """Element-wise multiplication."""
        return Vec4d(self.data * other.data)
    
    def div(self, other: 'Vec4d') -> 'Vec4d':
        """Element-wise division."""
        return Vec4d(self.data / other.data)
    
    def dot(self, other: 'Vec4d') -> float:
        """Dot product."""
        return float(np.dot(self.data, other.data))
    
    def __repr__(self) -> str:
        return f"Vec4d({self.data})"


# ============================================================================
# Thread Pool
# ============================================================================

class ThreadPool:
    """Thread pool for parallel task execution."""
    
    def __init__(self, num_threads: int = None):
        """Create thread pool."""
        if num_threads is None:
            num_threads = multiprocessing.cpu_count()
        self.num_threads = num_threads
        self.executor = ThreadPoolExecutor(max_workers=num_threads)
        self.futures = []
    
    def execute(self, task: Callable) -> None:
        """Submit task to pool."""
        future = self.executor.submit(task)
        self.futures.append(future)
    
    def wait(self) -> None:
        """Wait for all tasks to complete."""
        for future in self.futures:
            future.result()
        self.futures.clear()
    
    def shutdown(self) -> None:
        """Shutdown thread pool."""
        self.executor.shutdown(wait=True)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


class ProcessPool:
    """Process pool for parallel task execution."""
    
    def __init__(self, num_processes: int = None):
        """Create process pool."""
        if num_processes is None:
            num_processes = multiprocessing.cpu_count()
        self.num_processes = num_processes
        self.executor = ProcessPoolExecutor(max_workers=num_processes)
        self.futures = []
    
    def execute(self, task: Callable) -> None:
        """Submit task to pool."""
        future = self.executor.submit(task)
        self.futures.append(future)
    
    def wait(self) -> None:
        """Wait for all tasks to complete."""
        for future in self.futures:
            future.result()
        self.futures.clear()
    
    def shutdown(self) -> None:
        """Shutdown process pool."""
        self.executor.shutdown(wait=True)


# ============================================================================
# Parallel Operations
# ============================================================================

def parallel_for(start: int, end: int, body: Callable[[int], None], 
                 num_threads: int = None) -> None:
    """Execute loop in parallel."""
    if num_threads is None:
        num_threads = multiprocessing.cpu_count()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(start, end):
            futures.append(executor.submit(body, i))
        for future in futures:
            future.result()


def parallel_map(data: List[T], func: Callable[[T], T], 
                 num_threads: int = None) -> List[T]:
    """Apply function to list in parallel."""
    if num_threads is None:
        num_threads = multiprocessing.cpu_count()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(func, item) for item in data]
        return [future.result() for future in futures]


def parallel_reduce(data: List[T], init: T, func: Callable[[T, T], T],
                    num_threads: int = None) -> T:
    """Reduce list in parallel."""
    if num_threads is None:
        num_threads = multiprocessing.cpu_count()
    
    if not data:
        return init
    
    # Divide data into chunks
    chunk_size = max(1, len(data) // num_threads)
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Reduce each chunk
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        def reduce_chunk(chunk):
            result = init
            for item in chunk:
                result = func(result, item)
            return result
        
        futures = [executor.submit(reduce_chunk, chunk) for chunk in chunks]
        partial_results = [future.result() for future in futures]
    
    # Reduce partial results
    result = init
    for partial in partial_results:
        result = func(result, partial)
    
    return result


# ============================================================================
# Vectorization Support
# ============================================================================

def vectorize_operation(func: Callable, data: List[float]) -> List[float]:
    """Vectorize scalar function over array."""
    return [func(x) for x in data]


def simd_vector_add(a: List[float], b: List[float]) -> List[float]:
    """Add two vectors using SIMD."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    return (a_arr + b_arr).tolist()


def simd_vector_mul(a: List[float], b: List[float]) -> List[float]:
    """Multiply two vectors using SIMD."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    return (a_arr * b_arr).tolist()


def simd_dot_product(a: List[float], b: List[float]) -> float:
    """Calculate dot product using SIMD."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    return float(np.dot(a_arr, b_arr))


def simd_matrix_mul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Multiply matrices using SIMD."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    return np.matmul(a_arr, b_arr).tolist()


# ============================================================================
# Synchronization Primitives
# ============================================================================

class Mutex:
    """Mutual exclusion lock."""
    
    def __init__(self):
        """Create mutex."""
        self._lock = threading.Lock()
    
    def lock(self) -> None:
        """Acquire lock."""
        self._lock.acquire()
    
    def unlock(self) -> None:
        """Release lock."""
        self._lock.release()
    
    def try_lock(self) -> bool:
        """Try to acquire lock."""
        return self._lock.acquire(blocking=False)
    
    def __enter__(self):
        """Context manager entry."""
        self.lock()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.unlock()


class Semaphore:
    """Semaphore for resource counting."""
    
    def __init__(self, count: int = 1):
        """Create semaphore."""
        self._semaphore = threading.Semaphore(count)
    
    def acquire(self) -> None:
        """Acquire semaphore."""
        self._semaphore.acquire()
    
    def release(self) -> None:
        """Release semaphore."""
        self._semaphore.release()
    
    def try_acquire(self) -> bool:
        """Try to acquire semaphore."""
        return self._semaphore.acquire(blocking=False)


class Barrier:
    """Barrier for thread synchronization."""
    
    def __init__(self, num_threads: int):
        """Create barrier."""
        self._barrier = threading.Barrier(num_threads)
    
    def wait(self) -> None:
        """Wait for all threads at barrier."""
        self._barrier.wait()


__all__ = [
    'Vec4f', 'Vec8f', 'Vec4d',
    'ThreadPool', 'ProcessPool',
    'parallel_for', 'parallel_map', 'parallel_reduce',
    'vectorize_operation', 'simd_vector_add', 'simd_vector_mul',
    'simd_dot_product', 'simd_matrix_mul',
    'Mutex', 'Semaphore', 'Barrier'
]
