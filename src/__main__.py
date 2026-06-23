"""
Main entry point for IndoClaw AI OS.
"""

import sys
import os
import warnings
from pathlib import Path

# Suppress LangChain Pydantic compatibility warnings for Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater",
    category=UserWarning
)

# Try to import workspace config
try:
    from src.core.workspace import get_agent_config, ensure_agent_workspace
    WORKSPACE_AVAILABLE = True
except ImportError:
    WORKSPACE_AVAILABLE = False


def is_onboarded() -> bool:
    """
    Check if the user has run the onboard process.
    
    Returns:
        True if onboarded, False otherwise
    """
    if not WORKSPACE_AVAILABLE:
        return False
    
    try:
        from pathlib import Path
        
        # Check if workspaces folder exists
        workspaces_dir = Path.home() / "IndoClaw" / "workspaces"
        if not workspaces_dir.exists():
            return False
        
        # Check if default agent folder exists
        default_dir = workspaces_dir / "default"
        if not default_dir.exists():
            return False
        
        # Check if config file exists
        config_file = default_dir / "agent_config.json"
        if not config_file.exists():
            return False
        
        # Load config and check essential settings
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check if the config has essential settings
        essential_keys = ["llm_provider", "llm_model", "agent_name"]
        for key in essential_keys:
            if key not in config:
                return False
        
        # Check if ollama_enabled is set (this is a key indicator of being configured)
        if config.get("ollama_enabled") is None:
            return False
        
        return True
    except Exception:
        return False


def get_default_agent_name() -> str:
    """
    Get the default agent name ("default" if configured).
    
    Returns:
        Default agent name
    """
    if not WORKSPACE_AVAILABLE:
        return "default"
    
    try:
        from src.core.workspace.config import list_agents
        agents = list_agents()
        if "default" in agents:
            return "default"
        elif agents:
            return agents[0]
        else:
            return "default"
    except Exception:
        return "default"


def run_onboard() -> bool:
    """
    Run the onboard process for first-time setup.
    Creates the "default" agent configuration.
    
    Returns:
        True if successful, False otherwise
    """
    print("=" * 50)
    print("IndoClaw First-Time Setup")
    print("=" * 50)
    print()
    print("Welcome to IndoClaw! Let's configure your agent.")
    print()
    
    # Get agent name - must be "default" for initial setup
    agent_name = input("Enter agent name (default: default): ").strip()
    if not agent_name:
        agent_name = "default"
    
    print(f"\nConfiguring agent: '{agent_name}'")
    print()
    
    # Get LLM provider
    llm_provider = input("LLM Provider (ollama/openai, default: ollama): ").strip()
    if not llm_provider:
        llm_provider = "ollama"
    
    # Get LLM model
    llm_model = input(f"LLM Model (default: gemma4:26b for ollama): ").strip()
    if not llm_model:
        llm_model = "gemma4:26b"
    
    # Get LLM base URL
    llm_base_url = input("LLM Base URL (default: http://localhost:11434/v1): ").strip()
    if not llm_base_url:
        llm_base_url = "http://localhost:11434/v1"
    
    # Get API key
    llm_api_key = input("API Key (press Enter for none/ollama): ").strip() or None
    
    # Get default channel
    default_channel = input("Default channel (console/telegram, default: console): ").strip()
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
        
        print()
        print("=" * 50)
        print("Setup Complete!")
        print("=" * 50)
        print(f"Agent '{agent_name}' configured successfully!")
        print(f"Config saved to: {workspace_config.workspace_dir}")
        print(f"LLM Provider: {llm_provider}")
        print(f"LLM Model: {llm_model}")
        print()
        print("You can now run 'indoclaw' to start your agent.")
        print()
        
        return True
    except Exception as e:
        print(f"Setup failed: {e}")
        return False


def uninstall(full: bool = False) -> bool:
    """
    Uninstall IndoClaw files.
    
    Args:
        full: If True, also remove the ~/IndoClaw folder
    
    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path
    
    print("=" * 50)
    print("IndoClaw Uninstall")
    print("=" * 50)
    print()
    
    if full:
        indo_claw_dir = Path.home() / "IndoClaw"
        print(f"Removing entire IndoClaw folder: {indo_claw_dir}")
        
        if not indo_claw_dir.exists():
            print("IndoClaw folder not found. Nothing to remove.")
            return True
        
        try:
            import shutil
            shutil.rmtree(indo_claw_dir)
            print(f"Successfully removed {indo_claw_dir}")
            print()
            print("IndoClaw has been completely uninstalled.")
            return True
        except Exception as e:
            print(f"Error removing IndoClaw folder: {e}")
            return False
    else:
        # Remove workspace config files but keep the folder
        print("Removing agent configurations...")
        
        workspaces_dir = Path.home() / "IndoClaw" / "workspaces"
        
        if not workspaces_dir.exists():
            print("No agent configurations found.")
            return True
        
        try:
            import shutil
            # Remove all agent folders
            for item in workspaces_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                elif item.is_file():
                    item.unlink()
            
            print(f"Successfully removed agent configurations from {workspaces_dir}")
            print()
            print("IndoClaw has been uninstalled. Run 'indoclaw onboard' to reconfigure.")
            return True
        except Exception as e:
            print(f"Error removing agent configurations: {e}")
            return False


def main() -> None:
    """Main entry point."""
    import argparse
    from pathlib import Path
    
    # Parse arguments early to detect onboard command before agent initialization
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
        "--onboard",
        action="store_true",
        help="Run first-time setup wizard"
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
        help="Completely remove IndoClaw folder"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Uninstall IndoClaw (remove agent configurations)"
    )
    
    args, remaining = parser.parse_known_args()
    
    # Handle --help
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
        print("  -h, --help      Show help message")
        print("  --onboard       Run first-time setup wizard")
        print("  --setup [name]  Run setup wizard for agent configuration")
        print("  --full          Completely remove IndoClaw folder")
        print("  --uninstall     Uninstall IndoClaw (remove agent configurations)")
        print()
        print("commands:")
        print("  onboard     Run first-time setup wizard")
        print("  setup       Run setup wizard for agent configuration")
        print("  uninstall   Uninstall IndoClaw")
        print("  research    Run research on a topic")
        print("  write       Write content on a topic")
        print("  chat        Run in chat mode")
        return
    
    # Handle --full with --uninstall
    if args.uninstall:
        uninstall(full=args.full)
        return
    
    # Check if remaining args start with "uninstall"
    if remaining and remaining[0] == "uninstall":
        uninstall(full=args.full)
        return
    
    # Handle --onboard or "onboard" command (before any agent initialization)
    if args.onboard:
        run_onboard()
        return
    
    # Check if remaining args start with "onboard"
    if remaining and remaining[0] == "onboard":
        run_onboard()
        return
    
    # Handle --setup or "setup" command
    if args.setup is not None:
        from src.interfaces.cli import IndoClawCLI
        cli = IndoClawCLI(verbose=False)
        cli.setup_agent(args.setup)
        return
    
    if remaining and len(remaining) > 0 and remaining[0] == "setup":
        from src.interfaces.cli import IndoClawCLI
        cli = IndoClawCLI(verbose=False)
        cli.setup_agent(remaining[1] if len(remaining) > 1 else None)
        return
    
    # Check if onboarded (only after we've handled all setup-related commands)
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
        # Ask user if they want to run onboard
        user_input = input("Would you like to run the setup wizard now? (yes/no): ").strip().lower()
        if user_input in ["yes", "y"]:
            run_onboard()
            print()
            print("Agent configured successfully. Please run 'indoclaw' again to start.")
            sys.exit(0)
        else:
            print("\nThank you for using IndoClaw. Exiting...")
            sys.exit(0)
        return
    
    # Run the CLI with remaining arguments
    from src.interfaces.cli import main as cli_main
    if remaining:
        # Reconstruct sys.argv for CLI
        sys.argv = ["indoclaw"] + remaining
    cli_main()


if __name__ == "__main__":
    main()
