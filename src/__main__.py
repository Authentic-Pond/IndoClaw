"""
Main entry point for IndoClaw AI OS.
"""

import warnings
from src.interfaces.cli import main

# Suppress LangChain Pydantic compatibility warnings for Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater",
    category=UserWarning
)

if __name__ == "__main__":
    main()
