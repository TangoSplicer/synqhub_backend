"""QML (Quantum Machine Learning) router."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.models import Job
from app.schemas import JobResponse, JobListResponse, VQERequest, QAOARequest
from app.security import verify_token
from app.tasks import execute_vqe_job, execute_qaoa_job

router = APIRouter(prefix=\"/qml\", tags=[\"quantum-machine-learning\"])


@router.post(\"/vqe\", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_vqe_job(
    request: VQERequest,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    \"\"\"Submit VQE (Variational Quantum Eigensolver) job.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    # Create job record
    job = Job(
        id=str(uuid4()),
        user_id=token.user_id,
        job_type=\"vqe\",
        status=\"SUBMITTED\",
        parameters={
            \"hamiltonian\": request.hamiltonian,
            \"ansatz_circuit\": request.ansatz_circuit,
            \"optimizer\": request.optimizer,
            \"max_iterations\": request.max_iterations,
            \"shots\": request.shots,
        },
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Submit async task
    execute_vqe_job.delay(
        job_id=job.id,
        hamiltonian=request.hamiltonian,
        ansatz_circuit=request.ansatz_circuit,
        optimizer=request.optimizer,
        max_iterations=request.max_iterations,
        shots=request.shots,
    )
    
    return JobResponse.from_orm(job)


@router.post(\"/qaoa\", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_qaoa_job(
    request: QAOARequest,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    \"\"\"Submit QAOA (Quantum Approximate Optimization Algorithm) job.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    # Create job record
    job = Job(
        id=str(uuid4()),
        user_id=token.user_id,
        job_type=\"qaoa\",
        status=\"SUBMITTED\",
        parameters={
            \"problem_graph\": request.problem_graph,
            \"p\": request.p,
            \"optimizer\": request.optimizer,
            \"shots\": request.shots,
        },
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Submit async task
    execute_qaoa_job.delay(
        job_id=job.id,
        problem_graph=request.problem_graph,
        p=request.p,
        optimizer=request.optimizer,
        shots=request.shots,
    )
    
    return JobResponse.from_orm(job)


@router.get(\"/jobs/{job_id}\", response_model=JobResponse)
async def get_job(
    job_id: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    \"\"\"Get QML job status and results.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=\"Job not found\",
        )
    
    # Verify ownership
    if job.user_id != token.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=\"Unauthorized access to job\",
        )
    
    return JobResponse.from_orm(job)


@router.get(\"/jobs\", response_model=JobListResponse)
async def list_jobs(
    limit: int = 10,
    offset: int = 0,
    status: str | None = None,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    \"\"\"List user's QML jobs.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    # Build query
    query = select(Job).where(Job.user_id == token.user_id)
    
    if status:
        query = query.where(Job.status == status.upper())
    
    # Get total count
    count_result = await db.execute(select(Job).where(Job.user_id == token.user_id))
    total_count = len(count_result.all())
    
    # Get paginated results
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(
        jobs=[JobResponse.from_orm(job) for job in jobs],
        total_count=total_count,
        has_more=(offset + limit) < total_count,
    )
