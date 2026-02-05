"""
Phase 9 Test Suite - Classical Language Enhancements

Comprehensive tests for standard library, LSP, and debugger functionality.
"""

import pytest
from app.stdlib import math, strings, collections, io, performance
from app.lsp.server import SynQLSPServer
from app.debugger.debugger import SynQDebugger


# ============================================================================
# Math Module Tests
# ============================================================================

class TestMathModule:
    """Test math module."""
    
    def test_basic_operations(self):
        """Test basic math operations."""
        assert math.add(2, 3) == 5
        assert math.subtract(5, 3) == 2
        assert math.multiply(4, 5) == 20
        assert math.divide(10, 2) == 5
    
    def test_trigonometry(self):
        """Test trigonometric functions."""
        assert abs(math.sin(0) - 0) < 1e-10
        assert abs(math.cos(0) - 1) < 1e-10
        assert abs(math.tan(0) - 0) < 1e-10
    
    def test_logarithms(self):
        """Test logarithmic functions."""
        assert abs(math.log(1) - 0) < 1e-10
        assert abs(math.log10(10) - 1) < 1e-10
        assert abs(math.log2(2) - 1) < 1e-10
    
    def test_statistics(self):
        """Test statistical functions."""
        data = [1, 2, 3, 4, 5]
        assert math.mean(data) == 3
        assert math.median(data) == 3
        assert math.sum(data) == 15
        assert math.product(data) == 120


# ============================================================================
# Strings Module Tests
# ============================================================================

class TestStringsModule:
    """Test strings module."""
    
    def test_basic_operations(self):
        """Test basic string operations."""
        assert strings.length("hello") == 5
        assert strings.concat("hello", " ", "world") == "hello world"
        assert strings.uppercase("hello") == "HELLO"
        assert strings.lowercase("HELLO") == "hello"
    
    def test_search_operations(self):
        """Test string search operations."""
        assert strings.contains("hello world", "world")
        assert strings.starts_with("hello", "he")
        assert strings.ends_with("hello", "lo")
        assert strings.index_of("hello", "l") == 2
    
    def test_formatting(self):
        """Test string formatting."""
        assert strings.format("Hello {}", "World") == "Hello World"
        assert strings.pad_left("5", 3, "0") == "005"
        assert strings.pad_right("5", 3, "0") == "500"
    
    def test_encoding(self):
        """Test string encoding/decoding."""
        encoded = strings.encode_base64("hello")
        assert strings.decode_base64(encoded) == "hello"


# ============================================================================
# Collections Module Tests
# ============================================================================

class TestCollectionsModule:
    """Test collections module."""
    
    def test_vector(self):
        """Test vector operations."""
        v = collections.Vector()
        v.push(1)
        v.push(2)
        v.push(3)
        assert v.len() == 3
        assert v.get(0) == 1
        assert v.pop() == 3
    
    def test_hashmap(self):
        """Test hashmap operations."""
        m = collections.HashMap()
        m.insert("key1", "value1")
        m.insert("key2", "value2")
        assert m.get("key1") == "value1"
        assert m.len() == 2
        assert m.contains("key1")
    
    def test_hashset(self):
        """Test hashset operations."""
        s = collections.HashSet()
        s.insert(1)
        s.insert(2)
        s.insert(3)
        assert s.len() == 3
        assert s.contains(2)
        assert not s.contains(4)
    
    def test_queue(self):
        """Test queue operations."""
        q = collections.Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        assert q.dequeue() == 1
        assert q.dequeue() == 2
    
    def test_stack(self):
        """Test stack operations."""
        s = collections.Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        assert s.pop() == 3
        assert s.pop() == 2
    
    def test_priority_queue(self):
        """Test priority queue operations."""
        pq = collections.PriorityQueue()
        pq.push("high", 1)
        pq.push("low", 3)
        pq.push("medium", 2)
        assert pq.pop() == "high"
        assert pq.pop() == "medium"


# ============================================================================
# I/O Module Tests
# ============================================================================

class TestIOModule:
    """Test I/O module."""
    
    def test_path_operations(self):
        """Test path operations."""
        path = io.path_join("/home", "user", "file.txt")
        assert io.path_basename(path) == "file.txt"
        assert io.path_dirname(path) == "/home/user"
        assert io.path_extension(path) == ".txt"
    
    def test_json_operations(self):
        """Test JSON operations."""
        obj = {"name": "test", "value": 42}
        json_str = io.json_stringify(obj)
        parsed = io.json_parse(json_str)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42


# ============================================================================
# Performance Module Tests
# ============================================================================

class TestPerformanceModule:
    """Test performance module."""
    
    def test_simd_vectors(self):
        """Test SIMD vector operations."""
        v1 = performance.Vec4f(1, 2, 3, 4)
        v2 = performance.Vec4f(5, 6, 7, 8)
        v3 = v1.add(v2)
        assert v3.data[0] == 6
        assert v3.data[3] == 12
    
    def test_simd_operations(self):
        """Test SIMD operations."""
        a = [1.0, 2.0, 3.0, 4.0]
        b = [5.0, 6.0, 7.0, 8.0]
        result = performance.simd_vector_add(a, b)
        assert result[0] == 6.0
        assert result[3] == 12.0
    
    def test_thread_pool(self):
        """Test thread pool."""
        results = []
        
        def task(x):
            results.append(x * 2)
        
        with performance.ThreadPool(2) as pool:
            for i in range(4):
                pool.execute(lambda x=i: task(x))
            pool.wait()
        
        assert len(results) == 4
    
    def test_parallel_map(self):
        """Test parallel map."""
        data = [1, 2, 3, 4, 5]
        result = performance.parallel_map(data, lambda x: x * 2, num_threads=2)
        assert result == [2, 4, 6, 8, 10]


# ============================================================================
# LSP Server Tests
# ============================================================================

class TestLSPServer:
    """Test LSP server."""
    
    def test_document_management(self):
        """Test document management."""
        server = SynQLSPServer()
        code = "fn hello() { print('hello') }"
        server.open_document("test.synq", code)
        assert "test.synq" in server.documents
    
    def test_completions(self):
        """Test code completions."""
        server = SynQLSPServer()
        server.open_document("test.synq", "fn test() { }")
        completions = server.get_completions("test.synq", 0, 0)
        assert len(completions) > 0
        labels = [c.label for c in completions]
        assert "fn" in labels
    
    def test_diagnostics(self):
        """Test diagnostics."""
        server = SynQLSPServer()
        code = 'let x = "unclosed'
        server.open_document("test.synq", code)
        diagnostics = server.get_diagnostics("test.synq")
        assert len(diagnostics) > 0


# ============================================================================
# Debugger Tests
# ============================================================================

class TestDebugger:
    """Test debugger."""
    
    def test_breakpoint_management(self):
        """Test breakpoint management."""
        debugger = SynQDebugger()
        bp = debugger.set_breakpoint("test.synq", 10)
        assert bp.id == 1
        assert bp.file == "test.synq"
        assert bp.line == 10
        
        bps = debugger.get_breakpoints()
        assert len(bps) == 1
    
    def test_variable_management(self):
        """Test variable management."""
        debugger = SynQDebugger()
        debugger.set_variable("x", 42)
        var = debugger.get_variable("x")
        assert var.value == 42
        assert var.type == "int"
    
    def test_watch_expressions(self):
        """Test watch expressions."""
        debugger = SynQDebugger()
        debugger.set_variable("x", 10)
        watch_id = debugger.add_watch("x * 2")
        value = debugger.evaluate_watch(watch_id)
        assert value == 20
    
    def test_execution_control(self):
        """Test execution control."""
        debugger = SynQDebugger()
        debugger.start()
        assert debugger.state.value == "running"
        debugger.pause()
        assert debugger.state.value == "paused"
        debugger.resume()
        assert debugger.state.value == "running"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests."""
    
    def test_stdlib_integration(self):
        """Test standard library integration."""
        # Use multiple stdlib modules together
        text = "hello world"
        upper = strings.uppercase(text)
        length = strings.length(upper)
        assert length == 11
    
    def test_collections_with_strings(self):
        """Test collections with strings."""
        v = collections.Vector()
        v.push("hello")
        v.push("world")
        assert v.len() == 2
        assert strings.uppercase(v.get(0)) == "HELLO"
    
    def test_performance_with_math(self):
        """Test performance with math."""
        data = [1.0, 2.0, 3.0, 4.0]
        result = performance.parallel_map(data, math.square, num_threads=2)
        assert result == [1.0, 4.0, 9.0, 16.0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
