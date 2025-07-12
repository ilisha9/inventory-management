"""
Production Management package for ADIENT Inventory Management System

This package provides comprehensive production monitoring and analysis including:
- Real-time production line monitoring
- Performance metrics calculation and analysis
- Production data collection and validation
- Efficiency tracking and trend analysis
- Quality control monitoring
- Downtime tracking and reporting

Components:
- production_monitor: Core production monitoring and data collection
- data_collector: Automated production data collection from various sources
- performance_analyzer: Production performance analysis and reporting

Key Features:
- Real-time production line status monitoring
- Automated efficiency calculations and trending
- Quality metrics tracking and analysis
- Downtime analysis with root cause tracking
- Integration with inventory consumption tracking
- Predictive maintenance scheduling support

Performance Metrics Tracked:
- Overall Equipment Effectiveness (OEE)
- Production efficiency vs targets
- Quality rates and defect tracking
- Downtime patterns and analysis
- Throughput and capacity utilization

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .production_monitor import ProductionMonitor

# Import other components when they are implemented
try:
    from .data_collector import ProductionDataCollector
except ImportError:
    ProductionDataCollector = None

try:
    from .performance_analyzer import PerformanceAnalyzer
except ImportError:
    PerformanceAnalyzer = None

__all__ = [
    'ProductionMonitor',
]

# Add optional components if available
if ProductionDataCollector:
    __all__.append('ProductionDataCollector')
    
if PerformanceAnalyzer:
    __all__.append('PerformanceAnalyzer')

# Package metadata
__version__ = "1.0.0"
__description__ = "Production monitoring and analysis components for manufacturing optimization"

# Configuration constants
DEFAULT_MONITORING_INTERVAL = 60  # 1 minute
DEFAULT_EFFICIENCY_TARGET = 0.85  # 85%
DEFAULT_QUALITY_TARGET = 0.95  # 95%
DEFAULT_ALERT_THRESHOLD = 0.8  # 80% efficiency threshold for alerts

# Production shift configurations
SHIFTS_PER_DAY = 3
SHIFT_DURATION_HOURS = 8
PRODUCTION_DAYS_PER_WEEK = 5