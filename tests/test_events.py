"""
Tests for the event system in IndoClaw.
"""

import pytest
import json
import time
from datetime import datetime
from src.core.events.publisher import (
    EventPublisher,
    EventCallback,
    WebhookCallback,
    FileCallback,
    ConsoleCallback,
    AgentEvent,
    EventType
)


class TestAgentEvent:
    """Tests for AgentEvent dataclass."""

    def test_event_creation(self):
        """Test creating an event."""
        event = AgentEvent(
            event_type=EventType.TASK_START,
            timestamp="2024-01-01T00:00:00",
            agent_id="test_agent",
            payload={"task": "test task"},
            metadata={"user": "admin"}
        )
        assert event.event_type == EventType.TASK_START
        assert event.agent_id == "test_agent"
        assert event.payload == {"task": "test task"}

    def test_event_to_dict(self):
        """Test event to dictionary conversion."""
        event = AgentEvent(
            event_type=EventType.ERROR,
            timestamp=datetime.now().isoformat(),
            agent_id="agent1",
            payload={"error": "test error"}
        )
        result = event.to_dict()
        assert result["event_type"] == "error"
        assert result["agent_id"] == "agent1"
        assert result["payload"]["error"] == "test error"

    def test_event_to_json(self):
        """Test event to JSON conversion."""
        event = AgentEvent(
            event_type=EventType.TOOL_EXECUTED,
            timestamp=datetime.now().isoformat(),
            agent_id="agent1",
            payload={"tool": "calculator"}
        )
        json_str = event.to_json()
        result = json.loads(json_str)
        assert result["event_type"] == "tool_executed"
        assert result["agent_id"] == "agent1"


class TestEventPublisher:
    """Tests for EventPublisher."""

    def test_publish_event(self):
        """Test publishing an event."""
        publisher = EventPublisher()
        publisher.publish(
            event_type=EventType.TASK_START,
            agent_id="test_agent",
            payload={"task": "test"}
        )
        history = publisher.get_history()
        assert len(history) == 1
        assert history[0].event_type == EventType.TASK_START

    def test_publish_disabled(self):
        """Test that publishing is disabled."""
        publisher = EventPublisher()
        publisher.disable()
        publisher.publish(EventType.TASK_START, "agent1")
        history = publisher.get_history()
        assert len(history) == 0

    def test_get_history_filtered(self):
        """Test filtering history by event type."""
        publisher = EventPublisher()
        publisher.publish(EventType.TASK_START, "agent1")
        publisher.publish(EventType.TASK_END, "agent1")
        publisher.publish(EventType.ERROR, "agent2")

        task_start = publisher.get_history(event_type=EventType.TASK_START)
        assert len(task_start) == 1

        agent1_events = publisher.get_history(agent_id="agent1")
        assert len(agent1_events) == 2

    def test_clear_history(self):
        """Test clearing event history."""
        publisher = EventPublisher()
        publisher.publish(EventType.TASK_START, "agent1")
        publisher.publish(EventType.TASK_END, "agent1")
        publisher.clear_history()
        assert len(publisher.get_history()) == 0


class TestConsoleCallback:
    """Tests for ConsoleCallback."""

    def test_notify(self, capsys):
        """Test console notification."""
        callback = ConsoleCallback()
        event = AgentEvent(
            event_type=EventType.TOOL_EXECUTED,
            timestamp=datetime.now().isoformat(),
            agent_id="test_agent",
            payload={"tool": "calculator"}
        )
        callback.notify(event)
        captured = capsys.readouterr()
        assert "tool_executed" in captured.out


class TestFileCallback:
    """Tests for FileCallback."""

    def test_notify_write_file(self, tmp_path):
        """Test writing event to file."""
        filepath = tmp_path / "events.log"
        callback = FileCallback(str(filepath))

        event = AgentEvent(
            event_type=EventType.TASK_START,
            timestamp=datetime.now().isoformat(),
            agent_id="test_agent"
        )
        callback.notify(event)

        content = filepath.read_text()
        assert "task_start" in content
        assert "test_agent" in content


class TestEventTypes:
    """Tests for event type constants."""

    def test_all_event_types(self):
        """Test all event types are defined."""
        expected_types = [
            "task_start", "task_end", "tool_executed",
            "tool_approval_needed", "error", "plan_created",
            "plan_approved", "input_requested", "input_received",
            "agent_thought", "memory_updated"
        ]
        for event_type in EventType:
            assert event_type.value in expected_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
