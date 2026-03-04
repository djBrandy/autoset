#!/usr/bin/env python3
"""
AutoSET Launcher
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run main
from autoset.agent import main

if __name__ == "__main__":
    main()
