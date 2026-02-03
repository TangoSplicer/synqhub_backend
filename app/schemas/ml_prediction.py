"""Pydantic schemas for ML prediction endpoints."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field


class MLModelBase(BaseModel):
    """Base schema for ML models."""
    
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    model_type: str = Field(..., min_length=1, max_length=100)
    framework: str = Field(..., pattern=\"^(tensorflow|pytorch|sklearn)$\")
    description: Optional[str] = None


class MLModelCreate(MLModelBase):
    """Schema for creating ML models."""
    
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class MLModelUpdate(BaseModel):
    """Schema for updating ML models."""
    
    is_active: Optional[bool] = None
    is_production: Optional[bool] = None
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    precision: Optional[float] = Field(None, ge=0.0, le=1.0)
    recall: Optional[float] = Field(None, ge=0.0, le=1.0)
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class MLModelResponse(MLModelBase):
    \"\"\"Schema for ML model responses.\"\"\"
    
    id: UUID
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    is_active: bool
    is_production: bool
    created_at: datetime
    updated_at: datetime
    training_data_size: Optional[int] = None
    training_time_seconds: Optional[float] = None
    last_trained: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MLPredictionBase(BaseModel):
    \"\"\"Base schema for ML predictions.\"\"\"
    
    prediction_type: str = Field(..., min_length=1, max_length=100)
    input_data: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)


class MLPredictionCreate(MLPredictionBase):
    \"\"\"Schema for creating ML predictions.\"\"\"
    
    circuit_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    model_id: UUID


class MLPredictionResponse(MLPredictionBase):
    \"\"\"Schema for ML prediction responses.\"\"\"
    
    id: UUID
    circuit_id: Optional[UUID]
    job_id: Optional[UUID]
    model_id: UUID
    user_id: UUID
    predicted_output: Dict[str, Any]
    actual_output: Optional[Dict[str, Any]] = None
    prediction_error: Optional[float] = None
    created_at: datetime
    execution_time_ms: Optional[float] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None
    was_helpful: Optional[bool] = None
    
    class Config:
        from_attributes = True


class CircuitOptimizationBase(BaseModel):
    \"\"\"Base schema for circuit optimizations.\"\"\"
    
    original_gate_count: int = Field(..., ge=0)
    original_depth: int = Field(..., ge=0)
    original_two_qubit_gates: int = Field(..., ge=0)
    optimized_gate_count: int = Field(..., ge=0)
    optimized_depth: int = Field(..., ge=0)
    optimized_two_qubit_gates: int = Field(..., ge=0)
    optimization_technique: str = Field(..., min_length=1, max_length=255)
    estimated_improvement: float = Field(..., ge=0.0, le=100.0)


class CircuitOptimizationCreate(CircuitOptimizationBase):
    \"\"\"Schema for creating circuit optimizations.\"\"\"
    
    prediction_id: UUID
    circuit_id: UUID
    optimization_steps: List[Dict[str, Any]]
    optimized_circuit: Dict[str, Any]


class CircuitOptimizationResponse(CircuitOptimizationBase):
    \"\"\"Schema for circuit optimization responses.\"\"\"
    
    id: UUID
    prediction_id: UUID
    circuit_id: UUID
    optimization_steps: List[Dict[str, Any]]
    optimized_circuit: Dict[str, Any]
    applied: bool
    applied_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResourceEstimateBase(BaseModel):
    \"\"\"Base schema for resource estimates.\"\"\"
    
    qubits_required: int = Field(..., ge=1)
    classical_bits_required: int = Field(..., ge=0)
    single_qubit_gates: int = Field(..., ge=0)
    two_qubit_gates: int = Field(..., ge=0)
    measurement_gates: int = Field(..., ge=0)
    circuit_depth: int = Field(..., ge=0)
    circuit_width: int = Field(..., ge=0)
    estimated_execution_time_ms: float = Field(..., ge=0.0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class ResourceEstimateCreate(ResourceEstimateBase):
    \"\"\"Schema for creating resource estimates.\"\"\"
    
    prediction_id: UUID
    circuit_id: UUID
    compatible_backends: List[str]
    recommended_backend: Optional[str] = None


class ResourceEstimateResponse(ResourceEstimateBase):
    \"\"\"Schema for resource estimate responses.\"\"\"
    
    id: UUID
    prediction_id: UUID
    circuit_id: UUID
    compatible_backends: List[str]
    recommended_backend: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PatternAnalysisBase(BaseModel):
    \"\"\"Base schema for pattern analysis.\"\"\"
    
    detected_patterns: List[str]
    pattern_confidence: float = Field(..., ge=0.0, le=1.0)
    algorithm_type: Optional[str] = None
    algorithm_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    recommended_optimizations: List[str]


class PatternAnalysisCreate(PatternAnalysisBase):
    \"\"\"Schema for creating pattern analysis.\"\"\"
    
    prediction_id: UUID
    circuit_id: UUID
    alternative_implementations: Optional[List[Dict[str, Any]]] = None
    similar_circuits: Optional[List[UUID]] = None
    similarity_scores: Optional[List[float]] = None


class PatternAnalysisResponse(PatternAnalysisBase):
    \"\"\"Schema for pattern analysis responses.\"\"\"
    
    id: UUID
    prediction_id: UUID
    circuit_id: UUID
    alternative_implementations: Optional[List[Dict[str, Any]]] = None
    similar_circuits: Optional[List[UUID]] = None
    similarity_scores: Optional[List[float]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionFeedback(BaseModel):
    \"\"\"Schema for prediction feedback.\"\"\"
    
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
    was_helpful: bool


class OptimizationApply(BaseModel):
    \"\"\"Schema for applying optimizations.\"\"\"
    
    optimization_id: UUID
