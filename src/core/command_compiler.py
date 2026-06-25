"""
Command compiler for IndoClaw CLI.
Parses command line arguments to identify commands, options, and prompts.
"""

import sys
from typing import Dict, Any, List, Optional


class CommandParser:
    """Parse command line arguments for IndoClaw."""

    # Primary commands
    COMMANDS = {
        "agent", "onboard", "setup", "research", "write",
        "chat", "uninstall", "reset", "list-tools", "list-agents"
    }

    # Secondary commands (after 'agent')
    AGENT_COMMANDS = {"research", "write", "chat"}

    # Options that take values (short and long forms)
    OPTIONS_WITH_VALUE = {"-a", "--agent", "-f", "--format"}

    # Flag options without values
    FLAG_OPTIONS = {"-h", "--help", "-v", "--verbose", "--full", "--trace", "--chat", "--install"}

    # Phase 2-4 info commands
    INFO_COMMANDS = {"list-tools", "list-agents"}

    def __init__(self, args: List[str]):
        """
        Initialize parser with arguments.

        Args:
            args: Command line arguments (sys.argv[1:])
        """
        self.args = args
        self.result: Dict[str, Any] = {
            "command": None,
            "subcommand": None,
            "agent_name": None,
            "prompt": None,
            "options": {},
            "help": False,
            "verbose": False,
            "format": None,
            "trace": False,
        }

    def parse(self) -> Dict[str, Any]:
        """
        Parse command line arguments.

        Returns:
            Dict with parsed command, options, and prompt
        """
        if not self.args:
            # Default to interactive chat mode
            self.result["command"] = "agent"
            self.result["subcommand"] = "chat"
            return self.result

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            # Help flag
            if arg in ("-h", "--help"):
                self.result["help"] = True
                i += 1
                continue

            # Verbose flag
            if arg in ("-v", "--verbose"):
                self.result["verbose"] = True
                i += 1
                continue

            # Trace flag (Phase 4)
            if arg == "--trace":
                self.result["trace"] = True
                i += 1
                continue

            # Options with values
            if arg in self.OPTIONS_WITH_VALUE:
                if i + 1 < len(self.args):
                    next_arg = self.args[i + 1]
                    if arg in ("-a", "--agent"):
                        self.result["agent_name"] = next_arg
                    elif arg in ("-f", "--format"):
                        self.result["format"] = next_arg
                    else:
                        self.result["options"][arg] = next_arg
                    i += 2
                    continue
                else:
                    raise ValueError(f"Error: '{arg}' requires a value")

            # Known primary commands
            if arg in self.COMMANDS:
                # Handle info commands (Phase 2-4)
                if arg in self.INFO_COMMANDS:
                    self.result["command"] = arg
                    i += 1
                    continue

                self.result["command"] = arg
                i += 1

                # For 'agent' command, check for subcommand or agent name
                if arg == "agent" and i < len(self.args):
                    next_arg = self.args[i]
                    # Check if next arg is a subcommand or agent name
                    if next_arg in self.AGENT_COMMANDS:
                        self.result["subcommand"] = next_arg
                        i += 1
                    elif not next_arg.startswith("-") and not self._is_quoted_string(next_arg):
                        # It's an agent name
                        self.result["agent_name"] = next_arg
                        i += 1
                continue

            # Options with -- prefix and = format
            if arg.startswith("--") and "=" in arg:
                key, value = arg.split("=", 1)
                if key in self.OPTIONS_WITH_VALUE:
                    self.result["options"][key] = value
                i += 1
                continue

            # Flag options with -- prefix
            if arg.startswith("--") and arg in self.FLAG_OPTIONS:
                if arg == "--help":
                    self.result["help"] = True
                elif arg == "--verbose":
                    self.result["verbose"] = True
                elif arg == "--full":
                    self.result["options"]["--full"] = True
                elif arg == "--trace":
                    self.result["trace"] = True
                i += 1
                continue

            # quoted strings (prompts)
            if self._is_quoted_string(arg):
                if self.result["prompt"] is None:
                    self.result["prompt"] = arg
                else:
                    self.result["prompt"] += " " + arg
                i += 1
                continue

            # Unquoted arg - could be a prompt or unknown command
            if self.result["command"] is None:
                # Before any command - try to find the best match
                # If it looks like a prompt (not a known command), treat as prompt
                if not self._is_similar_to_command(arg):
                    if self.result["prompt"] is None:
                        self.result["prompt"] = arg
                    else:
                        self.result["prompt"] += " " + arg
                else:
                    raise ValueError(f"Error: Invalid command '{arg}'")
            else:
                # After command - treat as prompt or agent name
                if self.result["agent_name"] is None and self.result["subcommand"] is None:
                    # Check if it looks like an agent name (not a subcommand)
                    if arg not in self.AGENT_COMMANDS:
                        self.result["agent_name"] = arg
                    else:
                        self.result["subcommand"] = arg
                elif self.result["prompt"] is None:
                    self.result["prompt"] = arg
                else:
                    self.result["prompt"] += " " + arg

            i += 1

        return self.result

    def _is_quoted_string(self, s: str) -> bool:
        """Check if string is quoted."""
        return (s.startswith('"') and s.endswith('"')) or \
               (s.startswith("'") and s.endswith("'"))

    def _is_similar_to_command(self, s: str) -> bool:
        """Check if string looks like a command."""
        # Simple check - if it's short and starts with a letter, might be a command
        return len(s) <= 20 and s.isalpha()


def parse_command_line(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Parse command line arguments.

    Args:
        args: Command line arguments (sys.argv[1:] if None)

    Returns:
        Dict with parsed command, options, and prompt
    """
    if args is None:
        args = sys.argv[1:]

    parser = CommandParser(args)
    return parser.parse()


def print_help() -> None:
    """Print the help message."""
    help_text = """usage: indoclaw [-h] [--verbose] [command] [options] [prompt]

IndoClaw - Autonomous AI Agent OS

Commands:
  agent [name] [chat|research|write] [prompt]
    Run with specified agent (default: default), optionally with subcommand
  research <topic>
    Run research on a topic
  write <topic> [--format <format>]
    Write content on a topic
  chat
    Run in interactive chat mode
  onboard
    Run first-time setup wizard
  setup [name]
    Run setup wizard for agent configuration
  list-tools
    List all registered tools (Phase 2)
  list-agents
    List all registered agents (Phase 3)
  uninstall [--full]
    Uninstall IndoClaw (remove configurations or full install)

Options:
  -a, --agent <name>   Run with specified agent
  -f, --format <fmt>   Output format for writing (default: article)
  -v, --verbose        Enable verbose output
  --trace              Enable thought tracing (Phase 4)
  --install            Auto-install IndoClaw with dependencies
  -h, --help           Show this help message

Examples:
  indoclaw agent
  indoclaw agent Serene "hello how are you"
  indoclaw agent researcher "Research quantum computing"
  indoclaw write "AI trends" --format markdown
  indoclaw research "Latest AI developments"
  indoclaw list-tools
  indoclaw list-agents

Installation:
  indoclaw --install   Auto-install to venv and show PATH instructions
  ./install.sh         Run the shell installer script
"""
    print(help_text)
