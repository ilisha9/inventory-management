"""
Inventory Management package for ADIENT Inventory Management System

This package provides comprehensive inventory management functionality including:
- Real-time stock level monitoring and tracking
- Automated reorder point calculations and suggestions
- Stock movement recording and history tracking
- Low stock alerts and notifications
- Inventory valuation and reporting
- Integration with production systems

Components:
- inventory_manager: Core inventory management operations
- stock_monitor: Real-time stock monitoring and alerts
- alerts: Inventory-related alert generation and management

Key Features:
- Automated stock tracking with real-time updates
- Intelligent reorder suggestions based on consumption patterns
- Comprehensive stock movement history
- Multi-location inventory support
- Supplier integration and lead time management

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .inventory_manager import InventoryManager

# Import other components when they are implemented
try:
    from .stock_monitor import StockMonitor
except ImportError:
    StockMonitor = None

try:
    from .alerts import InventoryAlertManager
except ImportError:
    InventoryAlertManager = None

__all__ = [
    'InventoryManager',
]

# Add optional components if available
if StockMonitor:
    __all__.append('StockMonitor')
    
if InventoryAlertManager:
    __all__.append('InventoryAlertManager')

# Package metadata
__version__ = "1.0.0"
__description__ = "Inventory management components for automated stock tracking and optimization"

# Configuration constants
DEFAULT_LOW_STOCK_THRESHOLD = 0.2  # 20% of maximum stock
DEFAULT_REORDER_SAFETY_FACTOR = 1.5
DEFAULT_MONITORING_INTERVAL = 300  # 5 minutes