"""
Tests for observation and thought tracing (Phase 4).
"""

import pytest
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.observation import (
    ThoughtTracer,
    TraceEntry,
    TraceLevel,
    get_tracer,
    set_tracer_enabled,
    trace,
)


class TestTraceEntry:
    """Tests for TraceEntry."""

    def test_create_entry(self):
        """Test creating a trace entry."""
        entry = TraceEntry(
            timestamp="2024-01-01T00:00:00",
            level="info",
            component="agent",
            action="thought",
        )

        assert entry.timestamp == "2024-01-01T00:00:00"
        assert entry.level == "info"
        assert entry.component == "agent"
        assert entry.action == "thought"
        assert entry.input_data == {}
        assert entry.output_data == {}

    def test_entry_with_data(self):
        """Test trace entry with input/output data."""
        entry = TraceEntry(
            timestamp="2024-01-01T00:00:00",
            level="info",
            component="agent",
            action="tool_selection",
            input_data={"tool": "search", "query": "test"},
            output_data={"reasoning": "Need to search for information"},
        )

        assert entry.input_data["tool"] == "search"
        assert entry.output_data["reasoning"] == "Need to search for information"

    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = TraceEntry(
            timestamp="2024-01-01T00:00:00",
            level="debug",
            component="llm",
            action="call",
        )

        data = entry.to_dict()

        assert data["component"] == "llm"
        assert data["action"] == "call"
        assert data["level"] == "debug"

    def test_entry_from_dict(self):
        """Test creating entry from dictionary."""
        original = TraceEntry(
            timestamp="2024-01-01T00:00:00",
            level="info",
            component="agent",
            action="thought",
        )

        data = original.to_dict()
        restored = TraceEntry.from_dict(data)

        assert restored.timestamp == original.timestamp
        assert restored.level == original.level
        assert restored.component == original.component
        assert restored.action == original.action


class TestThoughtTracer:
    """Tests for ThoughtTracer."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up a temporary directory for testing."""
        self.tracer = ThoughtTracer(log_file=str(tmp_path / "test_trace.jsonl"))
        self.tracer.clear()  # Clear any existing traces
        yield
        # Cleanup is automatic with tmp_path

    def test_tracer_enabled_by_default(self):
        """Test that tracer is enabled by default."""
        assert self.tracer.enabled is True

    def test_trace_method(self):
        """Test tracing a basic entry."""
        entry = self.tracer.trace(
            component="agent",
            action="thought",
            level=TraceLevel.DEBUG,
            input_data={"thought": "What should I do?"},
        )

        assert entry is not None
        assert entry.component == "agent"
        assert entry.action == "thought"
        assert entry.level == "debug"

    def test_trace_agent_thought(self):
        """Test tracing an agent thought."""
        entry = self.tracer.trace_agent_thought(
            thought="I should use the calculator tool",
            reasoning={"confidence": 0.9},
        )

        assert entry.component == "agent"
        assert entry.action == "thought"
        assert entry.input_data["thought"] == "I should use the calculator tool"
        assert entry.output_data["reasoning"]["confidence"] == 0.9

    def test_trace_tool_selection(self):
        """Test tracing tool selection."""
        entry = self.tracer.trace_tool_selection(
            tool_name="calculator",
            task="2 + 2",
            reasoning="User asked for a simple calculation",
        )

        assert entry.component == "agent"
        assert entry.action == "tool_selection"
        assert entry.input_data["tool"] == "calculator"
        assert entry.input_data["task"] == "2 + 2"

    def test_trace_llm_call(self):
        """Test tracing an LLM call."""
        entry = self.tracer.trace_llm_call(
            prompt="What is 2 + 2?",
            response="4",
            model="gpt-4",
            tokens_used=10,
        )

        assert entry.component == "llm"
        assert entry.action == "call"
        assert entry.input_data["prompt"] == "What is 2 + 2?"
        assert entry.output_data["response"] == "4"
        assert entry.output_data["tokens_used"] == 10

    def test_trace_memory_operation(self):
        """Test tracing a memory operation."""
        entry = self.tracer.trace_memory_operation(
            operation="add",
            content="User prefers dark mode",
            result={"id": "mem-123"},
        )

        assert entry.component == "memory"
        assert entry.action == "add"
        assert entry.input_data["content"] == "User prefers dark mode"

    def test_trace_error(self):
        """Test tracing an error."""
        entry = self.tracer.trace_error(
            error_type="ToolError",
            error_message="Tool not found",
            context={"tool": "calculator"},
        )

        assert entry.component == "error"
        assert entry.action == "ToolError"
        assert entry.level == "error"
        assert entry.input_data["error"] == "Tool not found"

    def test_get_entries(self):
        """Test getting trace entries."""
        self.tracer.trace(component="a", action="action1")
        self.tracer.trace(component="b", action="action2")
        self.tracer.trace(component="c", action="action3", level=TraceLevel.ERROR)

        all_entries = self.tracer.get_entries()
        assert len(all_entries) == 3

        error_entries = self.tracer.get_entries(TraceLevel.ERROR)
        assert len(error_entries) == 1
        assert error_entries[0].action == "action3"

    def test_clear_traces(self):
        """Test clearing all traces."""
        self.tracer.trace(component="a", action="action1")
        self.tracer.trace(component="b", action="action2")

        assert len(self.tracer.entries) == 2

        self.tracer.clear()
        assert len(self.tracer.entries) == 0

    def test_export_json(self):
        """Test exporting traces as JSON."""
        self.tracer.trace(component="a", action="action1")
        self.tracer.trace(component="b", action="action2")

        json_output = self.tracer.export("json")

        data = json.loads(json_output)
        assert len(data) == 2
        assert data[0]["component"] == "a"
        assert data[1]["component"] == "b"

    def test_export_markdown(self):
        """Test exporting traces as markdown."""
        self.tracer.trace(component="agent", action="thought", level=TraceLevel.INFO)

        md_output = self.tracer.export("markdown")

        assert "# Agent Trace Log" in md_output
        assert "## thought" in md_output

    def test_export_invalid_format(self):
        """Test exporting with invalid format."""
        with pytest.raises(ValueError):
            self.tracer.export("invalid_format")

    def test_trace_with_metadata(self):
        """Test tracing with additional metadata."""
        entry = self.tracer.trace(
            component="agent",
            action="decision",
            metadata={"session_id": "sess-123", "trace_id": "trace-456"},
        )

        assert entry.metadata["session_id"] == "sess-123"
        assert entry.metadata["trace_id"] == "trace-456"


class TestGlobalTracer:
    """Tests for global tracer functions."""

    def test_get_tracer(self):
        """Test getting the global tracer."""
        tracer = get_tracer()
        assert isinstance(tracer, ThoughtTracer)

    def test_set_tracer_enabled(self):
        """Test enabling/disabling global tracer."""
        set_tracer_enabled(False)
        tracer = get_tracer()
        assert tracer.enabled is False

        set_tracer_enabled(True)
        tracer = get_tracer()
        assert tracer.enabled is True

    def test_trace_convenience_function(self):
        """Test the trace convenience function."""
        entry = trace(component="test", action="test_action")
        assert entry is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
