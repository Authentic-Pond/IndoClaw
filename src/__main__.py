"""
Main entry point for IndoClaw AI OS.
"""

import sys
import os
import warnings
from pathlib import Path

# Suppress ONNX Runtime warnings before any imports
os.environ["ORT_LOG_LEVEL"] = "OFF"
os.environ["ONNXRUNTIME_LOG_VERBOSITY_LEVEL"] = "0"

# Suppress LangChain Pydantic compatibility warnings for Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater",
    category=UserWarning
)

# Suppress ONNX Runtime GPU detection warnings (device discovery issues)
warnings.filterwarnings(
    "ignore",
    message=".*Failed to detect devices under.*",
    category=UserWarning
)
warnings.filterwarnings(
    "ignore",
    message=".*ReadFileContents Failed to open file.*",
    category=UserWarning
)
warnings.filterwarnings(
    "ignore",
    message=".*device_discovery.*",
    category=UserWarning
)

# Suppress all ONNX Runtime warnings
warnings.filterwarnings(
    "ignore",
    message=".*onnxruntime.*",
    category=UserWarning
)
warnings.filterwarnings(
    "ignore",
    message=".*onnx.*",
    category=UserWarning
)


def _install_indoclaw():
    """
    Auto-install IndoClaw with all dependencies.
    This is called when --install flag is used.
    Installs to ~/.indoclaw directory.
    """
    import subprocess
    import sys
    import shutil
    from pathlib import Path

    print()
    print("=" * 60)
    print("    IndoClaw Auto-Install")
    print("=" * 60)
    print()

    # Installation directory
    indoclaw_dir = Path.home() / ".indoclaw"
    venv_dir = indoclaw_dir / "venv"

    print(f"Installation directory: {indoclaw_dir}")
    print()

    # Get the script directory (where this file is located)
    script_dir = Path(__file__).parent.parent

    # Copy source files to installation directory
    print("Copying source files...")
    if indoclaw_dir.exists():
        shutil.rmtree(indoclaw_dir)
    indoclaw_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files from script directory
    for item in script_dir.iterdir():
        if item.name in [".git", "__pycache__"]:
            continue
        dest = indoclaw_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(item, dest)

    # Check for virtual environment
    if venv_dir.exists():
        print(f"Virtual environment already exists at {venv_dir}")
        print("Reinstalling automatically...")
        shutil.rmtree(venv_dir)
        print("Old venv removed.")

    # Create virtual environment
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        pip_path = venv_dir / "bin" / "pip"

    # Upgrade pip
    print("Upgrading pip...")
    subprocess.check_call([str(pip_path), "install", "--upgrade", "pip"])

    # Install IndoClaw package
    print("Installing IndoClaw and dependencies...")
    subprocess.check_call([str(pip_path), "install", "-e", str(indoclaw_dir)])

    print()
    print("=" * 60)
    print("    Installation Complete!")
    print("=" * 60)
    print()
    print("IndoClaw has been installed to:")
    print(f"    {indoclaw_dir}")
    print()
    print("To use IndoClaw, add the virtual environment's bin directory to your PATH:")
    print()
    if sys.platform == "win32":
        print(f'    set PATH="%PATH%:{venv_dir}\\Scripts"')
    else:
        print(f'    export PATH="$PATH:{venv_dir}/bin"')
    print()
    print("Add this line to your shell configuration file (~/.bashrc, ~/.zshrc, or ~/.profile)")
    print("Then run: indoclaw --help")
    print()


# Try to import workspace config
try:
    from src.core.workspace import get_agent_config, ensure_agent_workspace
    WORKSPACE_AVAILABLE = True
except ImportError:
    WORKSPACE_AVAILABLE = False


# Global settings file path
INDOCLAW_SETTINGS_FILE = Path.home() / ".indoclaw" / "settings.json"


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
        
        # Check if .indoclaw folder exists
        indo_claw_dir = Path.home() / ".indoclaw"
        if not indo_claw_dir.exists():
            return False
        
        # Check if settings.json exists
        settings_file = indo_claw_dir / "settings.json"
        if not settings_file.exists():
            return False
        
        # Load settings to get default agent
        import json
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        default_agent = settings.get("default_agent", "default")
        
        # Check if workspaces folder exists
        workspaces_dir = indo_claw_dir / "workspaces"
        if not workspaces_dir.exists():
            return False
        
        # Check if default agent folder exists
        agent_dir = workspaces_dir / default_agent
        if not agent_dir.exists():
            return False
        
        # Check if config file exists
        config_file = agent_dir / "agent_config.json"
        if not config_file.exists():
            return False
        
        # Load config and check essential settings
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
    Get the default agent name from global settings.
    
    Returns:
        Default agent name
    """
    if not WORKSPACE_AVAILABLE:
        return "default"
    
    try:
        from pathlib import Path
        
        # Check if .indoclaw/settings.json exists
        settings_file = Path.home() / ".indoclaw" / "settings.json"
        if settings_file.exists():
            import json
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings.get("default_agent", "default")
        
        # Fallback to checking workspace
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


def _create_agent_workspace_files(workspace_dir: Path, agent_name: str = "IndoClaw") -> None:
    """Create default workspace files for an agent."""
    # Update IDENTITY.md with agent name
    identity_content = f"""# IDENTITY.md - Agent Identity

## Agent Name
{agent_name}

## Role
Autonomous AI Assistant

## Persona
- Compassionate
- Wise
- Guiding

## Tone
- Professional
- Clear
- Helpful
"""

    default_files = {
        "SOUL.md": """# SOUL.md - Agent Soul & Mission

## Purpose
The core identity and mission of this agent.

## Vision
Long-term goals and aspirations.

## Values
Core principles guiding the agent's behavior.
""",
        "AGENTS.md": f"""# AGENTS.md - Agent Specifications

## Agent Name
{agent_name}

## Description
Autonomous AI agent operating system.

## Capabilities
- Task execution
- Memory management
- Tool usage

## Personality
- Helpful
- Efficient
- Adaptive
""",
        "HEARTBEAT.md": """# HEARTBEAT.md - Agent Status

## Status
Active

## Last Update
{date}

## Health Metrics
- CPU: N/A
- Memory: N/A
- Uptime: N/A
""",
        "IDENTITY.md": identity_content,
        "USER.md": """# USER.md - User Interaction

## User Profile
- Name: Admin
- Role: System Administrator

## Interaction Guidelines
- Provide clear, actionable guidance
- Maintain consistency
- Support user decision-making

## Preferences
- Direct communication
- Actionable insights
- Values-aligned suggestions
""",
        "MEMORY.md": """# MEMORY.md - Memory Configuration

## Short-term Memory
- Current session context
- Recent interactions
- Active tasks

## Long-term Memory
- Historical patterns
- Learned behaviors
- Key insights

## Memory Persistence
- Enable: Yes
- Storage: Local
- TTL: Session-based
""",
        "TOOLS.md": """# TOOLS.md - Available Tools

## Available Tools
- File system operations
- Data analysis
- Code generation
- Web browsing
- Database operations

## Tool Preferences
- Use most efficient method
- Prefer local operations when possible
- Cross-validate critical operations

## Tool Limitations
- Memory constraints
- Processing time
- API rate limits
"""
    }
    
    import datetime
    for filename, content in default_files.items():
        file_path = workspace_dir / filename
        content = content.replace("{date}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        file_path.write_text(content, encoding="utf-8")


def run_onboard() -> bool:
    """
    Run the onboard process for first-time setup.
    Creates the "default" agent configuration and workspace files.
    
    Returns:
        True if successful, False otherwise
    """
    print("=" * 50)
    print("IndoClaw First-Time Setup")
    print("=" * 50)
    print()
    print("Welcome to IndoClaw! Let's configure your agent.")
    print()
    
    # Get agent name - default to "IndoClaw" if not provided
    agent_name = input("Enter agent name (default: IndoClaw): ").strip()
    if not agent_name:
        agent_name = "IndoClaw"
    
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
        from pathlib import Path
        
        # Ensure .indoclaw folder exists
        indo_claw_dir = Path.home() / ".indoclaw"
        indo_claw_dir.mkdir(parents=True, exist_ok=True)
        
        # Save settings.json with default_agent
        settings_file = indo_claw_dir / "settings.json"
        import json
        settings = {"default_agent": agent_name}
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        
        workspace_config = get_agent_config(agent_name=agent_name)
        workspace_config.save(config)
        
        # Create workspace files
        _create_agent_workspace_files(workspace_config.workspace_dir, agent_name)
        
        print()
        print("=" * 50)
        print("Setup Complete!")
        print("=" * 50)
        print(f"Agent '{agent_name}' configured successfully!")
        print(f"Config saved to: {workspace_config.workspace_dir}")
        print(f"Workspace files created:")
        for filename in ["SOUL.md", "IDENTITY.md", "AGENTS.md", "HEARTBEAT.md", "USER.md", "MEMORY.md", "TOOLS.md"]:
            print(f"  - {filename}")
        print(f"LLM Provider: {llm_provider}")
        print(f"LLM Model: {llm_model}")
        print()
        print("You can now run 'indoclaw' to start your agent.")
        print()
        
        return True
    except Exception as e:
        print(f"Setup failed: {e}")
        return False


def reset_indoclaw() -> bool:
    """
    Reset IndoClaw by removing only the .indoclaw folder.
    This removes all agents and configurations.
    
    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path
    import shutil
    
    print("=" * 50)
    print("IndoClaw Reset")
    print("=" * 50)
    print()
    
    indo_claw_dir = Path.home() / ".indoclaw"
    
    print(f"Removing .indoclaw folder: {indo_claw_dir}")
    
    if not indo_claw_dir.exists():
        print(".indoclaw folder not found. Nothing to reset.")
        return True
    
    try:
        shutil.rmtree(indo_claw_dir)
        print(f"Successfully removed {indo_claw_dir}")
        print()
        print("IndoClaw has been reset. Run 'indoclaw onboard' to reconfigure.")
        return True
    except Exception as e:
        print(f"Error removing .indoclaw folder: {e}")
        return False


def uninstall(full: bool = False) -> bool:
    """
    Uninstall IndoClaw files.
    
    Args:
        full: If True, also remove the ~/.indoclaw folder
    
    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path
    
    print("=" * 50)
    print("IndoClaw Uninstall")
    print("=" * 50)
    print()
    
    if full:
        indo_claw_dir = Path.home() / ".indoclaw"
        print(f"Removing entire .indoclaw folder: {indo_claw_dir}")
        
        if not indo_claw_dir.exists():
            print(".indoclaw folder not found. Nothing to remove.")
            return True
        
        try:
            import shutil
            shutil.rmtree(indo_claw_dir)
            print(f"Successfully removed {indo_claw_dir}")
            print()
            print("IndoClaw has been completely uninstalled.")
            return True
        except Exception as e:
            print(f"Error removing .indoclaw folder: {e}")
            return False
    else:
        # Remove workspace config files but keep the folder
        print("Removing agent configurations...")
        
        workspaces_dir = Path.home() / ".indoclaw" / "workspaces"
        
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
    import sys
    
    # Import command compiler
    from src.core.command_compiler import parse_command_line, print_help
    
    # Get command line arguments (excluding script name)
    args_list = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Parse command line
    try:
        parsed = parse_command_line(args_list)
    except ValueError as e:
        print(str(e))
        print()
        print_help()
        return
    
    # Handle install flag (before parsing other options)
    if "--install" in args_list:
        _install_indoclaw()
        return

    # Handle help flag
    if parsed.get("help"):
        print_help()
        return

    # Extract parsed values
    command = parsed.get("command")
    agent_name = parsed.get("agent_name")
    prompt = parsed.get("prompt")
    
    # Fallback to default agent name if not specified
    if not agent_name:
        agent_name = get_default_agent_name()
    options = parsed.get("options", {})
    verbose = parsed.get("verbose", False)
    format_opt = parsed.get("format")
    full_remove = options.get("--full", False)
    
    # Handle onboard command
    if command == "onboard":
        run_onboard()
        return
    
    # Handle setup command
    if command == "setup":
        from src.interfaces.cli import IndoClawCLI
        cli = IndoClawCLI(verbose=False)
        cli.setup_agent(agent_name)
        return
    
    # Handle reset command
    if command == "reset":
        reset_indoclaw()
        return
    
    # Handle uninstall command
    if command == "uninstall":
        uninstall(full=full_remove)
        return
    
    # Check if command is actually an agent name (folder exists in workspaces)
    # This handles cases like "indoclaw klnd" where klnd is an agent name
    if not command and not agent_name and parsed.get("prompt"):
        potential_agent = parsed.get("prompt")
        workspace_base = Path.home() / ".indoclaw" / "workspaces"
        agent_dir = workspace_base / potential_agent
        config_file = agent_dir / "agent_config.json"
        if agent_dir.exists() and config_file.exists():
            # Treat the prompt as an agent name
            agent_name = potential_agent
            parsed["prompt"] = None  # Clear the prompt since it's the agent name
    
    # Check if no agents exist at all - prompt for onboarding
    workspace_base = Path.home() / ".indoclaw" / "workspaces"
    agents_exist = workspace_base.exists() and any(
        item.is_dir() and (item / "agent_config.json").exists()
        for item in workspace_base.iterdir()
    )
    
    if not agents_exist:
        print()
        print("=" * 60)
        print("  IndoClaw has not been configured yet.")
        print("=" * 60)
        print()
        print("No agents configured.")
        print()
        print("Please run 'indoclaw onboard' to create your first agent.")
        print()
        print("Available commands:")
        print("  onboard     Run first-time setup wizard")
        print("  uninstall   Uninstall IndoClaw")
        print()
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
    
    # Check if agent exists in workspaces (if agent_name is specified)
    if agent_name:
        agent_dir = workspace_base / agent_name
        config_file = agent_dir / "agent_config.json"
        if not agent_dir.exists() or not config_file.exists():
            print(f"Error: Agent '{agent_name}' not found.")
            print(f"Agent workspace: {agent_dir}")
            print()
            print("Available agents:")
            for item in workspace_base.iterdir():
                if item.is_dir() and (item / "agent_config.json").exists():
                    print(f"  - {item.name}")
            print()
            print("Please run 'indoclaw agent onboard' to configure an agent.")
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
    
    # Run the CLI with parsed values
    from src.interfaces.cli import IndoClawCLI
    
    # Create CLI with agent name
    cli = IndoClawCLI(verbose=verbose, agent_name=agent_name)
    
    # Run with prompt if provided, otherwise chat mode
    if prompt:
        cli.run_single(prompt)
    else:
        cli.run(chat=True)


if __name__ == "__main__":
    main()