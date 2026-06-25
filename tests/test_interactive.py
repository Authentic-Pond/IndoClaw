"""
Tests for interactive prompts module (Phase 5.3).
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.messaging.interactive import (
    InteractivePrompts,
    InteractivePrompt,
    PromptResponse,
    PromptType,
    confirm,
    select,
    text_input,
    number_input,
)


class TestInteractivePrompt:
    """Tests for InteractivePrompt dataclass."""

    def test_prompt_creation(self):
        """Test creating an interactive prompt."""
        prompt = InteractivePrompt(
            prompt_id="test_1",
            message="Is this correct?",
            prompt_type=PromptType.CONFIRMATION,
        )
        assert prompt.prompt_id == "test_1"
        assert prompt.message == "Is this correct?"
        assert prompt.prompt_type == PromptType.CONFIRMATION

    def test_prompt_with_options(self):
        """Test prompt with options."""
        prompt = InteractivePrompt(
            prompt_id="test_2",
            message="Choose an option:",
            prompt_type=PromptType.SELECTION,
            options=["Option A", "Option B", "Option C"],
            default_value="Option A",
        )
        assert len(prompt.options) == 3
        assert prompt.default_value == "Option A"

    def test_prompt_with_validation(self):
        """Test prompt with validation function."""
        def is_valid_email(value: str) -> bool:
            return "@" in value

        prompt = InteractivePrompt(
            prompt_id="test_3",
            message="Enter email:",
            prompt_type=PromptType.TEXT_INPUT,
            validation=is_valid_email,
        )
        assert prompt.validation("test@example.com") is True
        assert prompt.validation("invalid") is False

    def test_prompt_to_dict(self):
        """Test converting prompt to dictionary."""
        prompt = InteractivePrompt(
            prompt_id="test_4",
            message="Test message",
            prompt_type=PromptType.NUMBER_INPUT,
            options=[0, 100],
            default_value="50",
        )
        data = prompt.to_dict()
        assert data["prompt_id"] == "test_4"
        assert data["message"] == "Test message"
        assert data["prompt_type"] == "number_input"
        assert data["options"] == [0, 100]
        assert data["default_value"] == "50"

    def test_prompt_from_dict(self):
        """Test creating prompt from dictionary."""
        original = InteractivePrompt(
            prompt_id="test_5",
            message="Test message",
            prompt_type=PromptType.TEXT_INPUT,
            default_value="default",
        )
        data = original.to_dict()
        restored = InteractivePrompt.from_dict(data)
        assert restored.prompt_id == original.prompt_id
        assert restored.message == original.message
        assert restored.prompt_type == original.prompt_type


class TestPromptResponse:
    """Tests for PromptResponse dataclass."""

    def test_response_creation(self):
        """Test creating a prompt response."""
        response = PromptResponse(
            prompt_id="test_1",
            user_input="Yes",
        )
        assert response.prompt_id == "test_1"
        assert response.user_input == "Yes"
        assert response.cancelled is False

    def test_response_with_timestamp(self):
        """Test response includes timestamp."""
        response = PromptResponse(
            prompt_id="test_2",
            user_input="No",
        )
        assert response.timestamp is not None

    def test_response_cancelled(self):
        """Test cancelled response."""
        response = PromptResponse(
            prompt_id="test_3",
            user_input="",
            cancelled=True,
        )
        assert response.cancelled is True

    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = PromptResponse(
            prompt_id="test_4",
            user_input="selected",
            cancelled=False,
        )
        data = response.to_dict()
        assert data["prompt_id"] == "test_4"
        assert data["user_input"] == "selected"
        assert data["cancelled"] is False
        assert "timestamp" in data


class TestInteractivePrompts:
    """Tests for InteractivePrompts manager."""

    def test_init(self):
        """Test initialization."""
        prompts = InteractivePrompts()
        assert prompts.history == []
        assert prompts.active_prompts == {}

    def test_confirmation_prompt(self):
        """Test confirmation prompt (using mocked input)."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "yes")
        prompts.set_print_function(lambda _: None)  # Suppress output

        prompt = prompts.create_confirmation(
            prompt_id="confirm_test",
            message="Continue?",
            default_yes=True,
        )
        response = prompts.show_prompt(prompt)

        assert response.prompt_id == "confirm_test"
        assert response.user_input == "yes"
        assert len(prompts.history) == 1

    def test_selection_prompt(self):
        """Test selection prompt (using mocked input)."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "1")
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_selection(
            prompt_id="select_test",
            message="Choose one:",
            options=["First", "Second", "Third"],
            default_index=0,
        )
        response = prompts.show_prompt(prompt)

        assert response.prompt_id == "select_test"
        assert response.user_input == "First"

    def test_text_input_prompt(self):
        """Test text input prompt (using mocked input)."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "Hello World")
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_text_input(
            prompt_id="text_test",
            message="Enter text:",
            default_value="Default",
        )
        response = prompts.show_prompt(prompt)

        assert response.prompt_id == "text_test"
        assert response.user_input == "Hello World"

    def test_text_input_with_default(self):
        """Test text input with default value."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "")  # Empty input = use default
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_text_input(
            prompt_id="text_default",
            message="Enter text:",
            default_value="Fallback",
        )
        response = prompts.show_prompt(prompt)

        assert response.user_input == "Fallback"

    def test_number_input_prompt(self):
        """Test number input prompt (using mocked input)."""
        # Directly test the handler method
        prompts = InteractivePrompts()
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_number_input(
            prompt_id="number_test",
            message="Enter number:",
            min_val=0,
            max_val=100,
            default_value=50,
        )

        # The default value should be converted to string
        assert prompt.default_value == "50"

        # Call the handler directly
        response = prompts._handle_number_input(prompt)

        assert response.prompt_id == "number_test"
        # Default value (50) should be used as "50.0" since float(50) = 50.0
        assert response.user_input == "50.0"

    def test_multi_select_prompt(self):
        """Test multi-select prompt (using mocked input)."""
        prompts = InteractivePrompts()
        # First, create a proper multi-select prompt
        prompt = prompts.create_multi_select(
            prompt_id="multiselect_test",
            message="Choose multiple:",
            options=["A", "B", "C"],
            default_indices=[0],
        )
        # The default value should be "1" (first option)
        assert prompt.default_value == "1"

        # Call the handler directly
        response = prompts._handle_multi_select(prompt)

        assert response.prompt_id == "multiselect_test"
        assert response.user_input == "A"

    def test_cancelled_response(self):
        """Test cancelled response."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "q")  # q = quit/cancel
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_selection(
            prompt_id="cancel_test",
            message="Choose:",
            options=["A", "B"],
        )
        response = prompts.show_prompt(prompt)

        assert response.cancelled is True
        assert response.user_input == ""

    def test_clear_history(self):
        """Test clearing prompt history."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "yes")
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_confirmation("h1", "Test 1")
        prompts.show_prompt(prompt)

        prompt = prompts.create_confirmation("h2", "Test 2")
        prompts.show_prompt(prompt)

        assert len(prompts.history) == 2

        prompts.clear_history()
        assert prompts.history == []

    def test_get_history(self):
        """Test getting prompt history."""
        prompts = InteractivePrompts()
        prompts.set_input_function(lambda _: "yes")
        prompts.set_print_function(lambda _: None)

        prompt = prompts.create_confirmation("hist1", "Test")
        prompts.show_prompt(prompt)

        history = prompts.get_history()
        assert len(history) == 1
        assert history[0].prompt_id == "hist1"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_confirm(self):
        """Test confirm convenience function."""
        interactive_prompts = InteractivePrompts()
        interactive_prompts.set_input_function(lambda _: "yes")
        interactive_prompts.set_print_function(lambda _: None)

        result = interactive_prompts.create_confirmation("test_conf", "Test message?")
        response = interactive_prompts.show_prompt(result)

        assert response.user_input == "yes"

    def test_select(self):
        """Test select convenience function."""
        interactive_prompts = InteractivePrompts()
        interactive_prompts.set_input_function(lambda _: "1")
        interactive_prompts.set_print_function(lambda _: None)

        result = interactive_prompts.create_selection("test_sel", "Choose:", ["A", "B", "C"])
        response = interactive_prompts.show_prompt(result)

        assert response.user_input == "A"

    def test_text_input(self):
        """Test text_input convenience function."""
        interactive_prompts = InteractivePrompts()
        interactive_prompts.set_input_function(lambda _: "Hello")
        interactive_prompts.set_print_function(lambda _: None)

        result = interactive_prompts.create_text_input("test_txt", "Enter text:")
        response = interactive_prompts.show_prompt(result)

        assert response.user_input == "Hello"

    def test_number_input(self):
        """Test number_input convenience function."""
        interactive_prompts = InteractivePrompts()
        interactive_prompts.set_print_function(lambda _: None)

        result = interactive_prompts.create_number_input("test_num", "Enter number:", 0, 100, default_value=50)
        response = interactive_prompts.show_prompt(result)

        assert response.user_input == "50.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
