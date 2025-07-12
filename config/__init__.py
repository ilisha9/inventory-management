"""
Configuration package for ADIENT Inventory Management System

This package contains configuration settings, logging setup, and environment management.

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .logging_config import setup_logging

__version__ = "1.0.0"
__author__ = "Hilmi Iliass"

# Package metadata
__all__ = [
    'Config',
    'DevelopmentConfig', 
    'ProductionConfig',
    'TestingConfig',
    'setup_logging'
]

# Default configuration
DEFAULT_CONFIG = DevelopmentConfig