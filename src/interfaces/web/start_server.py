#!/usr/bin/env python3
"""
Web interface startup script for IndoClaw.
Starts the FastAPI backend server.
"""
import sys
import os
import subprocess
from pathlib import Path


def main():
    # Get the server directory
    script_dir = Path(__file__).parent
    server_dir = script_dir / "server"

    if not server_dir.exists():
        print("Error: Web interface server not found at", server_dir)
        print("Please run 'indoclaw web install' first.")
        sys.exit(1)

    # Check if fastapi is installed
    try:
        import fastapi
    except ImportError:
        print("Installing FastAPI dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-q",
            "fastapi", "uvicorn", "python-multipart", "websockets"
        ], check=True)

    # Change to the project root directory
    project_root = script_dir.parent.parent.parent
    os.chdir(project_root)

    # Add the project root to Python path
    sys.path.insert(0, str(project_root))

    # Start the server
    print("Starting IndoClaw Web Interface...")
    print(f"Server directory: {server_dir}")
    print("Visit http://localhost:8000 in your browser")
    print("Press Ctrl+C to stop\n")

    # Run uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.interfaces.web.server.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ], cwd=str(project_root), check=True)


if __name__ == "__main__":
    main()
