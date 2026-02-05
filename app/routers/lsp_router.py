"""
LSP Router - Language Server Protocol endpoints for FastAPI
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from app.lsp.server import (
    SynQLSPServer, CompletionItem, Diagnostic, SymbolInformation,
    Location, Hover, Position, Range
)


router = APIRouter(prefix="/api/v1/lsp", tags=["lsp"])

# Global LSP server instance
lsp_server = SynQLSPServer()


# ============================================================================
# Document Management
# ============================================================================

@router.post("/documents/open")
async def open_document(uri: str = Body(...), text: str = Body(...)):
    """Open a document for analysis."""
    try:
        lsp_server.open_document(uri, text)
        return {"status": "success", "message": f"Document {uri} opened"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/documents/close")
async def close_document(uri: str = Body(...)):
    """Close a document."""
    try:
        lsp_server.close_document(uri)
        return {"status": "success", "message": f"Document {uri} closed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/documents/update")
async def update_document(uri: str = Body(...), text: str = Body(...)):
    """Update document content."""
    try:
        lsp_server.update_document(uri, text)
        return {"status": "success", "message": f"Document {uri} updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Code Completion
# ============================================================================

@router.get("/completions")
async def get_completions(uri: str, line: int, character: int) -> List[dict]:
    """Get code completion suggestions."""
    try:
        completions = lsp_server.get_completions(uri, line, character)
        return [
            {
                "label": c.label,
                "kind": c.kind,
                "detail": c.detail,
                "documentation": c.documentation,
                "sortText": c.sortText,
                "filterText": c.filterText,
                "insertText": c.insertText
            }
            for c in completions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Navigation
# ============================================================================

@router.get("/definition")
async def get_definition(uri: str, line: int, character: int) -> Optional[dict]:
    """Get definition location for symbol."""
    try:
        location = lsp_server.get_definition(uri, line, character)
        if location:
            return {
                "uri": location.uri,
                "range": {
                    "start": {"line": location.range.start.line, "character": location.range.start.character},
                    "end": {"line": location.range.end.line, "character": location.range.end.character}
                }
            }
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/references")
async def find_references(uri: str, line: int, character: int) -> List[dict]:
    """Find all references to symbol."""
    try:
        references = lsp_server.find_references(uri, line, character)
        return [
            {
                "uri": ref.uri,
                "range": {
                    "start": {"line": ref.range.start.line, "character": ref.range.start.character},
                    "end": {"line": ref.range.end.line, "character": ref.range.end.character}
                }
            }
            for ref in references
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Hover Information
# ============================================================================

@router.get("/hover")
async def get_hover(uri: str, line: int, character: int) -> Optional[dict]:
    """Get hover information for symbol."""
    try:
        hover = lsp_server.get_hover(uri, line, character)
        if hover:
            return {
                "contents": hover.contents,
                "range": {
                    "start": {"line": hover.range.start.line, "character": hover.range.start.character},
                    "end": {"line": hover.range.end.line, "character": hover.range.end.character}
                } if hover.range else None
            }
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Formatting
# ============================================================================

@router.post("/format")
async def format_document(uri: str = Body(...)) -> dict:
    """Format entire document."""
    try:
        formatted = lsp_server.format_document(uri)
        return {"formatted": formatted}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/format-range")
async def format_range(uri: str = Body(...), start_line: int = Body(...), 
                       end_line: int = Body(...)) -> dict:
    """Format range of lines."""
    try:
        formatted = lsp_server.format_range(uri, start_line, end_line)
        return {"formatted": formatted}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Workspace Symbols
# ============================================================================

@router.get("/workspace-symbols")
async def get_workspace_symbols(query: str = "") -> List[dict]:
    """Get all symbols in workspace."""
    try:
        symbols = lsp_server.get_workspace_symbols(query)
        return [
            {
                "name": s.name,
                "kind": s.kind,
                "location": {
                    "uri": s.location.uri,
                    "range": {
                        "start": {"line": s.location.range.start.line, "character": s.location.range.start.character},
                        "end": {"line": s.location.range.end.line, "character": s.location.range.end.character}
                    }
                },
                "containerName": s.containerName
            }
            for s in symbols
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Diagnostics
# ============================================================================

@router.get("/diagnostics")
async def get_diagnostics(uri: str) -> List[dict]:
    """Get diagnostics for document."""
    try:
        diagnostics = lsp_server.get_diagnostics(uri)
        return [
            {
                "range": {
                    "start": {"line": d.range.start.line, "character": d.range.start.character},
                    "end": {"line": d.range.end.line, "character": d.range.end.character}
                },
                "severity": d.severity,
                "code": d.code,
                "source": d.source,
                "message": d.message,
                "relatedInformation": d.relatedInformation
            }
            for d in diagnostics
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def lsp_health():
    """Check LSP server health."""
    return {
        "status": "healthy",
        "service": "synq-lsp",
        "version": "1.0.0"
    }
