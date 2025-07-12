"""
Unit tests for ADIENT Inventory Management System - Inventory Module
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.inventory.inventory_manager import InventoryManager
from src.database.models import InventoryItem, Supplier, StockMovement
from config.settings import TestingConfig

class TestInventoryManager(unittest.TestCase):
    """Test cases for InventoryManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.inventory_manager = InventoryManager()
        
        # Mock database session
        self.mock_session = Mock()
        self.mock_session.__enter__ = Mock(return_value=self.mock_session)
        self.mock_session.__exit__ = Mock(return_value=None)
        
        # Sample test data
        self.sample_supplier = Supplier(
            id=1,
            name="Test Supplier",
            lead_time_days=5
        )
        
        self.sample_item = InventoryItem(
            id=1,
            part_number="TEST-001",
            name="Test Item",
            current_stock=100,
            minimum_stock=20,
            maximum_stock=500,
            reorder_point=50,
            reorder_quantity=200,
            unit_cost=25.50,
            supplier=self.sample_supplier
        )
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_get_all_inventory_items(self, mock_get_session):
        """Test getting all inventory items"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.all.return_value = [self.sample_item]
        
        # Execute
        result = self.inventory_manager.get_all_inventory_items()
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['part_number'], 'TEST-001')
        self.assertEqual(result[0]['current_stock'], 100)
        self.assertEqual(result[0]['supplier_name'], 'Test Supplier')
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_get_inventory_item_by_id(self, mock_get_session):
        """Test getting specific inventory item by ID"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.first.return_value = self.sample_item
        
        # Mock recent movements
        with patch.object(self.inventory_manager, '_get_recent_movements', return_value=[]):
            result = self.inventory_manager.get_inventory_item(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['part_number'], 'TEST-001')
        self.assertIn('stock_metrics', result)
        self.assertIn('supplier', result)
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_update_stock_in_movement(self, mock_get_session):
        """Test updating stock with IN movement"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.first.return_value = self.sample_item
        
        # Mock the check_stock_alerts method
        with patch.object(self.inventory_manager, '_check_stock_alerts'):
            result = self.inventory_manager.update_stock(
                item_id=1,
                quantity=50,
                movement_type='IN',
                reference_number='PO-123',
                reason='Purchase order delivery'
            )
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(self.sample_item.current_stock, 150)  # 100 + 50
        self.mock_session.add.assert_called()
        self.mock_session.commit.assert_called()
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_update_stock_out_movement(self, mock_get_session):
        """Test updating stock with OUT movement"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.first.return_value = self.sample_item
        
        # Mock the check_stock_alerts method
        with patch.object(self.inventory_manager, '_check_stock_alerts'):
            result = self.inventory_manager.update_stock(
                item_id=1,
                quantity=30,
                movement_type='OUT',
                reference_number='WO-456',
                reason='Production consumption'
            )
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(self.sample_item.current_stock, 70)  # 100 - 30
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_update_stock_insufficient_stock(self, mock_get_session):
        """Test updating stock with insufficient stock for OUT movement"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.first.return_value = self.sample_item
        
        # Execute and assert exception
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.update_stock(
                item_id=1,
                quantity=150,  # More than current stock (100)
                movement_type='OUT'
            )
        
        self.assertIn("Insufficient stock", str(context.exception))
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_get_low_stock_items(self, mock_get_session):
        """Test getting low stock items"""
        # Create low stock item
        low_stock_item = InventoryItem(
            id=2,
            part_number="LOW-001",
            name="Low Stock Item",
            current_stock=15,  # Below reorder point
            reorder_point=20,
            reorder_quantity=100,
            unit_cost=10.00,
            supplier=self.sample_supplier
        )
        
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.all.return_value = [low_stock_item]
        
        # Execute
        result = self.inventory_manager.get_low_stock_items()
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['part_number'], 'LOW-001')
        self.assertEqual(result[0]['current_stock'], 15)
        self.assertGreater(result[0]['urgency_score'], 0)
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_generate_reorder_suggestions(self, mock_get_session):
        """Test generating reorder suggestions"""
        # Mock get_low_stock_items
        with patch.object(self.inventory_manager, 'get_low_stock_items') as mock_low_stock:
            mock_low_stock.return_value = [{
                'id': 1,
                'part_number': 'TEST-001',
                'name': 'Test Item',
                'current_stock': 15,
                'reorder_point': 20,
                'reorder_quantity': 100,
                'supplier_name': 'Test Supplier',
                'lead_time_days': 5,
                'urgency_score': 75.0
            }]
            
            # Mock _get_item_cost
            with patch.object(self.inventory_manager, '_get_item_cost', return_value=25.50):
                result = self.inventory_manager.generate_reorder_suggestions()
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['part_number'], 'TEST-001')
        self.assertIn('suggested_quantity', result[0])
        self.assertIn('estimated_cost', result[0])
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_get_stock_valuation(self, mock_get_session):
        """Test calculating stock valuation"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.all.return_value = [self.sample_item]
        
        # Execute
        result = self.inventory_manager.get_stock_valuation()
        
        # Assert
        expected_value = 100 * 25.50  # current_stock * unit_cost
        self.assertEqual(result['total_value'], expected_value)
        self.assertEqual(result['total_items'], 100)
        self.assertEqual(result['unique_parts'], 1)
    
    def test_calculate_stock_metrics(self):
        """Test calculating stock metrics"""
        # Mock average consumption calculation
        with patch.object(self.inventory_manager, '_calculate_average_consumption', return_value=2.5):
            result = self.inventory_manager._calculate_stock_metrics(self.sample_item)
        
        # Assert
        self.assertIn('status', result)
        self.assertIn('days_of_supply', result)
        self.assertIn('reorder_needed', result)
        self.assertEqual(result['days_of_supply'], 40.0)  # 100 / 2.5
        self.assertFalse(result['reorder_needed'])  # 100 > 50 (reorder_point)
    
    def test_calculate_stock_metrics_low_stock(self):
        """Test calculating stock metrics for low stock item"""
        # Create low stock item
        low_stock_item = InventoryItem(
            id=2,
            part_number="LOW-001",
            name="Low Stock Item",
            current_stock=15,
            reorder_point=20,
            unit_cost=10.00
        )
        
        # Mock average consumption calculation
        with patch.object(self.inventory_manager, '_calculate_average_consumption', return_value=1.0):
            result = self.inventory_manager._calculate_stock_metrics(low_stock_item)
        
        # Assert
        self.assertEqual(result['status'], 'LOW_STOCK')
        self.assertTrue(result['reorder_needed'])
        self.assertGreater(result['urgency_score'], 0)
    
    def test_calculate_stock_metrics_out_of_stock(self):
        """Test calculating stock metrics for out of stock item"""
        # Create out of stock item
        out_of_stock_item = InventoryItem(
            id=3,
            part_number="OUT-001",
            name="Out of Stock Item",
            current_stock=0,
            reorder_point=10,
            unit_cost=15.00
        )
        
        # Mock average consumption calculation
        with patch.object(self.inventory_manager, '_calculate_average_consumption', return_value=0.5):
            result = self.inventory_manager._calculate_stock_metrics(out_of_stock_item)
        
        # Assert
        self.assertEqual(result['status'], 'OUT_OF_STOCK')
        self.assertTrue(result['reorder_needed'])
        self.assertEqual(result['days_of_supply'], 0)
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_calculate_average_consumption(self, mock_get_session):
        """Test calculating average consumption"""
        # Setup mock
        mock_get_session.return_value = self.mock_session
        self.mock_session.query.return_value.filter.return_value.scalar.return_value = 150  # Total OUT in 30 days
        
        # Execute
        result = self.inventory_manager._calculate_average_consumption(1, 30)
        
        # Assert
        self.assertEqual(result, 5.0)  # 150 / 30
    
    def test_calculate_optimal_reorder_quantity(self):
        """Test calculating optimal reorder quantity"""
        item_data = {
            'reorder_quantity': 100,
            'current_stock': 15,
            'reorder_point': 20
        }
        
        result = self.inventory_manager._calculate_optimal_reorder_quantity(item_data)
        
        # Assert
        expected = 100 + (20 - 15)  # base_quantity + deficit
        self.assertEqual(result, expected)
    
    def test_validator_integration(self):
        """Test that validator is properly integrated"""
        # Test invalid stock movement
        with self.assertRaises(ValueError):
            self.inventory_manager.update_stock(
                item_id=1,
                quantity=-10,  # Invalid negative quantity
                movement_type='IN'
            )


class TestInventoryValidation(unittest.TestCase):
    """Test cases for inventory data validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.inventory_manager = InventoryManager()
    
    def test_validate_positive_quantities(self):
        """Test validation of positive quantities"""
        # Valid positive quantity
        self.assertTrue(
            self.inventory_manager.validator.validate_stock_movement(50, 'IN')
        )
        
        # Invalid negative quantity for IN movement
        self.assertFalse(
            self.inventory_manager.validator.validate_stock_movement(-10, 'IN')
        )
        
        # Invalid zero quantity for OUT movement
        self.assertFalse(
            self.inventory_manager.validator.validate_stock_movement(0, 'OUT')
        )
    
    def test_validate_movement_types(self):
        """Test validation of movement types"""
        valid_types = ['IN', 'OUT', 'ADJUSTMENT']
        
        for movement_type in valid_types:
            self.assertTrue(
                self.inventory_manager.validator.validate_stock_movement(10, movement_type)
            )
        
        # Invalid movement type
        self.assertFalse(
            self.inventory_manager.validator.validate_stock_movement(10, 'INVALID')
        )


class TestInventoryIntegration(unittest.TestCase):
    """Integration tests for inventory management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.inventory_manager = InventoryManager()
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_stock_movement_workflow(self, mock_get_session):
        """Test complete stock movement workflow"""
        # Setup mock
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        mock_get_session.return_value = mock_session
        
        # Create test item
        test_item = InventoryItem(
            id=1,
            part_number="FLOW-001",
            name="Workflow Test Item",
            current_stock=100,
            reorder_point=20
        )
        
        mock_session.query.return_value.filter.return_value.first.return_value = test_item
        
        # Mock the alert checking
        with patch.object(self.inventory_manager, '_check_stock_alerts'):
            # Test IN movement
            result = self.inventory_manager.update_stock(
                item_id=1,
                quantity=50,
                movement_type='IN',
                reference_number='TEST-001'
            )
            
            self.assertTrue(result)
            self.assertEqual(test_item.current_stock, 150)
            
            # Test OUT movement
            result = self.inventory_manager.update_stock(
                item_id=1,
                quantity=30,
                movement_type='OUT',
                reference_number='TEST-002'
            )
            
            self.assertTrue(result)
            self.assertEqual(test_item.current_stock, 120)
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_reorder_workflow(self, mock_get_session):
        """Test reorder suggestion workflow"""
        # Setup mock
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        mock_get_session.return_value = mock_session
        
        # Create low stock items
        low_stock_items = [
            InventoryItem(
                id=1,
                part_number="REORDER-001",
                name="Low Stock Item 1",
                current_stock=10,
                reorder_point=20,
                reorder_quantity=100,
                unit_cost=15.00,
                supplier=Supplier(name="Supplier A", lead_time_days=5)
            ),
            InventoryItem(
                id=2,
                part_number="REORDER-002",
                name="Low Stock Item 2",
                current_stock=5,
                reorder_point=15,
                reorder_quantity=75,
                unit_cost=25.00,
                supplier=Supplier(name="Supplier B", lead_time_days=7)
            )
        ]
        
        mock_session.query.return_value.filter.return_value.all.return_value = low_stock_items
        
        # Execute
        result = self.inventory_manager.get_low_stock_items()
        
        # Assert
        self.assertEqual(len(result), 2)
        
        # Check urgency ordering (item 2 should be more urgent due to lower stock ratio)
        self.assertGreater(result[0]['urgency_score'], result[1]['urgency_score'])


class TestInventoryErrorHandling(unittest.TestCase):
    """Test error handling in inventory management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.inventory_manager = InventoryManager()
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_update_stock_item_not_found(self, mock_get_session):
        """Test updating stock for non-existent item"""
        # Setup mock
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        mock_get_session.return_value = mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute and assert
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.update_stock(
                item_id=999,  # Non-existent item
                quantity=10,
                movement_type='IN'
            )
        
        self.assertIn("not found", str(context.exception))
    
    def test_invalid_movement_data(self):
        """Test handling of invalid movement data"""
        # Test invalid quantity type
        with self.assertRaises(ValueError):
            self.inventory_manager.update_stock(
                item_id=1,
                quantity="invalid",  # String instead of int
                movement_type='IN'
            )
    
    @patch('src.inventory.inventory_manager.get_db_session')
    def test_database_error_handling(self, mock_get_session):
        """Test handling of database errors"""
        # Setup mock to raise exception
        mock_get_session.side_effect = Exception("Database connection error")
        
        # Execute and assert
        with self.assertRaises(Exception):
            self.inventory_manager.get_all_inventory_items()


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestInventoryManager))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestInventoryValidation))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestInventoryIntegration))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestInventoryErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)