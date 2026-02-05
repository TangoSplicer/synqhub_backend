"""
SynQ Debugger - Interactive debugging support for the classical language

Provides breakpoints, stepping, variable inspection, and call stack analysis.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import inspect


class DebuggerState(Enum):
    """Debugger state."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"


class StepType(Enum):
    """Step type."""
    INTO = "into"
    OVER = "over"
    OUT = "out"


@dataclass
class Breakpoint:
    """Breakpoint information."""
    id: int
    file: str
    line: int
    column: int = 0
    condition: Optional[str] = None
    hit_count: int = 0
    enabled: bool = True
    log_message: Optional[str] = None


@dataclass
class StackFrame:
    """Stack frame information."""
    id: int
    name: str
    file: str
    line: int
    column: int = 0
    variables: Dict[str, Any] = field(default_factory=dict)
    scopes: List[str] = field(default_factory=list)


@dataclass
class Variable:
    """Variable information."""
    name: str
    value: Any
    type: str
    scope: str
    indexed_variables: Optional[int] = None
    named_variables: Optional[int] = None


@dataclass
class Thread:
    """Thread information."""
    id: int
    name: str
    state: str


class SynQDebugger:
    """Interactive debugger for SynQ classical language."""
    
    def __init__(self):
        """Initialize debugger."""
        self.state = DebuggerState.STOPPED
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.breakpoint_counter = 0
        self.stack_frames: List[StackFrame] = []
        self.threads: Dict[int, Thread] = {}
        self.thread_counter = 0
        self.current_frame_id = 0
        self.variables: Dict[str, Variable] = {}
        self.watches: Dict[str, str] = {}
        self.output_events: List[Dict] = []
    
    # ========================================================================
    # Breakpoint Management
    # ========================================================================
    
    def set_breakpoint(self, file: str, line: int, column: int = 0,
                      condition: Optional[str] = None,
                      log_message: Optional[str] = None) -> Breakpoint:
        """Set a breakpoint."""
        self.breakpoint_counter += 1
        bp = Breakpoint(
            id=self.breakpoint_counter,
            file=file,
            line=line,
            column=column,
            condition=condition,
            log_message=log_message
        )
        self.breakpoints[bp.id] = bp
        return bp
    
    def remove_breakpoint(self, breakpoint_id: int) -> bool:
        """Remove a breakpoint."""
        if breakpoint_id in self.breakpoints:
            del self.breakpoints[breakpoint_id]
            return True
        return False
    
    def disable_breakpoint(self, breakpoint_id: int) -> bool:
        """Disable a breakpoint."""
        if breakpoint_id in self.breakpoints:
            self.breakpoints[breakpoint_id].enabled = False
            return True
        return False
    
    def enable_breakpoint(self, breakpoint_id: int) -> bool:
        """Enable a breakpoint."""
        if breakpoint_id in self.breakpoints:
            self.breakpoints[breakpoint_id].enabled = True
            return True
        return False
    
    def get_breakpoints(self, file: Optional[str] = None) -> List[Breakpoint]:
        """Get breakpoints."""
        bps = list(self.breakpoints.values())
        if file:
            bps = [bp for bp in bps if bp.file == file]
        return bps
    
    def check_breakpoint(self, file: str, line: int) -> Optional[Breakpoint]:
        """Check if breakpoint exists at location."""
        for bp in self.breakpoints.values():
            if bp.file == file and bp.line == line and bp.enabled:
                return bp
        return None
    
    # ========================================================================
    # Execution Control
    # ========================================================================
    
    def start(self) -> None:
        """Start debugging."""
        self.state = DebuggerState.RUNNING
    
    def pause(self) -> None:
        """Pause execution."""
        self.state = DebuggerState.PAUSED
    
    def resume(self) -> None:
        """Resume execution."""
        self.state = DebuggerState.RUNNING
    
    def terminate(self) -> None:
        """Terminate debugging."""
        self.state = DebuggerState.TERMINATED
    
    def step(self, step_type: StepType) -> None:
        """Step execution."""
        self.state = DebuggerState.PAUSED
        # Stepping logic would be implemented here
    
    def step_into(self) -> None:
        """Step into function."""
        self.step(StepType.INTO)
    
    def step_over(self) -> None:
        """Step over function."""
        self.step(StepType.OVER)
    
    def step_out(self) -> None:
        """Step out of function."""
        self.step(StepType.OUT)
    
    # ========================================================================
    # Stack Frame Management
    # ========================================================================
    
    def push_frame(self, name: str, file: str, line: int, 
                   column: int = 0) -> StackFrame:
        """Push stack frame."""
        frame_id = len(self.stack_frames)
        frame = StackFrame(
            id=frame_id,
            name=name,
            file=file,
            line=line,
            column=column
        )
        self.stack_frames.append(frame)
        self.current_frame_id = frame_id
        return frame
    
    def pop_frame(self) -> Optional[StackFrame]:
        """Pop stack frame."""
        if self.stack_frames:
            frame = self.stack_frames.pop()
            if self.stack_frames:
                self.current_frame_id = len(self.stack_frames) - 1
            return frame
        return None
    
    def get_stack_trace(self) -> List[StackFrame]:
        """Get stack trace."""
        return self.stack_frames.copy()
    
    def get_frame(self, frame_id: int) -> Optional[StackFrame]:
        """Get specific frame."""
        if 0 <= frame_id < len(self.stack_frames):
            return self.stack_frames[frame_id]
        return None
    
    def set_current_frame(self, frame_id: int) -> bool:
        """Set current frame."""
        if 0 <= frame_id < len(self.stack_frames):
            self.current_frame_id = frame_id
            return True
        return False
    
    # ========================================================================
    # Variable Inspection
    # ========================================================================
    
    def set_variable(self, name: str, value: Any, scope: str = "local") -> Variable:
        """Set variable value."""
        var = Variable(
            name=name,
            value=value,
            type=type(value).__name__,
            scope=scope
        )
        self.variables[name] = var
        return var
    
    def get_variable(self, name: str) -> Optional[Variable]:
        """Get variable."""
        return self.variables.get(name)
    
    def get_variables(self, scope: Optional[str] = None) -> List[Variable]:
        """Get all variables."""
        vars_list = list(self.variables.values())
        if scope:
            vars_list = [v for v in vars_list if v.scope == scope]
        return vars_list
    
    def update_variable(self, name: str, value: Any) -> bool:
        """Update variable value."""
        if name in self.variables:
            self.variables[name].value = value
            self.variables[name].type = type(value).__name__
            return True
        return False
    
    def delete_variable(self, name: str) -> bool:
        """Delete variable."""
        if name in self.variables:
            del self.variables[name]
            return True
        return False
    
    # ========================================================================
    # Watch Expressions
    # ========================================================================
    
    def add_watch(self, expression: str) -> str:
        """Add watch expression."""
        watch_id = f"watch_{len(self.watches)}"
        self.watches[watch_id] = expression
        return watch_id
    
    def remove_watch(self, watch_id: str) -> bool:
        """Remove watch expression."""
        if watch_id in self.watches:
            del self.watches[watch_id]
            return True
        return False
    
    def get_watches(self) -> Dict[str, str]:
        """Get all watch expressions."""
        return self.watches.copy()
    
    def evaluate_watch(self, watch_id: str) -> Optional[Any]:
        """Evaluate watch expression."""
        if watch_id not in self.watches:
            return None
        
        expression = self.watches[watch_id]
        try:
            # Evaluate in context of current variables
            return eval(expression, {"__builtins__": {}}, self.variables)
        except Exception:
            return None
    
    # ========================================================================
    # Thread Management
    # ========================================================================
    
    def create_thread(self, name: str) -> Thread:
        """Create thread."""
        thread_id = self.thread_counter
        self.thread_counter += 1
        thread = Thread(id=thread_id, name=name, state="running")
        self.threads[thread_id] = thread
        return thread
    
    def get_threads(self) -> List[Thread]:
        """Get all threads."""
        return list(self.threads.values())
    
    def get_thread(self, thread_id: int) -> Optional[Thread]:
        """Get specific thread."""
        return self.threads.get(thread_id)
    
    # ========================================================================
    # Output and Events
    # ========================================================================
    
    def output(self, text: str, category: str = "console") -> None:
        """Output text."""
        event = {
            "type": "output",
            "text": text,
            "category": category
        }
        self.output_events.append(event)
    
    def get_output_events(self) -> List[Dict]:
        """Get output events."""
        events = self.output_events.copy()
        self.output_events.clear()
        return events
    
    # ========================================================================
    # Source Code
    # ========================================================================
    
    def get_source(self, file: str, start_line: int = 1, 
                   end_line: Optional[int] = None) -> Dict[str, Any]:
        """Get source code."""
        try:
            with open(file, 'r') as f:
                lines = f.readlines()
            
            if end_line is None:
                end_line = len(lines)
            
            source_lines = []
            for i in range(max(0, start_line - 1), min(len(lines), end_line)):
                source_lines.append({
                    "line": i + 1,
                    "text": lines[i].rstrip('\n')
                })
            
            return {
                "file": file,
                "lines": source_lines,
                "total_lines": len(lines)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================================================
    # State Information
    # ========================================================================
    
    def get_state(self) -> Dict[str, Any]:
        """Get debugger state."""
        return {
            "state": self.state.value,
            "stack_depth": len(self.stack_frames),
            "current_frame": self.current_frame_id,
            "breakpoint_count": len(self.breakpoints),
            "thread_count": len(self.threads),
            "variable_count": len(self.variables),
            "watch_count": len(self.watches)
        }


__all__ = ['SynQDebugger', 'Breakpoint', 'StackFrame', 'Variable', 'Thread', 'DebuggerState', 'StepType']
