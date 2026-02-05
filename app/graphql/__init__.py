"""GraphQL module for flexible API queries."""

try:
    from app.graphql.schema import schema
except ImportError:
    schema = None

__all__ = ["schema"]
