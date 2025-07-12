"""
ADIENT Inventory Management System

A comprehensive Python-based automated inventory management system
developed during internship at ADIENT (March 2022 - June 2022).

This system provides:
- Real-time inventory tracking and monitoring
- Production line performance analysis
- Optimization algorithms for resource allocation
- Command-line interface for system interaction
- Automated alerts and notifications

Author: Hilmi Iliass
Email: ilihilmi13@gmail.com
Date: March 2022 - June 2022
"""

__version__ = "1.0.0"
__author__ = "Hilmi Iliass"
__email__ = "ilihilmi13@gmail.com"
__description__ = "ADIENT Automated Inventory Management System"

# Core module imports
from . import database
from . import inventory
from . import production
from . import optimization
from . import cli
from . import utils

__all__ = [
    'database',
    'inventory', 
    'production',
    'optimization',
    'cli',
    'utils'
]