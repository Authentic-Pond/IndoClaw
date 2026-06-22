"""
Command-line interface for IndoClaw AI OS.
"""

import sys
import os
import argparse
import json
import warnings
from typing import Optional

# Suppress LangChain Pydantic compatibility warnings for Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater",
    category=UserWarning
)

try:
    from prompt_toolkit import PromptSession, HTML
    from prompt_toolkit.styles import Style
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


class IndoClawCLI:
    """Command-line interface for IndoClaw."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        
        # Initialize console
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Initialize agent
        self.agent = None
        self.agents = {}
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize the main agent."""
        try:
            self.agent = create_agent(
                tools=None,  # Use default tools from settings
                verbose=self.verbose
            )
            self.agents["default"] = self.agent
            if self.console:
                self.console.print(
                    Panel.fit(
                        "[bold green]IndoClaw[/bold green] initialized successfully!",
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
    parser = argparse.ArgumentParser(
        description="IndoClaw - Autonomous AI Agent OS"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to process (if not provided, runs in chat mode)"
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
    
    args = parser.parse_args()
    
    cli = IndoClawCLI(verbose=args.verbose)
    
    if args.research:
        cli.run_research(args.research)
    elif args.write:
        cli.run_write(args.write, args.format)
    else:
        cli.run(prompt=args.prompt, chat=not args.research and not args.write)


if __name__ == "__main__":
    main()