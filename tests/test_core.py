"""
Core tests for IndoClaw AI Agent OS.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.memory.short_term import ShortTermMemory, Message
from core.tools.base import BaseTool, ToolResult


class TestShortTermMemory:
    """Tests for short-term memory."""
    
    def test_initialization(self):
        """Test memory initialization."""
        memory = ShortTermMemory(capacity=5)
        assert memory.capacity == 5
        assert len(memory.messages) == 0
    
    def test_add_message(self):
        """Test adding messages."""
        memory = ShortTermMemory(capacity=5)
        memory.add_message("user", "Hello")
        
        assert len(memory.messages) == 1
        assert memory.messages[0].role == "user"
        assert memory.messages[0].content == "Hello"
    
    def test_get_recent_messages(self):
        """Test getting recent messages."""
        memory = ShortTermMemory(capacity=5)
        
        for i in range(7):
            memory.add_message("user", f"Message {i}")
        
        recent = memory.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[0].content == "Message 4"  # Oldest in the 3
    
    def test_get_context(self):
        """Test getting context as list of dicts."""
        memory = ShortTermMemory(capacity=5)
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")
        
        context = memory.get_context()
        assert len(context) == 2
        assert context[0] == {"role": "user", "content": "Hello"}
        assert context[1] == {"role": "assistant", "content": "Hi there!"}
    
    def test_clear(self):
        """Test clearing memory."""
        memory = ShortTermMemory(capacity=5)
        memory.add_message("user", "Hello")
        memory.add_message("user", "World")
        
        memory.clear()
        assert len(memory.messages) == 0


class TestToolResult:
    """Tests for ToolResult."""
    
    def test_success_result(self):
        """Test successful tool result."""
        result = ToolResult(success=True, content={"data": "test"})
        assert result.success is True
        assert result.error is None
    
    def test_error_result(self):
        """Test error tool result."""
        result = ToolResult(success=False, error="Something went wrong")
        assert result.success is False
        assert "Something went wrong" in result.error


class TestBaseTool:
    """Tests for BaseTool."""
    
    def test_tool_info(self):
        """Test tool information."""
        tool = BaseTool()
        info = tool.get_info()
        
        assert "name" in info
        assert "description" in info
        assert info["enabled"] == "True"
    
    def test_enable_disable(self):
        """Test enabling/disabling tool."""
        tool = BaseTool()
        assert tool.is_enabled()
        
        tool.disable()
        assert not tool.is_enabled()
        
        tool.enable()
        assert tool.is_enabled()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])