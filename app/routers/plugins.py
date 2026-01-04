"""Plugin Registry router for SynQHub."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.security import verify_token
from app.services.plugin_registry import PluginRegistryService

router = APIRouter(prefix=\"/plugins\", tags=[\"plugin-registry\"])


@router.post(\"/register\", status_code=status.HTTP_201_CREATED)
async def register_plugin(
    name: str,
    version: str,
    category: str,
    plugin_code: str,
    description: str | None = None,
    source_url: str | None = None,
    documentation_url: str | None = None,
    dependencies: list | None = None,
    metadata: dict | None = None,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> dict:
    \"\"\"Register a new plugin in SynQHub.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    result = await PluginRegistryService.register_plugin(
        db=db,
        author_id=token.user_id,
        name=name,
        version=version,
        category=category,
        plugin_code=plugin_code,
        description=description,
        source_url=source_url,
        documentation_url=documentation_url,
        dependencies=dependencies,
        metadata=metadata,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get(\"error\", \"Plugin registration failed\"),
        )
    
    return result


@router.get(\"/search\")
async def search_plugins(
    query: str | None = None,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> dict:
    \"\"\"Search plugins in registry.\"\"\"
    result = await PluginRegistryService.search_plugins(
        db=db,
        query=query,
        category=category,
        limit=limit,
        offset=offset,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get(\"error\", \"Search failed\"),
        )
    
    return result


@router.get(\"/trending\")
async def get_trending_plugins(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> dict:
    \"\"\"Get trending plugins.\"\"\"
    result = await PluginRegistryService.get_trending_plugins(
        db=db,
        limit=limit,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get(\"error\", \"Failed to fetch trending plugins\"),
        )
    
    return result


@router.get(\"/{plugin_id}\")
async def get_plugin(
    plugin_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    \"\"\"Get plugin details.\"\"\"
    result = await PluginRegistryService.get_plugin(
        db=db,
        plugin_id=plugin_id,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get(\"error\", \"Plugin not found\"),
        )
    
    return result


@router.post(\"/{plugin_id}/review\", status_code=status.HTTP_201_CREATED)
async def submit_review(
    plugin_id: str,
    rating: int,
    review_text: str | None = None,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> dict:
    \"\"\"Submit a review for a plugin.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Authentication required\",
        )
    
    result = await PluginRegistryService.submit_review(
        db=db,
        plugin_id=plugin_id,
        reviewer_id=token.user_id,
        rating=rating,
        review_text=review_text,
    )
    
    if not result.get(\"success\"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get(\"error\", \"Review submission failed\"),
        )
    
    return result
