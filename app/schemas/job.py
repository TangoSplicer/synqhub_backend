"""Job request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class VQERequest(BaseModel):
    \"\"\"VQE job request.\"\"\"

    hamiltonian: str = Field(..., description=\"Hamiltonian specification\")
    ansatz_circuit: dict = Field(..., description=\"Ansatz circuit definition\")
    optimizer: str = Field(default=\"COBYLA\", description=\"Optimizer type\")
    max_iterations: int = Field(default=100, ge=1, le=1000)
    shots: int = Field(default=1024, ge=1, le=100000)


class QAOARequest(BaseModel):
    \"\"\"QAOA job request.\"\"\"

    problem_graph: dict = Field(..., description=\"Graph definition\")
    p: int = Field(default=1, ge=1, le=10, description=\"Circuit depth\")
    optimizer: str = Field(default=\"COBYLA\", description=\"Optimizer type\")
    shots: int = Field(default=1024, ge=1, le=100000)


class JobResponse(BaseModel):
    \"\"\"Job response.\"\"\"

    id: str
    user_id: str
    job_type: str
    status: str
    backend: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    results: dict | None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    \"\"\"Job list response.\"\"\"

    jobs: list[JobResponse]
    total_count: int
    has_more: bool
