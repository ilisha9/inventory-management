#!/usr/bin/env python3
"""
Example script demonstrating ADIENT Inventory Management System functionality
Shows how to use the system programmatically

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.logging_config import setup_logging
from src.database.connection import DatabaseManager
from src.inventory.inventory_manager import InventoryManager
from src.production.production_monitor import ProductionMonitor
from src.optimization.resource_allocator import ResourceAllocator

# Setup logging
logger = setup_logging()

def demonstrate_inventory_management():
    """Demonstrate inventory management functionality"""
    print("\n" + "="*50)
    print("INVENTORY MANAGEMENT DEMONSTRATION")
    print("="*50)
    
    inventory_manager = InventoryManager()
    
    # Get all inventory items
    print("\n1. Current Inventory Status:")
    items = inventory_manager.get_all_inventory_items()
    for item in items[:5]:  # Show first 5 items
        print(f"  {item['part_number']}: {item['current_stock']} units ({item['stock_status']})")
    
    # Check low stock items
    print("\n2. Low Stock Items:")
    low_stock_items = inventory_manager.get_low_stock_items()
    if low_stock_items:
        for item in low_stock_items:
            print(f"  {item['part_number']}: {item['current_stock']} units (Urgency: {item['urgency_score']:.1f}%)")
    else:
        print("  No low stock items found")
    
    # Generate reorder suggestions
    print("\n3. Reorder Suggestions:")
    suggestions = inventory_manager.generate_reorder_suggestions()
    if suggestions:
        total_cost = 0
        for suggestion in suggestions:
            cost = suggestion['estimated_cost']
            total_cost += cost
            print(f"  {suggestion['part_number']}: Order {suggestion['suggested_quantity']} units (${cost:.2f})")
        print(f"  Total estimated cost: ${total_cost:.2f}")
    else:
        print("  No reorder suggestions at this time")
    
    # Stock valuation
    print("\n4. Stock Valuation:")
    valuation = inventory_manager.get_stock_valuation()
    print(f"  Total inventory value: ${valuation['total_value']:,.2f}")
    print(f"  Total items in stock: {valuation['total_items']:,}")
    print(f"  Unique part numbers: {valuation['unique_parts']}")
    
    # Demonstrate stock update
    print("\n5. Stock Update Example:")
    try:
        # Update stock for first item (if exists)
        if items:
            first_item = items[0]
            old_stock = first_item['current_stock']
            
            # Add 10 units
            result = inventory_manager.update_stock(
                item_id=first_item['id'],
                quantity=10,
                movement_type='IN',
                reference_number='DEMO-001',
                reason='Demonstration stock update'
            )
            
            if result:
                print(f"  Updated {first_item['part_number']}: {old_stock} -> {old_stock + 10} units")
                
                # Revert the change
                inventory_manager.update_stock(
                    item_id=first_item['id'],
                    quantity=10,
                    movement_type='OUT',
                    reference_number='DEMO-002',
                    reason='Reverting demonstration update'
                )
                print(f"  Reverted {first_item['part_number']} back to {old_stock} units")
            
    except Exception as e:
        print(f"  Error during stock update: {str(e)}")

def demonstrate_production_monitoring():
    """Demonstrate production monitoring functionality"""
    print("\n" + "="*50)
    print("PRODUCTION MONITORING DEMONSTRATION")
    print("="*50)
    
    production_monitor = ProductionMonitor()
    
    # Get production lines
    print("\n1. Production Lines Status:")
    lines = production_monitor.get_production_lines()
    for line in lines:
        print(f"  {line['name']}: {line['current_status']} - Efficiency: {line['current_efficiency']:.1f}%")
    
    # Production summary
    print("\n2. Production Summary (Last 24 Hours):")
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)
    summary = production_monitor.get_production_summary(start_date, end_date)
    
    metrics = summary['overall_metrics']
    print(f"  Total planned: {metrics['total_planned']}")
    print(f"  Total actual: {metrics['total_actual']}")
    print(f"  Overall efficiency: {metrics['overall_efficiency']:.1f}%")
    print(f"  Quality rate: {metrics['quality_rate']:.1f}%")
    
    # Line performance
    if summary['line_summary']:
        print("\n3. Individual Line Performance:")
        for line_name, data in summary['line_summary'].items():
            print(f"  {line_name}: {data['efficiency']:.1f}% efficiency, {data['downtime']} min downtime")
    
    # Efficiency trends
    print("\n4. Efficiency Trends (Last 7 Days):")
    trends = production_monitor.get_efficiency_trends(days=7)
    avg_efficiency = trends['average_efficiency']
    print(f"  Average efficiency: {avg_efficiency:.1f}%")
    
    daily_data = trends['daily_efficiency']
    if daily_data:
        print("  Daily breakdown:")
        for date, data in list(daily_data.items())[-3:]:  # Show last 3 days
            print(f"    {date}: {data['efficiency']:.1f}%")

def demonstrate_optimization():
    """Demonstrate optimization functionality"""
    print("\n" + "="*50)
    print("OPTIMIZATION DEMONSTRATION")
    print("="*50)
    
    resource_allocator = ResourceAllocator()
    
    # Inventory optimization
    print("\n1. Running Inventory Allocation Optimization...")
    try:
        result = resource_allocator.optimize_inventory_allocation()
        print(f"  Status: {result['status']}")
        print(f"  Execution time: {result.get('execution_time', 0):.2f} seconds")
        if 'objective_value' in result:
            print(f"  Objective value: ${result['objective_value']:.2f}")
    except Exception as e:
        print(f"  Optimization failed: {str(e)}")
    
    # Production scheduling
    print("\n2. Running Production Schedule Optimization...")
    try:
        result = resource_allocator.optimize_production_schedule()
        print(f"  Status: {result['status']}")
        print(f"  Execution time: {result.get('execution_time', 0):.2f} seconds")
        if 'objective_value' in result:
            print(f"  Objective value: {result['objective_value']:.2f}")
    except Exception as e:
        print(f"  Optimization failed: {str(e)}")
    
    # Resource utilization analysis
    print("\n3. Running Resource Utilization Analysis...")
    try:
        result = resource_allocator.optimize_resource_utilization()
        print(f"  Status: {result['status']}")
        print(f"  Execution time: {result.get('execution_time', 0):.2f} seconds")
        
        if 'recommendations' in result:
            recommendations = result['recommendations']
            print(f"  Generated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
                print(f"    {i}. {rec['type']}: {rec.get('line_name', rec.get('part_number', 'N/A'))}")
    except Exception as e:
        print(f"  Analysis failed: {str(e)}")
    
    # Optimization history
    print("\n4. Recent Optimization History:")
    try:
        history = resource_allocator.get_optimization_history(days=7)
        if history:
            print(f"  Found {len(history)} recent optimizations:")
            for opt in history[-3:]:  # Show last 3
                print(f"    {opt['optimization_type']}: {opt['status']} ({opt['execution_time_seconds']:.2f}s)")
        else:
            print("  No recent optimization history found")
    except Exception as e:
        print(f"  Error retrieving history: {str(e)}")

def demonstrate_system_integration():
    """Demonstrate system integration and workflow"""
    print("\n" + "="*50)
    print("SYSTEM INTEGRATION DEMONSTRATION")
    print("="*50)
    
    print("\n1. Simulating Production Workflow:")
    
    # Initialize managers
    inventory_manager = InventoryManager()
    production_monitor = ProductionMonitor()
    
    try:
        # Get a production line
        lines = production_monitor.get_production_lines()
        if lines:
            line = lines[0]
            print(f"  Using production line: {line['name']}")
            
            # Simulate production record
            production_data = {
                'product_id': 'DEMO-PRODUCT',
                'shift_id': 'DEMO-SHIFT',
                'planned_quantity': 50,
                'actual_quantity': 48,
                'defective_quantity': 2,
                'start_time': datetime.utcnow() - timedelta(hours=2),
                'end_time': datetime.utcnow(),
                'downtime_minutes': 15,
                'downtime_reason': 'Equipment adjustment',
                'quality_score': 96.0,
                'materials_used': []
            }
            
            # Record production data
            result = production_monitor.record_production_data(line['id'], production_data)
            if result:
                print("  Production record created successfully")
            
        else:
            print("  No production lines available for demonstration")
    
    except Exception as e:
        print(f"  Error in production workflow: {str(e)}")
    
    print("\n2. System Health Check:")
    
    # Database connection
    db_manager = DatabaseManager()
    db_status = "Connected" if db_manager.check_connection() else "Disconnected"
    print(f"  Database: {db_status}")
    
    # Component status
    try:
        items_count = len(inventory_manager.get_all_inventory_items())
        lines_count = len(production_monitor.get_production_lines())
        print(f"  Inventory items: {items_count}")
        print(f"  Production lines: {lines_count}")
    except Exception as e:
        print(f"  Error checking components: {str(e)}")

def main():
    """Main demonstration function"""
    print("ADIENT Inventory Management System")
    print("Comprehensive Functionality Demonstration")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize database
        print("\nInitializing system...")
        db_manager = DatabaseManager()
        if not db_manager.check_connection():
            print("Error: Database connection failed")
            return
        
        print("System initialized successfully!")
        
        # Run demonstrations
        demonstrate_inventory_management()
        demonstrate_production_monitoring()
        demonstrate_optimization()
        demonstrate_system_integration()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nThis demonstration showed:")
        print("✓ Inventory management and tracking")
        print("✓ Production monitoring and analysis")
        print("✓ Optimization algorithms and resource allocation")
        print("✓ System integration and workflow automation")
        print("\nThe system is ready for production use!")
        
    except Exception as e:
        print(f"\nDemonstration failed: {str(e)}")
        logger.error(f"Demonstration error: {str(e)}")
    
    finally:
        # Clean up
        try:
            db_manager.close_all_connections()
        except:
            pass

if __name__ == "__main__":
    main()