"""
Tests for tools module (Phase 2: Tool Registry).
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.tools.base import BaseTool, ToolResult
from src.core.tools.registry import ToolRegistry


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()

        class TestTool(BaseTool):
            name = "test_tool"
            description = "Test tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        tool = TestTool()
        registry.register(tool)

        assert registry.get_tool("test_tool") == tool
        assert "test_tool" in registry.list_tools()

    def test_register_disabled_tool(self):
        """Test that disabled tools are not registered."""
        registry = ToolRegistry()

        class TestTool(BaseTool):
            name = "disabled_tool"
            description = "Disabled tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        tool = TestTool()
        tool.disable()
        registry.register(tool)

        assert registry.get_tool("disabled_tool") is None

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()

        class TestTool(BaseTool):
            name = "unregister_tool"
            description = "Unregister tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        tool = TestTool()
        registry.register(tool)
        assert registry.get_tool("unregister_tool") is not None

        registry.unregister("unregister_tool")
        assert registry.get_tool("unregister_tool") is None

    def test_list_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry()

        class TestTool1(BaseTool):
            name = "tool_1"
            description = "First tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test1")

        class TestTool2(BaseTool):
            name = "tool_2"
            description = "Second tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test2")

        registry.register(TestTool1())
        registry.register(TestTool2())

        tools = registry.list_tools()
        assert "tool_1" in tools
        assert "tool_2" in tools
        assert tools["tool_1"] == "First tool"
        assert tools["tool_2"] == "Second tool"

    def test_get_all_tools(self):
        """Test getting all tool instances."""
        registry = ToolRegistry()

        class TestTool(BaseTool):
            name = "test_tool"
            description = "Test tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        tool = TestTool()
        registry.register(tool)

        all_tools = registry.get_all_tools()
        assert len(all_tools) == 1
        assert all_tools["test_tool"] == tool

    def test_register_multiple(self):
        """Test registering multiple tools at once."""
        registry = ToolRegistry()

        class TestTool1(BaseTool):
            name = "batch_1"
            description = "Batch tool 1"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        class TestTool2(BaseTool):
            name = "batch_2"
            description = "Batch tool 2"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        class TestTool3(BaseTool):
            name = "batch_3"
            description = "Disabled tool"

            def _run(self, **kwargs):
                return ToolResult(success=True, content="test")

        tools = [TestTool1(), TestTool2(), TestTool3()]
        tools[2].disable()  # Disable third tool

        count = registry.register_multiple(tools)
        assert count == 2  # Only 2 enabled tools should be registered
        assert "batch_1" in registry.list_tools()
        assert "batch_2" in registry.list_tools()
        assert "batch_3" not in registry.list_tools()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
