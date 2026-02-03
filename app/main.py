"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import close_db, init_db
from app.routers import auth, qml, synthesis, plugins, collaboration, ml_prediction, api_gateway

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Application lifespan context manager.\"\"\"
    # Startup
    print(\"Starting SynQ Backend...\")
    await init_db()
    print(\"Database initialized\")
    yield
    # Shutdown
    print(\"Shutting down SynQ Backend...\")
    await close_db()
    print(\"Database connection closed\")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=\"Unified platform for hybrid quantum-classical-AI computing\",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Health check endpoint
@app.get(\"/health\", status_code=status.HTTP_200_OK)
async def health_check():
    \"\"\"Health check endpoint.\"\"\"
    return {
        \"status\": \"healthy\",
        \"service\": settings.app_name,
        \"version\": settings.app_version,
    }


# Root endpoint
@app.get(\"/\", status_code=status.HTTP_200_OK)
async def root():
    \"\"\"Root endpoint.\"\"\"
    return {
        \"message\": f\"Welcome to {settings.app_name}\",
        \"version\": settings.app_version,
        \"docs\": \"/docs\",
        \"redoc\": \"/redoc\",
    }


# Include routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(qml.router, prefix=settings.api_prefix)
app.include_router(synthesis.router, prefix=settings.api_prefix)
app.include_router(plugins.router, prefix=settings.api_prefix)
app.include_router(collaboration.router, prefix=settings.api_prefix)
app.include_router(ml_prediction.router, prefix=settings.api_prefix)
app.include_router(api_gateway.router, prefix=settings.api_prefix)


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    \"\"\"Handle general exceptions.\"\"\"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            \"detail\": \"Internal server error\",
            \"error\": str(exc) if settings.debug else None,
        },
    )


if __name__ == \"__main__\":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
