"""SynQHub Plugin Registry Service."""

from typing import Any, Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Plugin, PluginReview


class PluginRegistryService:
    """Manage plugin registry and discovery."""

    @staticmethod
    async def register_plugin(
        db: AsyncSession,
        author_id: str,
        name: str,
        version: str,
        category: str,
        plugin_code: str,
        description: Optional[str] = None,
        source_url: Optional[str] = None,
        documentation_url: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a new plugin in SynQHub.
        
        Args:
            db: Database session
            author_id: Plugin author ID
            name: Plugin name
            version: Plugin version
            category: Plugin category
            plugin_code: Plugin source code
            description: Plugin description
            source_url: Source code repository URL
            documentation_url: Documentation URL
            dependencies: Plugin dependencies
            metadata: Additional metadata
            
        Returns:
            Registered plugin information
        """
        try:
            # Check if plugin already exists
            result = await db.execute(
                select(Plugin).where(Plugin.name == name)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                return {
                    "error": f"Plugin '{name}' already exists",
                    "success": False,
                }
            
            # Create plugin
            plugin = Plugin(
                author_id=author_id,
                name=name,
                version=version,
                category=category,
                plugin_code=plugin_code,
                description=description,
                source_url=source_url,
                documentation_url=documentation_url,
                dependencies=dependencies or [],
                metadata=metadata or {},
            )
            
            db.add(plugin)
            await db.commit()
            await db.refresh(plugin)
            
            return {
                "plugin_id": plugin.id,
                "name": plugin.name,
                "version": plugin.version,
                "category": plugin.category,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def search_plugins(
        db: AsyncSession,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search plugins in registry.
        
        Args:
            db: Database session
            query: Search query
            category: Filter by category
            limit: Maximum results
            offset: Result offset
            
        Returns:
            Search results
        """
        try:
            # Build query
            sql_query = select(Plugin)
            
            if query:
                sql_query = sql_query.where(
                    Plugin.name.ilike(f"%{query}%") |
                    Plugin.description.ilike(f"%{query}%")
                )
            
            if category:
                sql_query = sql_query.where(Plugin.category == category)
            
            # Get total count
            count_result = await db.execute(sql_query)
            total_count = len(count_result.all())
            
            # Get paginated results
            sql_query = sql_query.order_by(Plugin.downloads.desc()).limit(limit).offset(offset)
            result = await db.execute(sql_query)
            plugins = result.scalars().all()
            
            return {
                "plugins": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "version": p.version,
                        "category": p.category,
                        "description": p.description,
                        "author_id": p.author_id,
                        "downloads": p.downloads,
                        "rating": p.rating,
                        "is_verified": p.is_verified,
                        "is_featured": p.is_featured,
                    }
                    for p in plugins
                ],
                "total_count": total_count,
                "has_more": (offset + limit) < total_count,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_plugin(
        db: AsyncSession,
        plugin_id: str,
    ) -> Dict[str, Any]:
        """Get plugin details.
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            
        Returns:
            Plugin details
        """
        try:
            result = await db.execute(
                select(Plugin).where(Plugin.id == plugin_id)
            )
            plugin = result.scalar_one_or_none()
            
            if not plugin:
                return {
                    "error": "Plugin not found",
                    "success": False,
                }
            
            # Increment download count
            await db.execute(
                update(Plugin).where(Plugin.id == plugin_id).values(
                    downloads=Plugin.downloads + 1
                )
            )
            await db.commit()
            
            return {
                "id": plugin.id,
                "name": plugin.name,
                "version": plugin.version,
                "category": plugin.category,
                "description": plugin.description,
                "author_id": plugin.author_id,
                "source_url": plugin.source_url,
                "documentation_url": plugin.documentation_url,
                "plugin_code": plugin.plugin_code,
                "dependencies": plugin.dependencies,
                "metadata": plugin.metadata,
                "downloads": plugin.downloads + 1,
                "rating": plugin.rating,
                "is_verified": plugin.is_verified,
                "is_featured": plugin.is_featured,
                "created_at": plugin.created_at.isoformat(),
                "updated_at": plugin.updated_at.isoformat(),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def submit_review(
        db: AsyncSession,
        plugin_id: str,
        reviewer_id: str,
        rating: int,
        review_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit a review for a plugin.
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            reviewer_id: Reviewer ID
            rating: Rating (1-5)
            review_text: Review text
            
        Returns:
            Review submission result
        """
        try:
            # Validate rating
            if not 1 <= rating <= 5:
                return {
                    "error": "Rating must be between 1 and 5",
                    "success": False,
                }
            
            # Create review
            review = PluginReview(
                plugin_id=plugin_id,
                reviewer_id=reviewer_id,
                rating=rating,
                review_text=review_text,
            )
            
            db.add(review)
            await db.commit()
            await db.refresh(review)
            
            # Update plugin rating
            result = await db.execute(
                select(PluginReview).where(PluginReview.plugin_id == plugin_id)
            )
            reviews = result.scalars().all()
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            
            await db.execute(
                update(Plugin).where(Plugin.id == plugin_id).values(
                    rating=avg_rating
                )
            )
            await db.commit()
            
            return {
                "review_id": review.id,
                "rating": rating,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_trending_plugins(
        db: AsyncSession,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get trending plugins.
        
        Args:
            db: Database session
            limit: Maximum results
            
        Returns:
            Trending plugins
        """
        try:
            result = await db.execute(
                select(Plugin)
                .where(Plugin.is_verified == True)
                .order_by(Plugin.downloads.desc())
                .limit(limit)
            )
            plugins = result.scalars().all()
            
            return {
                "plugins": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "version": p.version,
                        "category": p.category,
                        "downloads": p.downloads,
                        "rating": p.rating,
                    }
                    for p in plugins
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
