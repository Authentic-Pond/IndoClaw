"""
Command compiler for IndoClaw CLI.
Parses command line arguments to identify commands, options, and prompts.
"""

import sys
from typing import Dict, Any, List, Optional


class CommandParser:
    """Parse command line arguments for IndoClaw."""
    
    # Known commands
    COMMANDS = {"agent", "onboard", "setup", "research", "write", "chat", "uninstall", "reset"}
    
    # Options that take values (short and long forms)
    OPTIONS_WITH_VALUE = {"-a", "--agent", "-f", "--format"}
    
    # Options without values
    FLAG_OPTIONS = {"-h", "--help", "-v", "--verbose", "--full"}
    
    def __init__(self, args: List[str]):
        """
        Initialize parser with arguments.
        
        Args:
            args: Command line arguments (sys.argv[1:])
        """
        self.args = args
        self.result: Dict[str, Any] = {
            "command": None,
            "agent_name": None,
            "prompt": None,
            "options": {},
            "help": False,
            "verbose": False,
            "format": None
        }
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse command line arguments.
        
        Returns:
            Dict with parsed command, options, and prompt
            
        Raises:
            ValueError: If parsing fails
        """
        if not self.args:
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
            
            # Options with values
            if arg in self.OPTIONS_WITH_VALUE:
                if i + 1 < len(self.args):
                    next_arg = self.args[i + 1]
                    # Check if it's actually a prompt in quotes
                    if self._is_quoted_string(next_arg):
                        # This is a prompt, not a value for this option
                        pass
                    elif arg in ("-a", "--agent"):
                        self.result["agent_name"] = next_arg
                    elif arg in ("-f", "--format"):
                        self.result["format"] = next_arg
                    else:
                        self.result["options"][arg] = next_arg
                    i += 2
                    continue
                else:
                    raise ValueError(f"Error: '{arg}' requires a value")
            
            # Known commands
            if arg in self.COMMANDS:
                self.result["command"] = arg
                i += 1
                
                # For 'agent' command, next arg might be agent name
                if arg == "agent" and i < len(self.args):
                    next_arg = self.args[i]
                    # If next arg is not a quoted string, it's likely an agent name
                    if not self._is_quoted_string(next_arg) and not next_arg.startswith("-"):
                        self.result["agent_name"] = next_arg
                        i += 1
                continue
            
            # Options with -- prefix
            if arg.startswith("--") and "=" in arg:
                # Handle --option=value format
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
                i += 1
                continue
            
            # Check if arg is a quoted string (prompt)
            if self._is_quoted_string(arg):
                if self.result["prompt"] is None:
                    self.result["prompt"] = arg
                else:
                    self.result["prompt"] += " " + arg
            elif self.result["command"] is None and self.result["agent_name"] is None:
                # Unquoted arg before any command - this is an error
                raise ValueError(f"Error: Invalid command '{arg}'")
            else:
                # After command or agent_name - treat as prompt
                if self.result["prompt"] is None:
                    self.result["prompt"] = arg
                else:
                    self.result["prompt"] += " " + arg
            
            i += 1
        
        return self.result
    
    def _is_quoted_string(self, s: str) -> bool:
        """Check if string is quoted."""
        return (s.startswith('"') and s.endswith('"')) or \
               (s.startswith("'") and s.endswith("'"))


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
    help_text = """usage: indoclaw [-h] [--onboard] [command] [prompt]

IndoClaw - Autonomous AI Agent OS

positional arguments:
  command    Command to run (onboard, research, write, or chat)
  prompt     Prompt to process (if not provided, runs in chat mode)

optional arguments:
  -h, --help      Show help message
  --onboard       Run first-time setup wizard
  --setup [name]  Run setup wizard for agent configuration
  --agent [name]  Run with specified agent (default: default)
  --full          Completely remove IndoClaw folder
  --uninstall     Uninstall IndoClaw (remove agent configurations)
  --verbose       Enable verbose output
  --format        Output format for writing (default: article)

commands:
  agent [name]    Run with specified agent
  onboard         Run first-time setup wizard
  setup           Run setup wizard for agent configuration
  reset           Remove .indoclaw folder (reset all configurations)
  uninstall       Remove agent configurations (keep .indoclaw folder)
  uninstall --full Remove .indoclaw folder (complete uninstall)
  research        Run research on a topic
  write           Write content on a topic
  chat            Run in chat mode

note: prompts should be enclosed in quotes
  example: indoclaw agent Serene "hello how are you"
"""
    print(help_text)