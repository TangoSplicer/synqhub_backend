"""Machine learning prediction models for Phase 6 intelligence."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class MLModel(Base):
    """Represents a machine learning model for predictions."""
    
    __tablename__ = "ml_models"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)  # "circuit_optimization", "resource_estimation", etc.
    
    # Model metadata
    description = Column(Text, nullable=True)
    framework = Column(String(50), nullable=False)  # "tensorflow", "pytorch", "sklearn"
    input_schema = Column(JSON, nullable=False)  # Expected input format
    output_schema = Column(JSON, nullable=False)  # Expected output format
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Model status
    is_active = Column(Boolean, default=False, nullable=False)
    is_production = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Training info
    training_data_size = Column(Integer, nullable=True)
    training_time_seconds = Column(Float, nullable=True)
    last_trained = Column(DateTime, nullable=True)
    
    # Relationships
    predictions = relationship("MLPrediction", back_populates="model", cascade="all, delete-orphan")


class MLPrediction(Base):
    """Represents a single ML prediction result."""
    
    __tablename__ = "ml_predictions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    circuit_id = Column(PG_UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=True)
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Prediction details
    prediction_type = Column(String(100), nullable=False)  # "optimization", "resource", "error", "pattern"
    input_data = Column(JSON, nullable=False)
    predicted_output = Column(JSON, nullable=False)
    
    # Confidence and accuracy
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    actual_output = Column(JSON, nullable=True)  # For validation after execution
    prediction_error = Column(Float, nullable=True)  # Difference between predicted and actual
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_time_ms = Column(Float, nullable=True)
    
    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(Text, nullable=True)
    was_helpful = Column(Boolean, nullable=True)
    
    # Relationships
    circuit = relationship("Circuit")
    job = relationship("Job")
    model = relationship("MLModel", back_populates="predictions")
    user = relationship("User")


class CircuitOptimization(Base):
    """Represents circuit optimization suggestions from ML."""
    
    __tablename__ = "circuit_optimizations"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    prediction_id = Column(PG_UUID(as_uuid=True), ForeignKey("ml_predictions.id"), nullable=False)
    circuit_id = Column(PG_UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=False)
    
    # Original circuit metrics
    original_gate_count = Column(Integer, nullable=False)
    original_depth = Column(Integer, nullable=False)
    original_two_qubit_gates = Column(Integer, nullable=False)
    
    # Optimized circuit metrics
    optimized_gate_count = Column(Integer, nullable=False)
    optimized_depth = Column(Integer, nullable=False)
    optimized_two_qubit_gates = Column(Integer, nullable=False)
    
    # Optimization details
    optimization_technique = Column(String(255), nullable=False)
    optimization_steps = Column(JSON, nullable=False)  # List of transformations applied
    estimated_improvement = Column(Float, nullable=False)  # Percentage improvement
    
    # Optimized circuit
    optimized_circuit = Column(JSON, nullable=False)
    
    # Status
    applied = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ResourceEstimate(Base):
    """Represents resource requirement estimates from ML."""
    
    __tablename__ = "resource_estimates"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    prediction_id = Column(PG_UUID(as_uuid=True), ForeignKey("ml_predictions.id"), nullable=False)
    circuit_id = Column(PG_UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=False)
    
    # Qubit requirements
    qubits_required = Column(Integer, nullable=False)
    classical_bits_required = Column(Integer, nullable=False)
    
    # Gate requirements
    single_qubit_gates = Column(Integer, nullable=False)
    two_qubit_gates = Column(Integer, nullable=False)
    measurement_gates = Column(Integer, nullable=False)
    
    # Circuit characteristics
    circuit_depth = Column(Integer, nullable=False)
    circuit_width = Column(Integer, nullable=False)
    estimated_execution_time_ms = Column(Float, nullable=False)
    
    # Hardware compatibility
    compatible_backends = Column(JSON, nullable=False)  # List of compatible quantum backends
    recommended_backend = Column(String(100), nullable=True)
    
    # Confidence
    confidence = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PatternAnalysis(Base):
    """Represents pattern analysis results from ML."""
    
    __tablename__ = "pattern_analyses"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    prediction_id = Column(PG_UUID(as_uuid=True), ForeignKey("ml_predictions.id"), nullable=False)
    circuit_id = Column(PG_UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=False)
    
    # Pattern detection
    detected_patterns = Column(JSON, nullable=False)  # List of identified patterns
    pattern_confidence = Column(Float, nullable=False)
    
    # Algorithm classification
    algorithm_type = Column(String(100), nullable=True)  # e.g., "VQE", "QAOA", "Grover"
    algorithm_confidence = Column(Float, nullable=True)
    
    # Recommendations
    recommended_optimizations = Column(JSON, nullable=False)  # List of optimization suggestions
    alternative_implementations = Column(JSON, nullable=True)  # Alternative ways to implement
    
    # Similarity analysis
    similar_circuits = Column(JSON, nullable=True)  # IDs of similar circuits in database
    similarity_scores = Column(JSON, nullable=True)  # Similarity scores for each
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
