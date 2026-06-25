"""
Observation and thought tracing for IndoClaw.
Captures the agent's reasoning steps into a readable format for debugging.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import os


class TraceLevel(Enum):
    """Logging levels for trace entries."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class TraceEntry:
    """A single trace entry capturing an agent reasoning step."""
    timestamp: str
    level: str
    component: str
    action: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "TraceEntry":
        """Create from dictionary."""
        return cls(
            timestamp=data.get("timestamp", ""),
            level=data.get("level", "info"),
            component=data.get("component", "unknown"),
            action=data.get("action", ""),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            metadata=data.get("metadata", {}),
        )


class ThoughtTracer:
    """
    Traces agent reasoning steps for observability.

    Captures:
    - Agent decisions
    - Tool selections
    - Memory operations
    - LLM calls
    - Error states
    """

    def __init__(self, enabled: bool = True, log_file: str = "./data/traces"):
        self.enabled = enabled
        self.log_file = log_file
        self.entries: List[TraceEntry] = []
        self._ensure_log_dir()

    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def trace(
        self,
        component: str,
        action: str,
        level: TraceLevel = TraceLevel.INFO,
        input_data: Dict[str, Any] = None,
        output_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
    ) -> TraceEntry:
        """
        Record a trace entry.

        Args:
            component: The component making the trace (e.g., 'agent', 'tool', 'memory')
            action: The action being performed
            level: The trace level
            input_data: Input data for the action
            output_data: Output data from the action
            metadata: Additional metadata

        Returns:
            The created TraceEntry
        """
        if not self.enabled:
            return TraceEntry(
                timestamp="",
                level=level.value,
                component=component,
                action=action,
            )

        entry = TraceEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            component=component,
            action=action,
            input_data=input_data or {},
            output_data=output_data or {},
            metadata=metadata or {},
        )

        self.entries.append(entry)
        self._write_entry(entry)
        return entry

    def _write_entry(self, entry: TraceEntry) -> None:
        """Write entry to log file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except Exception:
            pass  # Silently fail to avoid disrupting operation

    def trace_agent_thought(
        self,
        thought: str,
        reasoning: Dict[str, Any] = None,
        confidence: float = None,
    ) -> TraceEntry:
        """Trace an agent reasoning step."""
        return self.trace(
            component="agent",
            action="thought",
            level=TraceLevel.DEBUG,
            input_data={"thought": thought},
            output_data={"reasoning": reasoning or {}, "confidence": confidence},
        )

    def trace_tool_selection(
        self,
        tool_name: str,
        task: str,
        reasoning: str = None,
    ) -> TraceEntry:
        """Trace tool selection decision."""
        return self.trace(
            component="agent",
            action="tool_selection",
            level=TraceLevel.INFO,
            input_data={"tool": tool_name, "task": task},
            output_data={"reasoning": reasoning},
        )

    def trace_llm_call(
        self,
        prompt: str,
        response: str,
        model: str = None,
        tokens_used: int = None,
    ) -> TraceEntry:
        """Trace an LLM call."""
        return self.trace(
            component="llm",
            action="call",
            level=TraceLevel.DEBUG,
            input_data={"prompt": prompt, "model": model},
            output_data={"response": response, "tokens_used": tokens_used},
        )

    def trace_memory_operation(
        self,
        operation: str,
        content: str = None,
        result: Dict[str, Any] = None,
    ) -> TraceEntry:
        """Trace a memory operation."""
        return self.trace(
            component="memory",
            action=operation,
            level=TraceLevel.DEBUG,
            input_data={"content": content},
            output_data=result,
        )

    def trace_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any] = None,
    ) -> TraceEntry:
        """Trace an error event."""
        return self.trace(
            component="error",
            action=error_type,
            level=TraceLevel.ERROR,
            input_data={"error": error_message, "context": context or {}},
        )

    def get_entries(self, level: TraceLevel = None) -> List[TraceEntry]:
        """Get trace entries, optionally filtered by level."""
        if level is None:
            return self.entries
        return [e for e in self.entries if e.level == level.value]

    def clear(self) -> None:
        """Clear all trace entries."""
        self.entries = []
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
        except Exception:
            pass

    def export(self, format: str = "json") -> str:
        """Export traces to a string."""
        if format == "json":
            return json.dumps([e.to_dict() for e in self.entries], indent=2)
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unknown format: {format}")

    def _export_markdown(self) -> str:
        """Export traces as markdown."""
        lines = ["# Agent Trace Log", ""]
        for entry in self.entries:
            lines.append(f"## {entry.action}")
            lines.append(f"- **Component**: {entry.component}")
            lines.append(f"- **Level**: {entry.level}")
            lines.append(f"- **Time**: {entry.timestamp}")
            if entry.input_data:
                lines.append(f"- **Input**: {json.dumps(entry.input_data)}")
            if entry.output_data:
                lines.append(f"- **Output**: {json.dumps(entry.output_data)}")
            lines.append("")
        return "\n".join(lines)


# Global tracer instance
_global_tracer = ThoughtTracer()


def get_tracer() -> ThoughtTracer:
    """Get the global tracer instance."""
    return _global_tracer


def trace(*args, **kwargs) -> TraceEntry:
    """Convenience function for global tracing."""
    return _global_tracer.trace(*args, **kwargs)


def set_tracer_enabled(enabled: bool) -> None:
    """Enable or disable tracing globally."""
    _global_tracer.enabled = enabled
