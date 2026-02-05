"""
ML Training Router for model training and inference endpoints.

Provides endpoints for creating models, training jobs, and predictions.
"""

import logging
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from app.ml.training_pipeline import (
    training_pipeline,
    ModelType,
    CircuitOptimizationTrainer,
    ResourceEstimationTrainer,
    PatternRecognitionTrainer,
    TrainingStatus
)
from app.ml.inference_engine import inference_engine
from app.security.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ml", tags=["ml-training"])


@router.post("/models")
async def create_model(
    name: str,
    model_type: str,
    version: str = "1.0.0",
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Create a new ML model.
    
    Model types: circuit_optimization, resource_estimation, pattern_recognition
    """
    try:
        # Validate model type
        try:
            mt = ModelType(model_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model type. Must be one of: {', '.join([t.value for t in ModelType])}"
            )
        
        model = await training_pipeline.create_model(name, mt, version)
        
        return JSONResponse({
            "model_id": model.model_id,
            "name": model.name,
            "model_type": model.model_type.value,
            "version": model.version,
            "status": model.status,
            "created_at": model.created_at.isoformat()
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating model: {e}")
        raise HTTPException(status_code=500, detail="Failed to create model")


@router.get("/models")
async def list_models(
    model_type: Optional[str] = None,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    List all ML models, optionally filtered by type.
    """
    try:
        mt = None
        if model_type:
            try:
                mt = ModelType(model_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid model type")
        
        models = await training_pipeline.list_models(mt)
        
        return JSONResponse({
            "models": [m.to_dict() for m in models],
            "total": len(models)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail="Failed to list models")


@router.get("/models/{model_id}")
async def get_model(
    model_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get details of a specific model.
    """
    try:
        model = await training_pipeline.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(model.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model")


@router.post("/training-jobs")
async def create_training_job(
    model_id: str,
    training_data_size: int,
    epochs: int = 10,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Create and start a training job for a model.
    """
    try:
        model = await training_pipeline.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        job = await training_pipeline.create_training_job(
            model_id,
            training_data_size,
            epochs,
            batch_size,
            learning_rate
        )
        
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create training job")
        
        # Start training in background
        await training_pipeline.start_training(job.job_id)
        
        if background_tasks:
            background_tasks.add_task(
                _run_training,
                job.job_id,
                model.model_type
            )
        
        return JSONResponse({
            "job_id": job.job_id,
            "model_id": job.model_id,
            "status": job.status.value,
            "created_at": job.created_at.isoformat()
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating training job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create training job")


@router.get("/training-jobs/{job_id}")
async def get_training_job(
    job_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get status of a training job.
    """
    try:
        job = await training_pipeline.get_training_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        return JSONResponse(job.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training job: {e}")
        raise HTTPException(status_code=500, detail="Failed to get training job")


@router.post("/models/{model_id}/deploy")
async def deploy_model(
    model_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Deploy a trained model for inference.
    """
    try:
        model = await training_pipeline.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        success = await training_pipeline.deploy_model(model_id)
        if not success:
            raise HTTPException(status_code=400, detail="Model is not ready for deployment")
        
        return JSONResponse({
            "model_id": model_id,
            "status": "deployed",
            "deployed_at": model.deployed_at.isoformat()
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        raise HTTPException(status_code=500, detail="Failed to deploy model")


@router.post("/predict/circuit-optimization")
async def predict_circuit_optimization(
    circuit_data: dict,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Predict circuit optimization.
    
    Input: circuit_data with gate_count, qubits, etc.
    Output: Optimized circuit recommendations
    """
    try:
        result = await inference_engine.predict_circuit_optimization(circuit_data)
        if not result:
            raise HTTPException(status_code=503, detail="Prediction service unavailable")
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting circuit optimization: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict optimization")


@router.post("/predict/resource-estimation")
async def predict_resource_estimation(
    circuit_data: dict,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Predict resource requirements for a circuit.
    
    Input: circuit_data with complexity, algorithm type, etc.
    Output: Estimated resource requirements
    """
    try:
        result = await inference_engine.predict_resource_estimation(circuit_data)
        if not result:
            raise HTTPException(status_code=503, detail="Prediction service unavailable")
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict resources")


@router.post("/predict/pattern-recognition")
async def predict_pattern_recognition(
    circuit_data: dict,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Recognize patterns in a circuit.
    
    Input: circuit_data with structure and history
    Output: Identified patterns and optimization opportunities
    """
    try:
        result = await inference_engine.predict_pattern_recognition(circuit_data)
        if not result:
            raise HTTPException(status_code=503, detail="Prediction service unavailable")
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict patterns")


@router.get("/models/{model_id}/performance")
async def get_model_performance(
    model_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get performance metrics for a model.
    """
    try:
        result = await inference_engine.get_model_performance(model_id)
        if not result:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model performance")


@router.get("/stats")
async def get_ml_stats(
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get overall ML system statistics.
    """
    try:
        stats = training_pipeline.get_model_stats()
        return JSONResponse(stats)
    
    except Exception as e:
        logger.error(f"Error getting ML stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ML stats")


async def _run_training(job_id: str, model_type: ModelType):
    """Background task to run training."""
    try:
        job = await training_pipeline.get_training_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Select appropriate trainer
        if model_type == ModelType.CIRCUIT_OPTIMIZATION:
            trainer = CircuitOptimizationTrainer()
        elif model_type == ModelType.RESOURCE_ESTIMATION:
            trainer = ResourceEstimationTrainer()
        elif model_type == ModelType.PATTERN_RECOGNITION:
            trainer = PatternRecognitionTrainer()
        else:
            logger.error(f"Unknown model type: {model_type}")
            return
        
        # Run training
        success, metrics = await trainer.train(job)
        
        if success:
            await training_pipeline.complete_training(job_id, metrics)
        else:
            await training_pipeline.fail_training(job_id, "Training failed")
    
    except Exception as e:
        logger.error(f"Error in training task: {e}")
        await training_pipeline.fail_training(job_id, str(e))
