"""
SynQ Standard Library - Collections Module

Provides data structures including vectors, maps, sets, queues, and heaps.
"""

from typing import TypeVar, Generic, List, Dict, Set, Optional, Tuple
from collections import deque
import heapq


T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


# ============================================================================
# Vector (Dynamic Array)
# ============================================================================

class Vector(Generic[T]):
    """Dynamic array implementation."""
    
    def __init__(self, capacity: int = 10):
        """Initialize vector with optional capacity."""
        self._data: List[T] = []
        self._capacity = capacity
    
    def push(self, value: T) -> None:
        """Add element to end."""
        self._data.append(value)
    
    def pop(self) -> Optional[T]:
        """Remove and return last element."""
        if not self._data:
            return None
        return self._data.pop()
    
    def get(self, index: int) -> Optional[T]:
        """Get element at index."""
        if 0 <= index < len(self._data):
            return self._data[index]
        return None
    
    def set(self, index: int, value: T) -> bool:
        """Set element at index."""
        if 0 <= index < len(self._data):
            self._data[index] = value
            return True
        return False
    
    def insert(self, index: int, value: T) -> bool:
        """Insert element at index."""
        if 0 <= index <= len(self._data):
            self._data.insert(index, value)
            return True
        return False
    
    def remove(self, index: int) -> Optional[T]:
        """Remove and return element at index."""
        if 0 <= index < len(self._data):
            return self._data.pop(index)
        return None
    
    def len(self) -> int:
        """Get vector length."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if vector is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Clear all elements."""
        self._data.clear()
    
    def contains(self, value: T) -> bool:
        """Check if vector contains value."""
        return value in self._data
    
    def index_of(self, value: T) -> int:
        """Find index of value (-1 if not found)."""
        try:
            return self._data.index(value)
        except ValueError:
            return -1
    
    def reverse(self) -> None:
        """Reverse vector in place."""
        self._data.reverse()
    
    def sort(self) -> None:
        """Sort vector in place."""
        self._data.sort()
    
    def to_list(self) -> List[T]:
        """Convert to Python list."""
        return self._data.copy()
    
    def __iter__(self):
        """Iterate over elements."""
        return iter(self._data)
    
    def __repr__(self) -> str:
        return f"Vector({self._data})"


# ============================================================================
# HashMap
# ============================================================================

class HashMap(Generic[K, V]):
    """Hash map implementation."""
    
    def __init__(self):
        """Initialize empty hash map."""
        self._data: Dict[K, V] = {}
    
    def insert(self, key: K, value: V) -> None:
        """Insert key-value pair."""
        self._data[key] = value
    
    def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        return self._data.get(key)
    
    def remove(self, key: K) -> Optional[V]:
        """Remove and return value by key."""
        return self._data.pop(key, None)
    
    def contains(self, key: K) -> bool:
        """Check if key exists."""
        return key in self._data
    
    def len(self) -> int:
        """Get number of entries."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if map is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Clear all entries."""
        self._data.clear()
    
    def keys(self) -> List[K]:
        """Get all keys."""
        return list(self._data.keys())
    
    def values(self) -> List[V]:
        """Get all values."""
        return list(self._data.values())
    
    def items(self) -> List[Tuple[K, V]]:
        """Get all key-value pairs."""
        return list(self._data.items())
    
    def __iter__(self):
        """Iterate over keys."""
        return iter(self._data)
    
    def __repr__(self) -> str:
        return f"HashMap({self._data})"


# ============================================================================
# HashSet
# ============================================================================

class HashSet(Generic[T]):
    """Hash set implementation."""
    
    def __init__(self):
        """Initialize empty set."""
        self._data: Set[T] = set()
    
    def insert(self, value: T) -> bool:
        """Insert value. Returns True if new."""
        before = len(self._data)
        self._data.add(value)
        return len(self._data) > before
    
    def remove(self, value: T) -> bool:
        """Remove value. Returns True if existed."""
        if value in self._data:
            self._data.remove(value)
            return True
        return False
    
    def contains(self, value: T) -> bool:
        """Check if set contains value."""
        return value in self._data
    
    def len(self) -> int:
        """Get set size."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if set is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Clear all elements."""
        self._data.clear()
    
    def union(self, other: 'HashSet[T]') -> 'HashSet[T]':
        """Return union of sets."""
        result = HashSet()
        result._data = self._data.union(other._data)
        return result
    
    def intersection(self, other: 'HashSet[T]') -> 'HashSet[T]':
        """Return intersection of sets."""
        result = HashSet()
        result._data = self._data.intersection(other._data)
        return result
    
    def difference(self, other: 'HashSet[T]') -> 'HashSet[T]':
        """Return difference of sets."""
        result = HashSet()
        result._data = self._data.difference(other._data)
        return result
    
    def to_list(self) -> List[T]:
        """Convert to list."""
        return list(self._data)
    
    def __iter__(self):
        """Iterate over elements."""
        return iter(self._data)
    
    def __repr__(self) -> str:
        return f"HashSet({self._data})"


# ============================================================================
# Queue (FIFO)
# ============================================================================

class Queue(Generic[T]):
    """First-in-first-out queue."""
    
    def __init__(self):
        """Initialize empty queue."""
        self._data: deque = deque()
    
    def enqueue(self, value: T) -> None:
        """Add element to back."""
        self._data.append(value)
    
    def dequeue(self) -> Optional[T]:
        """Remove and return element from front."""
        if not self._data:
            return None
        return self._data.popleft()
    
    def peek(self) -> Optional[T]:
        """Get front element without removing."""
        if not self._data:
            return None
        return self._data[0]
    
    def len(self) -> int:
        """Get queue size."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Clear all elements."""
        self._data.clear()
    
    def __iter__(self):
        """Iterate over elements."""
        return iter(self._data)
    
    def __repr__(self) -> str:
        return f"Queue({list(self._data)})"


# ============================================================================
# Stack (LIFO)
# ============================================================================

class Stack(Generic[T]):
    """Last-in-first-out stack."""
    
    def __init__(self):
        """Initialize empty stack."""
        self._data: List[T] = []
    
    def push(self, value: T) -> None:
        """Add element to top."""
        self._data.append(value)
    
    def pop(self) -> Optional[T]:
        """Remove and return element from top."""
        if not self._data:
            return None
        return self._data.pop()
    
    def peek(self) -> Optional[T]:
        """Get top element without removing."""
        if not self._data:
            return None
        return self._data[-1]
    
    def len(self) -> int:
        """Get stack size."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Clear all elements."""
        self._data.clear()
    
    def __iter__(self):
        """Iterate over elements."""
        return iter(reversed(self._data))
    
    def __repr__(self) -> str:
        return f"Stack({self._data})"


# ============================================================================
# Priority Queue (Min-Heap)
# ============================================================================

class PriorityQueue(Generic[T]):
    """Priority queue (min-heap) implementation."""
    
    def __init__(self):
        """Initialize empty priority queue."""
        self._data: List[Tuple[float, T]] = []
        self._counter = 0
    
    def push(self, value: T, priority: float = 0) -> None:
        """Add element with priority."""
        heapq.heappush(self._data, (priority, self._counter, value))
        self._counter += 1
    
    def pop(self) -> Optional[T]:
        """Remove and return highest priority element."""
        if not self._data:
            return None
        _, _, value = heapq.heappop(self._data)
        return value
    
    def peek(self) -> Optional[T]:
        """Get highest priority element without removing."""
        if not self._data:
            return None
        return self._data[0][2]
    
    def len(self) -> int:
        """Get queue size."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Clear all elements."""
        self._data.clear()
        self._counter = 0
    
    def __repr__(self) -> str:
        values = [v for _, _, v in self._data]
        return f"PriorityQueue({values})"


# ============================================================================
# Linked List
# ============================================================================

class LinkedListNode(Generic[T]):
    """Node in linked list."""
    
    def __init__(self, value: T):
        self.value = value
        self.next: Optional['LinkedListNode[T]'] = None


class LinkedList(Generic[T]):
    """Singly linked list implementation."""
    
    def __init__(self):
        """Initialize empty linked list."""
        self._head: Optional[LinkedListNode[T]] = None
        self._size = 0
    
    def push_front(self, value: T) -> None:
        """Add element to front."""
        node = LinkedListNode(value)
        node.next = self._head
        self._head = node
        self._size += 1
    
    def push_back(self, value: T) -> None:
        """Add element to back."""
        node = LinkedListNode(value)
        if not self._head:
            self._head = node
        else:
            current = self._head
            while current.next:
                current = current.next
            current.next = node
        self._size += 1
    
    def pop_front(self) -> Optional[T]:
        """Remove and return element from front."""
        if not self._head:
            return None
        value = self._head.value
        self._head = self._head.next
        self._size -= 1
        return value
    
    def get(self, index: int) -> Optional[T]:
        """Get element at index."""
        if index < 0 or index >= self._size:
            return None
        current = self._head
        for _ in range(index):
            current = current.next
        return current.value if current else None
    
    def len(self) -> int:
        """Get list size."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if list is empty."""
        return self._size == 0
    
    def clear(self) -> None:
        """Clear all elements."""
        self._head = None
        self._size = 0
    
    def to_list(self) -> List[T]:
        """Convert to Python list."""
        result = []
        current = self._head
        while current:
            result.append(current.value)
            current = current.next
        return result
    
    def __iter__(self):
        """Iterate over elements."""
        current = self._head
        while current:
            yield current.value
            current = current.next
    
    def __repr__(self) -> str:
        return f"LinkedList({self.to_list()})"


__all__ = [
    'Vector', 'HashMap', 'HashSet', 'Queue', 'Stack',
    'PriorityQueue', 'LinkedList', 'LinkedListNode'
]
