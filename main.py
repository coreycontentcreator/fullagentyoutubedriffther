"""
Main entry point for the Research System
"""

import sys
import os

# Add the research system to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from research_system.chat.chat_interface import main

if __name__ == "__main__":
    main()
