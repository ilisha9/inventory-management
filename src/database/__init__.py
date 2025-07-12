"""
Database package for ADIENT Inventory Management System

This package handles all database operations including:
- Database connection management
- ORM models for all entities
- Database migrations and schema management
- Session handling and transaction management

Components:
- models: SQLAlchemy ORM models for all database entities
- connection: Database connection and session management
- migrations: Database schema and migration scripts

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .connection import DatabaseManager, get_db_session, get_scoped_session, close_db_connections
from .models import (
    Base,
    InventoryItem,
    Supplier,
    StockMovement,
    ProductionLine,
    ProductionRecord,
    ProductionItem,
    ResourceAllocation,
    Alert,
    OptimizationResult,
    SystemLog,
    create_tables
)

__all__ = [
    # Connection management
    'DatabaseManager',
    'get_db_session',
    'get_scoped_session', 
    'close_db_connections',
    
    # ORM Models
    'Base',
    'InventoryItem',
    'Supplier',
    'StockMovement',
    'ProductionLine',
    'ProductionRecord',
    'ProductionItem',
    'ResourceAllocation',
    'Alert',
    'OptimizationResult',
    'SystemLog',
    
    # Utilities
    'create_tables'
]

# Package metadata
__version__ = "1.0.0"