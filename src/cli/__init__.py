"""
Command Line Interface package for ADIENT Inventory Management System

This package provides a comprehensive command-line interface for interacting with
the inventory management system without requiring a web interface.

Components:
- cli_interface: Main CLI application with command parsing and execution
- Interactive commands for inventory management
- Production monitoring and reporting commands
- Optimization execution and results display
- System status and health monitoring

Available Command Categories:
- inventory: Stock management, reorder suggestions, valuation
- production: Line status, performance metrics, summaries
- optimize: Run optimization algorithms and view results
- system: Health checks, configuration, and maintenance

Key Features:
- Tabulated output for easy reading
- Interactive command-line interface
- Real-time system monitoring
- Comprehensive reporting capabilities
- Error handling and user-friendly messages
- Progress indicators for long-running operations

Usage Examples:
    python main.py inventory status
    python main.py production summary
    python main.py optimize inventory
    python main.py system status

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .cli_interface import ADIENTCLIInterface

__all__ = [
    'ADIENTCLIInterface',
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Command-line interface for ADIENT Inventory Management System"

# CLI configuration constants
DEFAULT_TABLE_FORMAT = 'grid'
MAX_DISPLAY_ROWS = 50
DEFAULT_PAGINATION_SIZE = 20

# Command categories
COMMAND_CATEGORIES = {
    'inventory': 'Inventory management operations',
    'production': 'Production monitoring and analysis',
    'optimize': 'Optimization algorithms and analysis',
    'system': 'System status and maintenance'
}

# Available inventory commands
INVENTORY_COMMANDS = [
    'status',      # Show current inventory status
    'low-stock',   # Display low stock items
    'reorder',     # Generate reorder suggestions
    'valuation',   # Show inventory valuation
    'update'       # Update stock levels
]

# Available production commands
PRODUCTION_COMMANDS = [
    'status',      # Show production line status
    'summary',     # Display production summary
    'efficiency',  # Show efficiency trends
    'quality'      # Display quality metrics
]

# Available optimization commands
OPTIMIZATION_COMMANDS = [
    'inventory',   # Run inventory optimization
    'production',  # Run production scheduling
    'resource'     # Run resource utilization analysis
]

# CLI color schemes (if terminal supports colors)
COLORS = {
    'SUCCESS': '\033[92m',
    'WARNING': '\033[93m', 
    'ERROR': '\033[91m',
    'INFO': '\033[94m',
    'BOLD': '\033[1m',
    'END': '\033[0m'
}