import pandas as pd
import re
import datetime

def clean_numeric(value):
    """Remove commas from numeric strings and convert to int or float."""
    if isinstance(value, str):
        return value.replace(',', '')
    return value
    
def safe_int(value):
    """Safely convert a value to int, handling commas and returning 0 if invalid."""
    if pd.isna(value):
        return 0
    try:
        # First remove any commas
        if isinstance(value, str):
            value = value.replace(',', '')
        return int(float(value))
    except (ValueError, TypeError):
        return 0
        
def safe_float(value):
    """Safely convert a value to float, handling commas and returning 0.0 if invalid."""
    if pd.isna(value):
        return 0.0
    try:
        # First remove any commas
        if isinstance(value, str):
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def format_number(value, decimal_places=1):
    """Format a number to a specified number of decimal places and remove trailing zeros."""
    formatted = f"{float(value):.{decimal_places}f}"
    if '.' in formatted:
        return formatted.rstrip('0').rstrip('.')
    return formatted

def get_current_timestamp():
    """Get the current timestamp in the format used for loadouts."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 