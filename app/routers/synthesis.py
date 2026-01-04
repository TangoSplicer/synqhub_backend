"""Circuit Synthesis router."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.models import Job
from app.schemas import JobResponse
from app.security import verify_token
from app.services.synthesis import CircuitSynthesisService
from app.services.transpilation import TranspilationService

router = APIRouter(prefix=\"/synthesis\", tags=[\"circuit-synthesis\"])


class SynthesisRequest:
    \"\"\"Synthesis request schema.\"\"\"
    def __init__(self, specification: dict, optimization_level: int = 1):
        self.specification = specification
        self.optimization_level = optimization_level


@router.post(\"/synthesize\", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def synthesize_circuit(
    specification: dict,
    optimization_level: int = 1,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    \"\"\"Synthesize quantum circuit from high-level specification.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    # Execute synthesis synchronously (for now)
    result = CircuitSynthesisService.synthesize_from_specification(
        specification=specification,
        optimization_level=optimization_level,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get(\"error\", \"Synthesis failed\"),
        )
    
    # Create job record
    job = Job(
        id=str(uuid4()),
        user_id=token.user_id,
        job_type=\"synthesis\",
        status=\"COMPLETED\",
        circuit_data=result.get(\"circuit\"),
        results=result.get(\"metrics\"),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return JobResponse.from_orm(job)


@router.post(\"/suggest-optimizations\")
async def suggest_optimizations(
    circuit: dict,
    target_backend: str = \"generic\",
    token: str = Depends(verify_token),
) -> dict:
    \"\"\"Get optimization suggestions for a circuit.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    suggestions = CircuitSynthesisService.suggest_optimizations(
        circuit=circuit,
        target_backend=target_backend,
    )
    
    return suggestions


@router.post(\"/transpile\")
async def transpile_circuit(
    circuit: dict,
    target_backend: str,
    optimization_level: int = 2,
    token: str = Depends(verify_token),
) -> dict:
    \"\"\"Transpile circuit to target backend format.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    result = TranspilationService.transpile_circuit(
        circuit=circuit,
        target_backend=target_backend,
        optimization_level=optimization_level,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get(\"error\", \"Transpilation failed\"),
        )
    
    return {
        \"circuit\": result.get(\"circuit\"),
        \"code\": result.get(\"code\"),
        \"metrics\": result.get(\"metrics\"),
        \"target_backend\": result.get(\"target_backend\"),
    }
