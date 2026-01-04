"""Celery tasks for async job processing."""

import json
from datetime import datetime

from celery import Celery
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import Job
from app.services.qml import VQEService, QAOAService, QNNService

settings = get_settings()

# Initialize Celery
celery_app = Celery(
    "synq",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Database setup for tasks
engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session():
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        return session


@celery_app.task(name="execute_vqe_job")
def execute_vqe_job(job_id: str, hamiltonian: str, ansatz_circuit: dict, optimizer: str, max_iterations: int, shots: int):
    """Execute VQE job asynchronously."""
    import asyncio
    
    async def _execute():
        session = await get_async_session()
        try:
            # Update job status to RUNNING
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="RUNNING",
                    started_at=datetime.utcnow(),
                )
            )
            await session.commit()
            
            # Execute VQE
            results = VQEService.execute_vqe(
                hamiltonian=hamiltonian,
                ansatz_circuit=ansatz_circuit,
                optimizer=optimizer,
                max_iterations=max_iterations,
                shots=shots,
            )
            
            # Update job with results
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="COMPLETED",
                    results=results,
                    completed_at=datetime.utcnow(),
                )
            )
            await session.commit()
            
        except Exception as e:
            # Update job with error
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="FAILED",
                    error_message=str(e),
                    completed_at=datetime.utcnow(),
                )
            )
            await session.commit()
        finally:
            await session.close()
    
    # Run async function
    asyncio.run(_execute())


@celery_app.task(name="execute_qaoa_job")
def execute_qaoa_job(job_id: str, problem_graph: dict, p: int, optimizer: str, shots: int):
    """Execute QAOA job asynchronously."""
    import asyncio
    
    async def _execute():
        session = await get_async_session()
        try:
            # Update job status to RUNNING
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="RUNNING",
                    started_at=datetime.utcnow(),
                )
            )
            await session.commit()
            
            # Execute QAOA
            results = QAOAService.execute_qaoa(
                problem_graph=problem_graph,
                p=p,
                optimizer=optimizer,
                shots=shots,
            )
            
            # Update job with results
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="COMPLETED",
                    results=results,
                    completed_at=datetime.utcnow(),
                )
            )
            await session.commit()
            
        except Exception as e:
            # Update job with error
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="FAILED",
                    error_message=str(e),
                    completed_at=datetime.utcnow(),
                )
            )
            await session.commit()
        finally:
            await session.close()
    
    # Run async function
    asyncio.run(_execute())


@celery_app.task(name="execute_qnn_job")
def execute_qnn_job(job_id: str, training_data: dict, circuit_architecture: dict, learning_rate: float, epochs: int):
    """Execute QNN training job asynchronously."""
    import asyncio
    
    async def _execute():
        session = await get_async_session()
        try:
            # Update job status to RUNNING
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="RUNNING",
                    started_at=datetime.utcnow(),
                )
            )
            await session.commit()
            
            # Execute QNN training
            results = QNNService.train_qnn(
                training_data=training_data,
                circuit_architecture=circuit_architecture,
                learning_rate=learning_rate,
                epochs=epochs,
            )
            
            # Update job with results
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="COMPLETED",
                    results=results,
                    completed_at=datetime.utcnow(),
                )
            )
            await session.commit()
            
        except Exception as e:
            # Update job with error
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="FAILED",
                    error_message=str(e),
                    completed_at=datetime.utcnow(),
                )
            )
            await session.commit()
        finally:
            await session.close()
    
    # Run async function
    asyncio.run(_execute())
