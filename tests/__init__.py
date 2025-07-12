"""
Test suite for ADIENT Inventory Management System

This package contains comprehensive unit tests, integration tests, and system tests
for all components of the inventory management system.

Test Categories:
- Unit Tests: Individual component testing with mocking
- Integration Tests: Component interaction testing
- System Tests: End-to-end system functionality testing
- Performance Tests: Load and performance testing
- Database Tests: Database operations and transactions

Test Modules:
- test_inventory: Inventory management functionality tests
- test_production: Production monitoring and analysis tests
- test_optimization: Optimization algorithms and performance tests
- test_database: Database operations and model tests
- test_cli: Command-line interface tests
- test_utils: Utility functions and validation tests

Test Coverage Areas:
- Inventory tracking and stock movements
- Production data collection and analysis
- Optimization algorithm correctness
- Database integrity and performance
- CLI command functionality
- Data validation and error handling
- Alert generation and management
- Report generation accuracy

Testing Framework:
- pytest for test execution and fixtures
- unittest.mock for component mocking
- pytest-cov for coverage reporting
- Custom fixtures for database testing

Usage:
    # Run all tests
    pytest tests/
    
    # Run specific test module
    pytest tests/test_inventory.py
    
    # Run with coverage
    pytest --cov=src tests/
    
    # Run specific test
    pytest tests/test_inventory.py::TestInventoryManager::test_update_stock

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for testing
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / 'src'
sys.path.insert(0, str(SRC_PATH))

# Test configuration
TEST_DATABASE_URL = 'sqlite:///:memory:'
TEST_LOG_LEVEL = 'WARNING'

# Test data constants
SAMPLE_INVENTORY_ITEMS = [
    {
        'part_number': 'TEST-001',
        'name': 'Test Seat Frame',
        'unit_cost': 85.50,
        'current_stock': 100,
        'minimum_stock': 20,
        'reorder_point': 30
    },
    {
        'part_number': 'TEST-002', 
        'name': 'Test Foam Cushion',
        'unit_cost': 25.75,
        'current_stock': 50,
        'minimum_stock': 10,
        'reorder_point': 15
    }
]

SAMPLE_PRODUCTION_DATA = [
    {
        'line_name': 'Test Assembly Line 1',
        'capacity_per_hour': 25,
        'efficiency_target': 0.90
    },
    {
        'line_name': 'Test Assembly Line 2',
        'capacity_per_hour': 20,
        'efficiency_target': 0.85
    }
]

# Test utilities
def setup_test_database():
    """Setup test database with sample data"""
    from src.database.connection import DatabaseManager
    from config.settings import TestingConfig
    
    db_manager = DatabaseManager(TEST_DATABASE_URL)
    db_manager.initialize_database()
    return db_manager

def cleanup_test_database(db_manager):
    """Cleanup test database after tests"""
    try:
        db_manager.close_all_connections()
    except:
        pass

def create_sample_inventory_item(inventory_manager, **kwargs):
    """Create sample inventory item for testing"""
    default_data = SAMPLE_INVENTORY_ITEMS[0].copy()
    default_data.update(kwargs)
    return default_data

def create_sample_production_record(**kwargs):
    """Create sample production record for testing"""
    default_data = {
        'product_id': 'TEST-PRODUCT',
        'planned_quantity': 100,
        'actual_quantity': 95,
        'defective_quantity': 2,
        'efficiency': 95.0,
        'downtime_minutes': 10,
        'quality_score': 98.0
    }
    default_data.update(kwargs)
    return default_data

# Test fixtures and helpers
class TestHelpers:
    """Common test helper methods"""
    
    @staticmethod
    def assert_inventory_item_valid(item_data):
        """Assert that inventory item data is valid"""
        required_fields = ['part_number', 'name', 'unit_cost']
        for field in required_fields:
            assert field in item_data, f"Missing required field: {field}"
        
        assert item_data['unit_cost'] >= 0, "Unit cost must be non-negative"
        if 'current_stock' in item_data:
            assert item_data['current_stock'] >= 0, "Stock must be non-negative"
    
    @staticmethod
    def assert_production_data_valid(production_data):
        """Assert that production data is valid"""
        if 'efficiency' in production_data:
            assert 0 <= production_data['efficiency'] <= 100, "Efficiency must be 0-100%"
        
        if 'quality_score' in production_data:
            assert 0 <= production_data['quality_score'] <= 100, "Quality score must be 0-100"
    
    @staticmethod
    def mock_database_session():
        """Create mock database session for testing"""
        from unittest.mock import Mock
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.close = Mock()
        
        return mock_session

# Export test utilities
__all__ = [
    'TEST_DATABASE_URL',
    'TEST_LOG_LEVEL',
    'SAMPLE_INVENTORY_ITEMS',
    'SAMPLE_PRODUCTION_DATA',
    'setup_test_database',
    'cleanup_test_database',
    'create_sample_inventory_item',
    'create_sample_production_record',
    'TestHelpers'
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Test suite for ADIENT Inventory Management System"