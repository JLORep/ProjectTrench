#!/usr/bin/env python3
"""
Claude Code slash command: /remember
Usage: /remember [--json] [--save filename]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from remember_command import main

if __name__ == "__main__":
    main()