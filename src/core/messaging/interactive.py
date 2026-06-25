"""
Interactive prompts for agent-user interaction (Phase 5.3).
Provides pause points where agents can wait for user input during execution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime


class PromptType(Enum):
    """Types of interactive prompts."""
    CONFIRMATION = "confirmation"      # Yes/No question
    SELECTION = "selection"            # Choose from options
    TEXT_INPUT = "text_input"          # Free text input
    NUMBER_INPUT = "number_input"      # Numeric input
    MULTI_SELECT = "multi_select"      # Multiple options


@dataclass
class InteractivePrompt:
    """
    An interactive prompt that can be shown to users during agent execution.

    Attributes:
        prompt_id: Unique identifier for this prompt
        message: The message to display to the user
        prompt_type: Type of prompt (confirmation, selection, etc.)
        options: Available options for selection prompts
        default_value: Default value if user provides no input
        validation: Optional function to validate user input
        error_message: Message to show if validation fails
        timeout: Optional timeout in seconds
    """

    prompt_id: str
    message: str
    prompt_type: PromptType = PromptType.CONFIRMATION
    options: List[str] = field(default_factory=list)
    default_value: Optional[str] = None
    validation: Optional[Callable[[str], bool]] = None
    error_message: str = "Invalid input. Please try again."
    timeout: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prompt_id": self.prompt_id,
            "message": self.message,
            "prompt_type": self.prompt_type.value,
            "options": self.options,
            "default_value": self.default_value,
            "timeout": self.timeout,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InteractivePrompt":
        """Create prompt from dictionary."""
        prompt_type = PromptType(data.get("prompt_type", "confirmation"))
        return cls(
            prompt_id=data.get("prompt_id", ""),
            message=data.get("message", ""),
            prompt_type=prompt_type,
            options=data.get("options", []),
            default_value=data.get("default_value"),
            timeout=data.get("timeout"),
        )


@dataclass
class PromptResponse:
    """Response from an interactive prompt."""
    prompt_id: str
    user_input: str
    timestamp: datetime = field(default_factory=datetime.now)
    cancelled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prompt_id": self.prompt_id,
            "user_input": self.user_input,
            "timestamp": self.timestamp.isoformat(),
            "cancelled": self.cancelled,
        }


class InteractivePrompts:
    """
    Manages interactive prompts during agent execution.

    Features:
    - Confirmation prompts (yes/no)
    - Selection prompts (choose from options)
    - Text input prompts
    - Number input prompts
    - Validation and error handling
    """

    def __init__(self):
        self.history: List[PromptResponse] = []
        self.active_prompts: Dict[str, InteractivePrompt] = {}
        self._input_function: Optional[Callable[[str], str]] = None
        self._print_function: Optional[Callable[[str], None]] = None

    def set_input_function(self, func: Callable[[str], str]) -> None:
        """Set a custom input function (useful for testing)."""
        self._input_function = func

    def set_print_function(self, func: Callable[[str], None]) -> None:
        """Set a custom print function (useful for testing)."""
        self._print_function = func

    def _print(self, message: str) -> None:
        """Print a message using configured or default function."""
        if self._print_function:
            self._print_function(message)
        else:
            print(message)

    def _get_input(self, prompt: str) -> str:
        """Get user input using configured or default function."""
        if self._input_function:
            return self._input_function(prompt)
        return input(prompt)

    def show_prompt(self, prompt: InteractivePrompt) -> PromptResponse:
        """
        Show an interactive prompt to the user and get their response.

        Args:
            prompt: The InteractivePrompt to display

        Returns:
            PromptResponse with the user's input
        """
        self.active_prompts[prompt.prompt_id] = prompt

        self._print("\n" + "=" * 60)
        self._print(f"[INTERACTIVE PROMPT: {prompt.prompt_id}]")
        self._print("=" * 60)
        self._print(prompt.message)

        # Handle different prompt types
        if prompt.prompt_type == PromptType.CONFIRMATION:
            response = self._handle_confirmation(prompt)
        elif prompt.prompt_type == PromptType.SELECTION:
            response = self._handle_selection(prompt)
        elif prompt.prompt_type == PromptType.MULTI_SELECT:
            response = self._handle_multi_select(prompt)
        elif prompt.prompt_type == PromptType.TEXT_INPUT:
            response = self._handle_text_input(prompt)
        elif prompt.prompt_type == PromptType.NUMBER_INPUT:
            response = self._handle_number_input(prompt)
        else:
            # Default to text input
            response = self._handle_text_input(prompt)

        self.history.append(response)
        if prompt.prompt_id in self.active_prompts:
            del self.active_prompts[prompt.prompt_id]

        return response

    def _handle_confirmation(self, prompt: InteractivePrompt) -> PromptResponse:
        """Handle yes/no confirmation prompt."""
        options_str = "/".join(prompt.options) if prompt.options else "[y/n]"

        while True:
            user_input = self._get_input(f"{options_str} ").strip().lower()

            if not user_input and prompt.default_value is not None:
                user_input = prompt.default_value.lower()

            if user_input in ("y", "yes", "true", "1"):
                return PromptResponse(
                    prompt_id=prompt.prompt_id,
                    user_input="yes",
                )
            elif user_input in ("n", "no", "false", "0"):
                return PromptResponse(
                    prompt_id=prompt.prompt_id,
                    user_input="no",
                )
            else:
                self._print(prompt.error_message)

    def _handle_selection(self, prompt: InteractivePrompt) -> PromptResponse:
        """Handle single selection prompt."""
        self._print("\nOptions:")
        for i, option in enumerate(prompt.options, 1):
            self._print(f"  {i}. {option}")

        while True:
            user_input = self._get_input("Enter choice (or q to quit): ").strip()

            if not user_input and prompt.default_value is not None:
                user_input = prompt.default_value

            if user_input.lower() == "q":
                return PromptResponse(
                    prompt_id=prompt.prompt_id,
                    user_input="",
                    cancelled=True,
                )

            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(prompt.options):
                    return PromptResponse(
                        prompt_id=prompt.prompt_id,
                        user_input=prompt.options[idx],
                    )
            except ValueError:
                pass

            # Check if input matches an option directly
            if user_input in prompt.options:
                return PromptResponse(
                    prompt_id=prompt.prompt_id,
                    user_input=user_input,
                )

            self._print(prompt.error_message)

    def _handle_multi_select(self, prompt: InteractivePrompt) -> PromptResponse:
        """Handle multiple selection prompt."""
        # If default value is provided, use it directly
        if prompt.default_value is not None:
            try:
                indices = [int(x.strip()) - 1 for x in prompt.default_value.split(",")]
                selected = [prompt.options[i] for i in indices if 0 <= i < len(prompt.options)]
                if selected:
                    return PromptResponse(
                        prompt_id=prompt.prompt_id,
                        user_input=",".join(selected),
                    )
            except (ValueError, IndexError):
                pass

        self._print("\nOptions (comma-separated):")
        for i, option in enumerate(prompt.options, 1):
            self._print(f"  {i}. {option}")

        while True:
            user_input = self._get_input("Enter choices (e.g., 1,3,5 or q to quit): ").strip()

            if user_input.lower() == "q":
                return PromptResponse(
                    prompt_id=prompt.prompt_id,
                    user_input="",
                    cancelled=True,
                )

            try:
                indices = [int(x.strip()) - 1 for x in user_input.split(",")]
                selected = [prompt.options[i] for i in indices if 0 <= i < len(prompt.options)]

                if selected:
                    return PromptResponse(
                        prompt_id=prompt.prompt_id,
                        user_input=",".join(selected),
                    )
            except (ValueError, IndexError):
                pass

            self._print(prompt.error_message)

    def _handle_text_input(self, prompt: InteractivePrompt) -> PromptResponse:
        """Handle free text input prompt."""
        default_str = f" [default: {prompt.default_value}]" if prompt.default_value else ""
        user_input = self._get_input(f"{default_str} ").strip()

        if not user_input and prompt.default_value is not None:
            user_input = prompt.default_value

        # Validate if validation function provided
        if prompt.validation and not prompt.validation(user_input):
            self._print(prompt.error_message)
            return self._handle_text_input(prompt)

        return PromptResponse(
            prompt_id=prompt.prompt_id,
            user_input=user_input,
        )

    def _handle_number_input(self, prompt: InteractivePrompt) -> PromptResponse:
        """Handle numeric input prompt."""
        # If default value is provided, use it directly
        if prompt.default_value is not None:
            try:
                value = float(prompt.default_value)
                return PromptResponse(
                    prompt_id=prompt.prompt_id,
                    user_input=str(value),
                )
            except ValueError:
                pass

        # Default range
        min_val = prompt.options[0] if len(prompt.options) > 0 else 0
        max_val = prompt.options[1] if len(prompt.options) > 1 else 100

        while True:
            user_input = self._get_input("Enter a number: ").strip()

            try:
                value = float(user_input)
                if min_val <= value <= max_val:
                    return PromptResponse(
                        prompt_id=prompt.prompt_id,
                        user_input=str(value),
                    )
                else:
                    self._print(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                self._print(prompt.error_message)

    def create_confirmation(
        self,
        prompt_id: str,
        message: str,
        default_yes: bool = True,
    ) -> InteractivePrompt:
        """Create a confirmation prompt."""
        default = "y" if default_yes else "n"
        return InteractivePrompt(
            prompt_id=prompt_id,
            message=message,
            prompt_type=PromptType.CONFIRMATION,
            default_value=default,
        )

    def create_selection(
        self,
        prompt_id: str,
        message: str,
        options: List[str],
        default_index: int = 0,
    ) -> InteractivePrompt:
        """Create a selection prompt."""
        default = options[default_index] if options else None
        return InteractivePrompt(
            prompt_id=prompt_id,
            message=message,
            prompt_type=PromptType.SELECTION,
            options=options,
            default_value=default,
        )

    def create_multi_select(
        self,
        prompt_id: str,
        message: str,
        options: List[str],
        default_indices: List[int] = None,
    ) -> InteractivePrompt:
        """Create a multi-select prompt."""
        default = ",".join(str(i + 1) for i in (default_indices or [0])) if options else None
        return InteractivePrompt(
            prompt_id=prompt_id,
            message=message,
            prompt_type=PromptType.MULTI_SELECT,
            options=options,
            default_value=default,
        )

    def create_text_input(
        self,
        prompt_id: str,
        message: str,
        default_value: str = None,
        validation: Callable[[str], bool] = None,
    ) -> InteractivePrompt:
        """Create a text input prompt."""
        return InteractivePrompt(
            prompt_id=prompt_id,
            message=message,
            prompt_type=PromptType.TEXT_INPUT,
            default_value=default_value,
            validation=validation,
        )

    def create_number_input(
        self,
        prompt_id: str,
        message: str,
        min_val: float = 0,
        max_val: float = 100,
        default_value: float = None,
    ) -> InteractivePrompt:
        """Create a number input prompt."""
        options = [min_val, max_val]
        default = str(default_value) if default_value is not None else None
        return InteractivePrompt(
            prompt_id=prompt_id,
            message=message,
            prompt_type=PromptType.NUMBER_INPUT,
            options=options,
            default_value=default,
        )

    def clear_history(self) -> None:
        """Clear prompt history."""
        self.history = []

    def get_history(self) -> List[PromptResponse]:
        """Get prompt history."""
        return self.history.copy()


# Convenience function for quick prompts
interactive_prompts = InteractivePrompts()


def confirm(prompt_id: str, message: str, default_yes: bool = True) -> bool:
    """Quick confirmation prompt. Returns True if confirmed."""
    prompt = interactive_prompts.create_confirmation(prompt_id, message, default_yes)
    response = interactive_prompts.show_prompt(prompt)
    return response.user_input.lower() == "yes"


def select(
    prompt_id: str,
    message: str,
    options: List[str],
    default_index: int = 0,
) -> Optional[str]:
    """Quick selection prompt. Returns selected option or None."""
    prompt = interactive_prompts.create_selection(
        prompt_id, message, options, default_index
    )
    response = interactive_prompts.show_prompt(prompt)
    return response.user_input if response.user_input else None


def text_input(
    prompt_id: str,
    message: str,
    default_value: str = None,
    validation: Callable[[str], bool] = None,
) -> Optional[str]:
    """Quick text input prompt. Returns user input or None."""
    prompt = interactive_prompts.create_text_input(
        prompt_id, message, default_value, validation
    )
    response = interactive_prompts.show_prompt(prompt)
    return response.user_input if response.user_input else None


def number_input(
    prompt_id: str,
    message: str,
    min_val: float = 0,
    max_val: float = 100,
    default_value: float = None,
) -> Optional[float]:
    """Quick number input prompt. Returns number or None."""
    prompt = interactive_prompts.create_number_input(
        prompt_id, message, min_val, max_val, default_value
    )
    response = interactive_prompts.show_prompt(prompt)
    try:
        return float(response.user_input) if response.user_input else None
    except ValueError:
        return None
