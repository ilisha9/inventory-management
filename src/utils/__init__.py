"""
Utilities package for ADIENT Inventory Management System

This package provides utility functions and helper classes used throughout
the system for data validation, reporting, and common operations.

Components:
- data_validator: Comprehensive data validation for all system inputs

Key Features:
- Input validation for all data types (inventory, production, etc.)
- Data sanitization and security validation
- Date/time utilities for manufacturing operations
- Mathematical utilities for calculations
- File I/O utilities for data import/export

Validation Categories:
- Inventory item validation (part numbers, quantities, costs)
- Production data validation (efficiency, quality metrics)
- Supplier information validation (contact details, lead times)
- Alert and notification validation
- System configuration validation

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .data_validator import DataValidator

__all__ = [
    'DataValidator',
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Utility functions and helpers for the ADIENT Inventory Management System"

# Validation constants
VALIDATION_PATTERNS = {
    'PART_NUMBER': r'^[A-Z0-9\-]{3,20},
    'EMAIL': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,},
    'PHONE': r'^[\+]?[1-9][\d]{0,15}
}

# Data type ranges
VALID_RANGES = {
    'QUANTITY': {'min': 0, 'max': 1000000},
    'COST': {'min': 0.0, 'max': 100000.0},
    'EFFICIENCY': {'min': 0.0, 'max': 1.0},
    'QUALITY_SCORE': {'min': 0.0, 'max': 100.0}
}

# Standard units of measure
STANDARD_UNITS = [
    'pieces', 'kg', 'liters', 'meters', 'boxes', 
    'rolls', 'sheets', 'tons', 'gallons', 'yards'
]

# Report formats
REPORT_FORMATS = [
    'table',     # Tabulated output
    'json',      # JSON format
    'csv',       # CSV format
    'excel',     # Excel format
    'pdf'        # PDF format (if implemented)
]

# Date/time utilities
from datetime import datetime, timedelta

def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string"""
    if isinstance(dt, datetime):
        return dt.strftime(format_str)
    return str(dt)

def parse_datetime(dt_str, format_str='%Y-%m-%d %H:%M:%S'):
    """Parse datetime string to datetime object"""
    try:
        return datetime.strptime(dt_str, format_str)
    except ValueError:
        return None

# Mathematical utilities
def calculate_percentage(value, total):
    """Calculate percentage with error handling"""
    if total == 0:
        return 0.0
    return (value / total) * 100

def round_to_precision(value, precision=2):
    """Round value to specified precision"""
    return round(float(value), precision)

# Add utility functions to __all__
__all__.extend([
    'format_datetime',
    'parse_datetime', 
    'calculate_percentage',
    'round_to_precision',
    'VALIDATION_PATTERNS',
    'VALID_RANGES',
    'STANDARD_UNITS',
    'REPORT_FORMATS'
])