"""
Formatting utility functions
"""

from .constants import Colors


def format_number(value):
    """Format large numbers in readable format"""
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except:
        return str(value)


def format_percentage(value):
    """Format percentage values"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except:
        return str(value)


def format_percentage_colored(value):
    """Format percentage values with color (green for positive, red for negative)"""
    if value is None:
        return f"{Colors.WHITE}N/A{Colors.END}"
    try:
        val = float(value)
        color = Colors.GREEN if val >= 0 else Colors.RED
        sign = "+" if val >= 0 else ""
        return f"{color}{sign}{val:.2f}%{Colors.END}"
    except:
        return f"{Colors.WHITE}{str(value)}{Colors.END}"


def format_ratio(value):
    """Format ratio values"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}"
    except:
        return str(value)


def format_price(value):
    """Format price values"""
    if value is None:
        return "N/A"
    try:
        return f"${float(value):.2f}"
    except:
        return str(value)


