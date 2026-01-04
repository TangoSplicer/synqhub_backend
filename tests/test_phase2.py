"""Phase 2 integration tests."""

import pytest

from app.services.synthesis import CircuitSynthesisService
from app.services.transpilation import TranspilationService
from app.services.quantum_backends import QuantumBackendIntegration
from app.services.monitoring import MonitoringService, LoggingService


class TestCircuitSynthesis:
    """Test circuit synthesis service."""

    def test_synthesize_circuit(self):
        """Test circuit synthesis."""
        specification = {
            "gates": ["H", "CNOT", "RZ"],
            "num_qubits": 2,
            "constraints": {},
        }

        result = CircuitSynthesisService.synthesize_from_specification(
            specification=specification,
            optimization_level=1,
        )

        assert result["success"] is True
        assert result["circuit"] is not None
        assert result["metrics"] is not None
        assert result["metrics"]["total_gates"] == 3

    def test_suggest_optimizations(self):
        """Test optimization suggestions."""
        circuit = {
            "num_qubits": 2,
            "gates": [
                {"type": "H", "target": 0},
                {"type": "CNOT", "control": 0, "target": 1},
            ],
            "depth": 2,
        }

        suggestions = CircuitSynthesisService.suggest_optimizations(
            circuit=circuit,
            target_backend="generic",
        )

        assert suggestions["suggestions"] is not None
        assert suggestions["metrics"] is not None


class TestTranspilation:
    """Test hardware transpilation service."""

    def test_transpile_to_ibmq(self):
        """Test transpilation to IBM Quantum."""
        circuit = {
            "num_qubits": 2,
            "gates": [
                {"type": "H", "target": 0},
                {"type": "CNOT", "control": 0, "target": 1},
            ],
        }

        result = TranspilationService.transpile_circuit(
            circuit=circuit,
            target_backend="ibmq",
            optimization_level=2,
        )

        assert result["success"] is True
        assert result["circuit"] is not None
        assert result["code"] is not None
        assert result["metrics"] is not None

    def test_transpile_to_ionq(self):
        """Test transpilation to IonQ."""
        circuit = {
            "num_qubits": 2,
            "gates": [
                {"type": "H", "target": 0},
                {"type": "CNOT", "control": 0, "target": 1},
            ],
        }

        result = TranspilationService.transpile_circuit(
            circuit=circuit,
            target_backend="ionq",
            optimization_level=2,
        )

        assert result["success"] is True
        assert result["metrics"]["backend_name"] == "IonQ"

    def test_transpile_invalid_backend(self):
        """Test transpilation with invalid backend."""
        circuit = {"num_qubits": 2, "gates": []}

        result = TranspilationService.transpile_circuit(
            circuit=circuit,
            target_backend="invalid_backend",
        )

        assert result["success"] is False
        assert "Unknown backend" in result["error"]


class TestQuantumBackends:
    """Test quantum backend integration."""

    def test_get_available_backends(self):
        """Test getting available backends."""
        result = QuantumBackendIntegration.get_available_backends()

        assert "backends" in result
        assert len(result["backends"]) > 0
        assert any(b["id"] == "ibmq" for b in result["backends"])
        assert any(b["id"] == "ionq" for b in result["backends"])

    def test_submit_job_to_simulator(self):
        """Test submitting job to simulator."""
        circuit = {
            "num_qubits": 2,
            "gates": [
                {"type": "H", "target": 0},
                {"type": "CNOT", "control": 0, "target": 1},
            ],
        }

        result = QuantumBackendIntegration.submit_job(
            backend_id="simulator",
            circuit=circuit,
            shots=1024,
        )

        assert result["success"] is True
        assert result["backend"] == "simulator"
        assert result["status"] == "COMPLETED"
        assert "results" in result

    def test_submit_job_missing_credentials(self):
        """Test submitting job without credentials."""
        circuit = {"num_qubits": 2, "gates": []}

        result = QuantumBackendIntegration.submit_job(
            backend_id="ibmq",
            circuit=circuit,
            shots=1024,
            credentials=None,
        )

        assert result["success"] is False
        assert "Credentials required" in result["error"]

    def test_get_job_status(self):
        """Test getting job status."""
        result = QuantumBackendIntegration.get_job_status(
            backend_id="simulator",
            job_id="test_job_123",
        )

        assert result["success"] is True
        assert result["status"] == "COMPLETED"

    def test_get_job_results(self):
        """Test getting job results."""
        result = QuantumBackendIntegration.get_job_results(
            backend_id="simulator",
            job_id="test_job_123",
        )

        assert result["success"] is True
        assert "results" in result


class TestMonitoring:
    """Test monitoring service."""

    def test_record_api_request(self):
        """Test recording API request."""
        MonitoringService.record_api_request(
            method="POST",
            endpoint="/api/v1/qml/vqe",
            status_code=200,
            latency=0.125,
        )
        # No assertion needed, just ensure no exception

    def test_record_job_submission(self):
        """Test recording job submission."""
        MonitoringService.record_job_submission(
            job_type="vqe",
            status="SUBMITTED",
        )
        # No assertion needed, just ensure no exception

    def test_get_health_status(self):
        """Test getting health status."""
        health = MonitoringService.get_health_status()

        assert health["status"] == "healthy"
        assert "components" in health
        assert health["components"]["database"] == "operational"

    def test_get_performance_metrics(self):
        """Test getting performance metrics."""
        metrics = MonitoringService.get_performance_metrics()

        assert "api" in metrics
        assert "jobs" in metrics
        assert "cache" in metrics
        assert "database" in metrics


class TestLogging:
    """Test logging service."""

    def test_log_event(self):
        """Test logging event."""
        LoggingService.log_event(
            event_type="job_submission",
            user_id="user_123",
            action="submit_vqe_job",
            details={"job_id": "job_456"},
        )
        # No assertion needed, just ensure no exception

    def test_log_error(self):
        """Test logging error."""
        LoggingService.log_error(
            error_type="ValueError",
            message="Invalid circuit specification",
            traceback="...",
            context={"circuit": {}},
        )
        # No assertion needed, just ensure no exception

    def test_log_audit(self):
        """Test logging audit event."""
        LoggingService.log_audit(
            user_id="user_123",
            action="register_plugin",
            resource="plugin_456",
            result="success",
        )
        # No assertion needed, just ensure no exception
