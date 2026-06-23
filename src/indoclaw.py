"""
IndoClaw - Autonomous AI Agent OS

A Python-based autonomous AI agent operating system built with LangChain.

Usage:
    python -m src
    python src/indoclaw.py

For more information, see the README.md file.
"""

import warnings
from src.__main__ import main

# Suppress LangChain Pydantic compatibility warnings for Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater",
    category=UserWarning
)

__version__ = "0.1.0"
__author__ = "IndoClaw Team"

__all__ = ["main"]
