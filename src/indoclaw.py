"""
IndoClaw - Autonomous AI Agent OS

A Python-based autonomous AI agent operating system built with LangChain.

Usage:
    python -m src
    python src/indoclaw.py

For more information, see the README.md file.
"""

from src.interfaces.cli import IndoClawCLI, main

__version__ = "0.1.0"
__author__ = "IndoClaw Team"

__all__ = ["IndoClawCLI", "main"]