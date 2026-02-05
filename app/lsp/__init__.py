"""
Language Server Protocol (LSP) Module

Provides IDE support with syntax highlighting, code completion, diagnostics,
and other language features.
"""

from .server import SynQLSPServer

__all__ = ['SynQLSPServer']
