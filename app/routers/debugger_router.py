"""
Debugger Router - Debugging endpoints for FastAPI
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from app.debugger.debugger import SynQDebugger, StepType


router = APIRouter(prefix="/api/v1/debugger", tags=["debugger"])

# Global debugger instance
debugger = SynQDebugger()


# ============================================================================
# Breakpoint Management
# ============================================================================

@router.post("/breakpoints")
async def set_breakpoint(file: str = Body(...), line: int = Body(...),
                        column: int = Body(0), condition: Optional[str] = Body(None),
                        log_message: Optional[str] = Body(None)):
    """Set a breakpoint."""
    try:
        bp = debugger.set_breakpoint(file, line, column, condition, log_message)
        return {
            "id": bp.id,
            "file": bp.file,
            "line": bp.line,
            "column": bp.column,
            "condition": bp.condition,
            "log_message": bp.log_message
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/breakpoints/{breakpoint_id}")
async def remove_breakpoint(breakpoint_id: int):
    """Remove a breakpoint."""
    try:
        if debugger.remove_breakpoint(breakpoint_id):
            return {"status": "success", "message": f"Breakpoint {breakpoint_id} removed"}
        else:
            raise HTTPException(status_code=404, detail="Breakpoint not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/breakpoints/{breakpoint_id}/disable")
async def disable_breakpoint(breakpoint_id: int):
    """Disable a breakpoint."""
    try:
        if debugger.disable_breakpoint(breakpoint_id):
            return {"status": "success", "message": f"Breakpoint {breakpoint_id} disabled"}
        else:
            raise HTTPException(status_code=404, detail="Breakpoint not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/breakpoints/{breakpoint_id}/enable")
async def enable_breakpoint(breakpoint_id: int):
    """Enable a breakpoint."""
    try:
        if debugger.enable_breakpoint(breakpoint_id):
            return {"status": "success", "message": f"Breakpoint {breakpoint_id} enabled"}
        else:
            raise HTTPException(status_code=404, detail="Breakpoint not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/breakpoints")
async def get_breakpoints(file: Optional[str] = None) -> List[Dict]:
    """Get all breakpoints."""
    try:
        bps = debugger.get_breakpoints(file)
        return [
            {
                "id": bp.id,
                "file": bp.file,
                "line": bp.line,
                "column": bp.column,
                "enabled": bp.enabled,
                "condition": bp.condition,
                "log_message": bp.log_message,
                "hit_count": bp.hit_count
            }
            for bp in bps
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Execution Control
# ============================================================================

@router.post("/start")
async def start_debugging():
    """Start debugging."""
    try:
        debugger.start()
        return {"status": "success", "message": "Debugging started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pause")
async def pause_debugging():
    """Pause execution."""
    try:
        debugger.pause()
        return {"status": "success", "message": "Execution paused"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resume")
async def resume_debugging():
    """Resume execution."""
    try:
        debugger.resume()
        return {"status": "success", "message": "Execution resumed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/terminate")
async def terminate_debugging():
    """Terminate debugging."""
    try:
        debugger.terminate()
        return {"status": "success", "message": "Debugging terminated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/step-into")
async def step_into():
    """Step into function."""
    try:
        debugger.step_into()
        return {"status": "success", "message": "Stepped into"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/step-over")
async def step_over():
    """Step over function."""
    try:
        debugger.step_over()
        return {"status": "success", "message": "Stepped over"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/step-out")
async def step_out():
    """Step out of function."""
    try:
        debugger.step_out()
        return {"status": "success", "message": "Stepped out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Stack Frames
# ============================================================================

@router.get("/stack-trace")
async def get_stack_trace() -> List[Dict]:
    """Get stack trace."""
    try:
        frames = debugger.get_stack_trace()
        return [
            {
                "id": f.id,
                "name": f.name,
                "file": f.file,
                "line": f.line,
                "column": f.column
            }
            for f in frames
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/frames/{frame_id}")
async def get_frame(frame_id: int) -> Dict:
    """Get specific frame."""
    try:
        frame = debugger.get_frame(frame_id)
        if frame:
            return {
                "id": frame.id,
                "name": frame.name,
                "file": frame.file,
                "line": frame.line,
                "column": frame.column,
                "variables": len(frame.variables)
            }
        else:
            raise HTTPException(status_code=404, detail="Frame not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Variable Inspection
# ============================================================================

@router.get("/variables")
async def get_variables(scope: Optional[str] = None) -> List[Dict]:
    """Get variables."""
    try:
        variables = debugger.get_variables(scope)
        return [
            {
                "name": v.name,
                "value": str(v.value),
                "type": v.type,
                "scope": v.scope
            }
            for v in variables
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variables/{name}")
async def get_variable(name: str) -> Dict:
    """Get specific variable."""
    try:
        var = debugger.get_variable(name)
        if var:
            return {
                "name": var.name,
                "value": str(var.value),
                "type": var.type,
                "scope": var.scope
            }
        else:
            raise HTTPException(status_code=404, detail="Variable not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/variables/{name}")
async def update_variable(name: str, value: Any = Body(...)):
    """Update variable value."""
    try:
        if debugger.update_variable(name, value):
            return {"status": "success", "message": f"Variable {name} updated"}
        else:
            raise HTTPException(status_code=404, detail="Variable not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Watch Expressions
# ============================================================================

@router.post("/watches")
async def add_watch(expression: str = Body(...)):
    """Add watch expression."""
    try:
        watch_id = debugger.add_watch(expression)
        return {"id": watch_id, "expression": expression}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/watches/{watch_id}")
async def remove_watch(watch_id: str):
    """Remove watch expression."""
    try:
        if debugger.remove_watch(watch_id):
            return {"status": "success", "message": f"Watch {watch_id} removed"}
        else:
            raise HTTPException(status_code=404, detail="Watch not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/watches")
async def get_watches() -> Dict[str, str]:
    """Get all watch expressions."""
    try:
        return debugger.get_watches()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Source Code
# ============================================================================

@router.get("/source")
async def get_source(file: str, start_line: int = 1, end_line: Optional[int] = None) -> Dict:
    """Get source code."""
    try:
        return debugger.get_source(file, start_line, end_line)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# State
# ============================================================================

@router.get("/state")
async def get_state() -> Dict:
    """Get debugger state."""
    try:
        return debugger.get_state()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def debugger_health():
    """Check debugger health."""
    return {
        "status": "healthy",
        "service": "synq-debugger",
        "version": "1.0.0"
    }
