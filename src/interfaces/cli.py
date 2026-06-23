"""
Command-line interface for IndoClaw AI OS.
"""

import sys
import os
import argparse
import json
import warnings
from typing import Optional, Dict, Any

# Suppress LangChain Pydantic compatibility warnings for Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater",
    category=UserWarning
)

try:
    from prompt_toolkit import PromptSession, HTML
    from prompt_toolkit.styles import Style
    from prompt_toolkit import prompt
    from prompt_toolkit.validation import Validator
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.live import Live
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Try to import langchain-openai
try:
    from langchain_openai import ChatOpenAI
    try:
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage, AIMessage
    try:
        from langchain_core.prompts import PromptTemplate
    except ImportError:
        from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..core.agent import IndoClawAgent, create_agent
from ..agents.researcher import ResearcherAgent
from ..agents.writer import WriterAgent
from ..config.settings import settings
from ..core.tools.web_search import WebSearchTool
from ..core.tools.file_ops import FileOperationTool
from ..core.tools.calculation import CalculatorTool
from ..core.workspace import get_agent_config, ensure_agent_workspace


def input_with_validation(prompt_text: str, validator: Validator = None) -> str:
    """Get user input with optional validation."""
    if PROMPT_TOOLKIT_AVAILABLE and sys.stdin.isatty():
        try:
            if validator:
                return prompt(prompt_text, validator=validator)
            return prompt(prompt_text)
        except Exception:
            # Fall back to input if prompt_toolkit fails
            pass
    return input(prompt_text)


class IndoClawCLI:
    """Command-line interface for IndoClaw."""
    
    def __init__(self, verbose: bool = False, init_agent: bool = True, agent_name: str = None):
        self.verbose = verbose
        self.agent_name = agent_name or "default"
        
        # Initialize console
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Initialize agent (optional)
        self.agent = None
        self.agents = {}
        if init_agent:
            self._initialize_agent()
    
    def _print_logo(self) -> None:
        """Print the IndoClaw ASCII logo in green color."""
        logo = """
[bold green]██╗███╗   ██╗██████╗  ██████╗  ██████╗██╗      █████╗ ██╗    ██╗
██║████╗  ██║██╔══██╗██╔═══██╗██╔════╝██║     ██╔══██╗██║    ██║
██║██╔██╗ ██║██║  ██║██║   ██║██║     ██║     ███████║██║ █╗ ██║
██║██║╚██╗██║██║  ██║██║   ██║██║     ██║     ██╔══██║██║███╗██║
██║██║ ╚████║██████╔╝╚██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝
╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝[/bold green] 
               [bold green]                           [/bold green]      
        """
        if self.console:
            self.console.print(logo)
        else:
            # Fallback for non-Rich environments
            print(logo.replace("[bold green]", "").replace("[/bold green]", ""))
    
    def _initialize_agent(self) -> None:
        """Initialize the main agent."""
        try:
            from src.core.workspace.config import get_agent_config
            from src.config.settings import Settings, LLMConfig, AgentConfig, ToolConfig, MemoryConfig
            
            # Use self.agent_name directly (passed from __main__.py)
            agent_name = self.agent_name
            if not agent_name or agent_name == "default":
                # Fallback to default agent name from settings
                agent_name = settings.agent.name
            
            # Load agent-specific config
            if agent_name and agent_name != "default":
                config = get_agent_config(agent_name=agent_name).load()
                if config:
                    agent_name = config.get("agent_name", agent_name)
                    
                    # Reload settings with agent-specific config
                    llm_config = LLMConfig()
                    llm_config.model_name = config.get("llm_model", getattr(llm_config, 'model_name', None))
                    llm_config.base_url = config.get("llm_base_url", getattr(llm_config, 'base_url', None))
                    llm_config.api_key = config.get("llm_api_key", getattr(llm_config, 'api_key', None))
                    llm_config.ollama_enabled = config.get("ollama_enabled", getattr(llm_config, 'ollama_enabled', True))
                    
                    agent_config = AgentConfig()
                    agent_config.name = config.get("agent_name", getattr(agent_config, 'name', None))
                    agent_config.role = config.get("agent_role", getattr(agent_config, 'role', None))
                    agent_config.max_iterations = config.get("max_iterations", getattr(agent_config, 'max_iterations', 10))
                    agent_config.verbose = config.get("verbose", getattr(agent_config, 'verbose', True))
                    
                    tool_config = ToolConfig()
                    tool_config.show_tool_calling = config.get("show_tool_calling", getattr(tool_config, 'show_tool_calling', False))
                    tool_config.show_thinking = config.get("show_thinking", getattr(tool_config, 'show_thinking', False))
                    tool_config.thinking_enabled = config.get("thinking_enabled", getattr(tool_config, 'thinking_enabled', True))
                    
                    memory_config = MemoryConfig()
                    memory_config.short_term_capacity = config.get("short_term_capacity", getattr(memory_config, 'short_term_capacity', 10))
                    memory_config.long_term_top_k = config.get("long_term_top_k", getattr(memory_config, 'long_term_top_k', 5))
                    memory_config.embedding_model = config.get("embedding_model", getattr(memory_config, 'embedding_model', None))
                    
                    # Update global settings
                    settings.llm = llm_config
                    settings.agent = agent_config
                    settings.tool = tool_config
                    settings.memory = memory_config
            
            self.agent = create_agent(
                tools=None,  # Use default tools from settings
                verbose=self.verbose
            )
            self.agents["default"] = self.agent
            
            # Print logo and agent ready message
            self._print_logo()
            
            if self.console:
                self.console.print(
                    Panel.fit(
                        f"[bold green]{agent_name}[/bold green] initialized successfully!",
                        title="[bold]Agent Ready[/bold]",
                        border_style="green"
                    )
                )
            if self.verbose:
                print(f"Using default tools: {[tool.name for tool in self.agent.tools]}")
        except Exception as e:
            if self.console:
                self.console.print(
                    Panel.fit(
                        f"[bold red]Error initializing agent: {str(e)}[/bold red]\n"
                        "Please set OPENAI_API_KEY in your environment.",
                        title="[bold]Error[/bold]",
                        border_style="red"
                    )
                )
            else:
                print(f"Error: {e}")
    
    def print_header(self) -> None:
        """Print the header."""
        if self.console:
            self.console.print(
                Panel(
                    "[bold cyan]IndoClaw[/bold cyan] - Autonomous AI Agent OS\n"
                    "[dim]Type 'exit' or 'quit' to close[/dim]",
                    border_style="cyan"
                )
            )
        else:
            print("=" * 50)
            print("IndoClaw - Autonomous AI Agent OS")
            print("Type 'exit' or 'quit' to close")
            print("=" * 50)
    
    def print_response(self, response: str, title: str = "Response") -> None:
        """Print a response in a styled panel."""
        if self.console:
            self.console.print(
                Panel(
                    Markdown(response),
                    title=f"[bold]{title}[/bold]",
                    border_style="green"
                )
            )
        else:
            print(f"\n{title}:")
            print("-" * 50)
            print(response)
            print("-" * 50)
    
    def print_error(self, error: str) -> None:
        """Print an error message."""
        if self.console:
            self.console.print(
                Panel.fit(
                    f"[bold red]{error}[/bold red]",
                    title="[bold]Error[/bold]",
                    border_style="red"
                )
            )
        else:
            print(f"Error: {error}")
    
    def print_info(self, message: str) -> None:
        """Print an info message."""
        if self.console:
            self.console.print(
                Panel.fit(
                    f"[bold cyan]{message}[/bold cyan]",
                    title="[bold]Info[/bold]",
                    border_style="cyan"
                )
            )
        else:
            print(f"Info: {message}")
    
    def run_chat(self) -> None:
        """Run interactive chat mode."""
        self.print_header()
        
        if PROMPT_TOOLKIT_AVAILABLE and RICH_AVAILABLE:
            session = PromptSession()
            style = Style.from_dict({
                "prompt": "cyan bold",
                "message": "green",
            })
            
            while True:
                try:
                    user_input = session.prompt(
                        HTML("<prompt>> </prompt>"),
                        style=style
                    ).strip()
                except (KeyboardInterrupt, EOFError):
                    break
                
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                # Run agent
                try:
                    result = self.agent.run(user_input)
                    self.print_response(result.response)
                except Exception as e:
                    self.print_error(str(e))
        else:
            # Fallback without prompt_toolkit
            while True:
                try:
                    user_input = input(">> ").strip()
                except (KeyboardInterrupt, EOFError):
                    break
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                try:
                    result = self.agent.run(user_input)
                    self.print_response(result.response)
                except Exception as e:
                    self.print_error(str(e))
    
    def run_single(self, prompt: str) -> None:
        """Run a single prompt and exit."""
        try:
            result = self.agent.run(prompt)
            self.print_response(result.response)
        except Exception as e:
            self.print_error(str(e))
            sys.exit(1)
    
    def run_research(self, topic: str) -> None:
        """Run a research task."""
        try:
            agent = ResearcherAgent(verbose=self.verbose)
            result = agent.research(topic)
            
            if self.console:
                self.console.print(
                    Panel.fit(
                        f"[bold green]Research Complete[/bold green]\n\n"
                        f"Query: {result.query}\n"
                        f"Confidence: {result.confidence * 100:.1f}%\n\n"
                        f"[bold]Summary:[/bold]\n{result.summary}",
                        title="[bold]Research Result[/bold]",
                        border_style="green"
                    )
                )
                
                if result.sources:
                    self.console.print(
                        Panel(
                            "\n".join([f"- {s}" for s in result.sources]),
                            title="[bold]Sources[/bold]",
                            border_style="blue"
                        )
                    )
            else:
                print(f"Research complete: {result.summary}")
        except Exception as e:
            self.print_error(str(e))
    
    def run_write(self, topic: str, format: str = "article") -> None:
        """Run a writing task."""
        try:
            agent = WriterAgent(verbose=self.verbose)
            result = agent.write(topic, format=format)
            
            if self.console:
                self.console.print(
                    Panel.fit(
                        f"[bold green]Writing Complete[/bold green]\n\n"
                        f"Title: {result.title}\n"
                        f"Format: {result.format}\n"
                        f"Word Count: {result.word_count}\n\n"
                        f"[bold]Content:[/bold]\n{result.content}",
                        title="[bold]Writing Result[/bold]",
                        border_style="green"
                    )
                )
            else:
                print(f"Writing complete: {result.content[:200]}..")
        except Exception as e:
            self.print_error(str(e))
    
    def setup_agent(self, agent_name: str = None) -> None:
        """Run setup wizard for agent configuration."""
        self.print_header()
        
        if self.console:
            self.console.print(
                Panel(
                    "[bold cyan]Agent Setup Wizard[/bold cyan]\n"
                    "Configure your agent's settings.",
                    border_style="cyan"
                )
            )
        else:
            print("\n" + "=" * 50)
            print("Agent Setup Wizard")
            print("Configure your agent's settings.")
            print("=" * 50)
        
        # Get or prompt for agent name
        if not agent_name:
            agent_name = input_with_validation("Enter agent name (default: default): ").strip()
            if not agent_name:
                agent_name = "default"
        
        # Get LLM provider
        if self.console:
            self.console.print("\n[bold]LLM Provider Configuration[/bold]")
        
        llm_provider = input_with_validation("LLM Provider (ollama/openai, default: ollama): ").strip()
        if not llm_provider:
            llm_provider = "ollama"
        
        # Get LLM model
        llm_model = input_with_validation(f"LLM Model (default: gemma4:26b for ollama): ").strip()
        if not llm_model:
            llm_model = "gemma4:26b"
        
        # Get LLM base URL
        llm_base_url = input_with_validation("LLM Base URL (default: http://localhost:11434/v1): ").strip()
        if not llm_base_url:
            llm_base_url = "http://localhost:11434/v1"
        
        # Get API key
        llm_api_key = input_with_validation("API Key (press Enter for none/ollama): ").strip() or None
        
        # Get default channel
        default_channel = input_with_validation("Default channel (console/telegram, default: console): ").strip()
        if not default_channel:
            default_channel = "console"
        
        # Build config
        config = {
            "agent_name": agent_name,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "llm_base_url": llm_base_url,
            "llm_api_key": llm_api_key,
            "default_channel": default_channel,
            "max_iterations": 10,
            "verbose": True,
            "thinking_enabled": True,
            "show_tool_calling": False,
            "show_thinking": False,
            "short_term_capacity": 10,
            "long_term_top_k": 5,
            "embedding_model": "text-embedding-3-small",
            "ollama_enabled": llm_provider == "ollama"
        }
        
        # Save config for this agent
        workspace_config = get_agent_config(agent_name=agent_name)
        workspace_config.save(config)
        
        # Ensure workspace files exist
        ensure_agent_workspace(agent_name)
        
        if self.console:
            self.console.print(
                Panel.fit(
                    f"[bold green]Agent '{agent_name}' configured successfully![/bold green]\n\n"
                    f"Config saved to: {workspace_config.workspace_dir}\n"
                    f"LLM Provider: {llm_provider}\n"
                    f"LLM Model: {llm_model}",
                    title="[bold]Setup Complete[/bold]",
                    border_style="green"
                )
            )
        else:
            print(f"\nAgent '{agent_name}' configured successfully!")
            print(f"Config saved to: {workspace_config.workspace_dir}")
            print(f"LLM Provider: {llm_provider}")
            print(f"LLM Model: {llm_model}")
    
    def run(self, prompt: str = None, chat: bool = True) -> None:
        """Run the CLI."""
        if prompt:
            self.run_single(prompt)
        elif chat:
            self.run_chat()
        else:
            self.print_header()
            self.run_chat()


def main() -> None:
    """Main entry point."""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(
        description="IndoClaw - Autonomous AI Agent OS",
        add_help=False
    )
    parser.add_argument(
        "--help", "-h",
        action="store_true",
        help="Show help message"
    )
    parser.add_argument(
        "-r", "--research",
        help="Run research on a topic"
    )
    parser.add_argument(
        "-w", "--write",
        help="Write content on a topic"
    )
    parser.add_argument(
        "-f", "--format",
        default="article",
        help="Output format for writing (default: article)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--chat", "-c",
        action="store_true",
        help="Force chat mode"
    )
    parser.add_argument(
        "--setup",
        nargs="?",
        const="default",
        metavar="AGENT_NAME",
        help="Run setup wizard for agent configuration"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Completely remove IndoClaw folder (when used with uninstall)"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check if agent is configured (for internal use)"
    )
    
    args, remaining = parser.parse_known_args()
    
    if args.help:
        print("usage: indoclaw [-h] [--onboard] [command] [prompt]")
        print()
        print("IndoClaw - Autonomous AI Agent OS")
        print()
        print("positional arguments:")
        print("  command    Command to run (onboard, research, write, or chat)")
        print("  prompt     Prompt to process (if not provided, runs in chat mode)")
        print()
        print("optional arguments:")
        print("  -h, --help  Show help message")
        print("  --onboard   Run first-time setup wizard")
        print()
        print("commands:")
        print("  onboard     Run first-time setup wizard")
        print("  research    Run research on a topic")
        print("  write       Write content on a topic")
        print("  chat        Run in chat mode")
        return
    
    # Check if agent is configured (before initializing CLI)
    if not args.check_config:
        try:
            from src.__main__ import is_onboarded
            if not is_onboarded():
                print()
                print("=" * 60)
                print("  IndoClaw has not been configured yet.")
                print("=" * 60)
                print()
                print("Please run 'indoclaw onboard' to configure your agent.")
                print()
                print("Available commands:")
                print("  onboard     Run first-time setup wizard")
                print("  uninstall   Uninstall IndoClaw")
                print("  setup [name]  Run setup wizard for specific agent")
                print()
                sys.exit(1)
        except Exception as e:
            pass
    
    # Parse remaining args for command
    prompt = None  # Default prompt value
    command = None  # Default command value
    agent_name = None  # Agent name (if specified)
    
    # Get default agent name if not specified
    from src.__main__ import get_default_agent_name
    if not agent_name:
        agent_name = get_default_agent_name()
    
    if remaining:
        command = remaining[0] if remaining else None
        prompt = remaining[1] if len(remaining) > 1 else None
        
        if command == "uninstall":
            from ..__main__ import uninstall
            uninstall(full=args.full if hasattr(args, 'full') else False)
        elif command == "onboard":
            run_onboard_cli()
        elif command == "setup":
            cli = IndoClawCLI(verbose=args.verbose, init_agent=False, agent_name=agent_name)
            cli.setup_agent(args.setup)
        elif command == "research":
            cli = IndoClawCLI(verbose=args.verbose, init_agent=False, agent_name=agent_name)
            cli.run_research(prompt)
        elif command == "write":
            cli = IndoClawCLI(verbose=args.verbose, init_agent=False, agent_name=agent_name)
            cli.run_write(prompt, args.format)
        elif command == "chat":
            cli = IndoClawCLI(verbose=args.verbose, init_agent=False, agent_name=agent_name)
            cli.run(chat=True)
        else:
            cli = IndoClawCLI(verbose=args.verbose, init_agent=True, agent_name=agent_name)
            cli.run(prompt=command if command else prompt, chat=not args.research and not args.write)
    else:
        cli = IndoClawCLI(verbose=args.verbose, init_agent=True, agent_name=agent_name)
        cli.run(prompt=prompt, chat=not args.research and not args.write)


def run_onboard_cli() -> None:
    """Run the onboard process for first-time setup."""
    from src.core.workspace import get_agent_config, ensure_agent_workspace
    from ..interfaces.cli import input_with_validation
    
    print("=" * 50)
    print("IndoClaw First-Time Setup")
    print("=" * 50)
    print()
    print("Welcome to IndoClaw! Let's configure your agent.")
    print()
    
    # Get agent name
    agent_name = input_with_validation("Enter agent name (default: default): ").strip()
    if not agent_name:
        agent_name = "default"
    
    # Get LLM provider
    llm_provider = input_with_validation("LLM Provider (ollama/openai, default: ollama): ").strip()
    if not llm_provider:
        llm_provider = "ollama"
    
    # Get LLM model
    llm_model = input_with_validation(f"LLM Model (default: gemma4:26b for ollama): ").strip()
    if not llm_model:
        llm_model = "gemma4:26b"
    
    # Get LLM base URL
    llm_base_url = input_with_validation("LLM Base URL (default: http://localhost:11434/v1): ").strip()
    if not llm_base_url:
        llm_base_url = "http://localhost:11434/v1"
    
    # Get API key
    llm_api_key = input_with_validation("API Key (press Enter for none/ollama): ").strip() or None
    
    # Get default channel
    default_channel = input_with_validation("Default channel (console/telegram, default: console): ").strip()
    if not default_channel:
        default_channel = "console"
    
    # Build config
    config = {
        "agent_name": agent_name,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "llm_base_url": llm_base_url,
        "llm_api_key": llm_api_key,
        "default_channel": default_channel,
        "max_iterations": 10,
        "verbose": True,
        "thinking_enabled": True,
        "show_tool_calling": False,
        "show_thinking": False,
        "short_term_capacity": 10,
        "long_term_top_k": 5,
        "embedding_model": "text-embedding-3-small",
        "ollama_enabled": llm_provider == "ollama"
    }
    
    # Save config
    try:
        workspace_config = get_agent_config(agent_name=agent_name)
        workspace_config.save(config)
        
        # Ensure workspace files exist
        ensure_agent_workspace(agent_name)
        
        print()
        print("=" * 50)
        print("Setup Complete!")
        print("=" * 50)
        print(f"Agent '{agent_name}' configured successfully!")
        print(f"Config saved to: {workspace_config.workspace_dir}")
        print(f"LLM Provider: {llm_provider}")
        print(f"LLM Model: {llm_model}")
        print()
    except Exception as e:
        print(f"Setup failed: {e}")


if __name__ == "__main__":
    main()
