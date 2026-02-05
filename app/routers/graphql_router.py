"""
GraphQL Router for FastAPI integration.

Provides GraphQL endpoint for flexible queries.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.security.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/graphql", tags=["graphql"])

# Try to import GraphQL schema
try:
    from app.graphql.schema import schema as graphql_schema
    GRAPHQL_AVAILABLE = graphql_schema is not None
except ImportError:
    GRAPHQL_AVAILABLE = False
    graphql_schema = None


@router.post("/query")
async def graphql_query(
    query: str,
    variables: Dict[str, Any] = None,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Execute a GraphQL query.
    
    Requires authentication. Pass GraphQL query string and optional variables.
    """
    if not GRAPHQL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="GraphQL support not available. Install strawberry-graphql."
        )
    
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Execute GraphQL query
        result = await graphql_schema.execute(
            query,
            variable_values=variables or {}
        )
        
        response = {
            "data": result.data,
            "errors": [str(e) for e in result.errors] if result.errors else None
        }
        
        return JSONResponse(response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GraphQL query error: {e}")
        raise HTTPException(status_code=500, detail="GraphQL query failed")


@router.post("/mutation")
async def graphql_mutation(
    query: str,
    variables: Dict[str, Any] = None,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Execute a GraphQL mutation.
    
    Requires authentication. Pass GraphQL mutation string and optional variables.
    """
    if not GRAPHQL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="GraphQL support not available. Install strawberry-graphql."
        )
    
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Mutation is required")
        
        # Execute GraphQL mutation
        result = await graphql_schema.execute(
            query,
            variable_values=variables or {}
        )
        
        response = {
            "data": result.data,
            "errors": [str(e) for e in result.errors] if result.errors else None
        }
        
        return JSONResponse(response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GraphQL mutation error: {e}")
        raise HTTPException(status_code=500, detail="GraphQL mutation failed")


@router.get("/schema")
async def get_schema(
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get GraphQL schema information.
    """
    if not GRAPHQL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="GraphQL support not available."
        )
    
    try:
        schema_str = str(graphql_schema)
        
        return JSONResponse({
            "available": True,
            "schema": schema_str,
            "types": [
                "Circuit",
                "Job",
                "MLModel",
                "TrainingJob",
                "Prediction",
                "CollaborationSession",
                "Participant",
                "Comment"
            ],
            "queries": [
                "circuit",
                "circuits",
                "job",
                "jobs",
                "ml_model",
                "ml_models",
                "collaboration_session",
                "collaboration_sessions",
                "session_participants",
                "session_comments"
            ],
            "mutations": [
                "create_circuit",
                "submit_job",
                "create_ml_model",
                "start_training",
                "create_collaboration_session",
                "add_comment"
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to get schema")


@router.post("/introspect")
async def introspect(
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get GraphQL introspection data.
    """
    if not GRAPHQL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="GraphQL support not available."
        )
    
    try:
        # GraphQL introspection query
        introspection_query = """
        {
            __schema {
                types {
                    name
                    kind
                    description
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        
        result = await graphql_schema.execute(introspection_query)
        
        return JSONResponse({
            "data": result.data,
            "errors": [str(e) for e in result.errors] if result.errors else None
        })
    
    except Exception as e:
        logger.error(f"Error introspecting schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to introspect schema")
