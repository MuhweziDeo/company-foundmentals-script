"""
Constants and configuration for Stock Finder
"""

import os

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    WHITE = '\033[97m'


# FRED API Configuration
FRED_API_KEY = os.environ.get('FRED_API_KEY')
FRED_API_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"




