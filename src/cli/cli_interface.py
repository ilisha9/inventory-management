"""
Command Line Interface for ADIENT Inventory Management System
Provides CLI access to system functionality without web interface

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from tabulate import tabulate

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.logging_config import setup_logging
from src.inventory.inventory_manager import InventoryManager
from src.production.production_monitor import ProductionMonitor
from src.optimization.resource_allocator import ResourceAllocator
from src.database.connection import DatabaseManager

logger = setup_logging()

class ADIENTCLIInterface:
    """Command line interface for ADIENT system"""
    
    def __init__(self):
        """Initialize CLI interface"""
        self.inventory_manager = InventoryManager()
        self.production_monitor = ProductionMonitor()
        self.resource_allocator = ResourceAllocator()
        self.db_manager = DatabaseManager()
        
        print("ADIENT Inventory Management System - CLI Interface")
        print("=" * 60)
    
    def inventory_status(self, args):
        """Display inventory status"""
        try:
            items = self.inventory_manager.get_all_inventory_items()
            
            if not items:
                print("No inventory items found.")
                return
            
            # Format data for table
            table_data = []
            for item in items:
                table_data.append([
                    item['part_number'],
                    item['name'][:30],  # Truncate long names
                    item['current_stock'],
                    item['minimum_stock'],
                    item['stock_status'],
                    f"${item['unit_cost']:.2f}",
                    item['supplier_name'] or 'N/A'
                ])
            
            headers = ['Part Number', 'Name', 'Stock', 'Min Stock', 'Status', 'Unit Cost', 'Supplier']
            print("\nInventory Status:")
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
            # Summary statistics
            total_items = len(items)
            low_stock_count = sum(1 for item in items if item['stock_status'] == 'LOW_STOCK')
            out_of_stock_count = sum(1 for item in items if item['stock_status'] == 'OUT_OF_STOCK')
            
            print(f"\nSummary:")
            print(f"Total Items: {total_items}")
            print(f"Low Stock: {low_stock_count}")
            print(f"Out of Stock: {out_of_stock_count}")
            
        except Exception as e:
            print(f"Error retrieving inventory status: {str(e)}")
    
    def low_stock_report(self, args):
        """Display low stock report"""
        try:
            low_stock_items = self.inventory_manager.get_low_stock_items()
            
            if not low_stock_items:
                print("No low stock items found.")
                return
            
            # Format data for table
            table_data = []
            for item in low_stock_items:
                table_data.append([
                    item['part_number'],
                    item['name'][:25],
                    item['current_stock'],
                    item['reorder_point'],
                    item['reorder_quantity'],
                    f"{item['urgency_score']:.1f}%",
                    item['supplier_name'] or 'N/A'
                ])
            
            headers = ['Part Number', 'Name', 'Current', 'Reorder Point', 'Reorder Qty', 'Urgency', 'Supplier']
            print("\nLow Stock Report:")
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
        except Exception as e:
            print(f"Error generating low stock report: {str(e)}")
    
    def reorder_suggestions(self, args):
        """Display reorder suggestions"""
        try:
            suggestions = self.inventory_manager.generate_reorder_suggestions()
            
            if not suggestions:
                print("No reorder suggestions at this time.")
                return
            
            # Format data for table
            table_data = []
            total_cost = 0
            for suggestion in suggestions:
                cost = suggestion['estimated_cost']
                total_cost += cost
                table_data.append([
                    suggestion['part_number'],
                    suggestion['name'][:25],
                    suggestion['current_stock'],
                    suggestion['suggested_quantity'],
                    f"${cost:.2f}",
                    f"{suggestion['lead_time_days']} days",
                    suggestion['supplier_name'] or 'N/A'
                ])
            
            headers = ['Part Number', 'Name', 'Current', 'Suggested Qty', 'Est. Cost', 'Lead Time', 'Supplier']
            print("\nReorder Suggestions:")
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            print(f"\nTotal Estimated Cost: ${total_cost:.2f}")
            
        except Exception as e:
            print(f"Error generating reorder suggestions: {str(e)}")
    
    def stock_valuation(self, args):
        """Display stock valuation"""
        try:
            valuation = self.inventory_manager.get_stock_valuation()
            
            print("\nStock Valuation Report:")
            print("=" * 40)
            print(f"Total Inventory Value: ${valuation['total_value']:,.2f}")
            print(f"Total Items in Stock: {valuation['total_items']:,}")
            print(f"Unique Part Numbers: {valuation['unique_parts']}")
            print(f"Calculated At: {valuation['calculated_at']}")
            
            # Category breakdown
            if valuation['category_breakdown']:
                print("\nCategory Breakdown:")
                table_data = []
                for category, data in valuation['category_breakdown'].items():
                    table_data.append([
                        category,
                        data['items_count'],
                        data['quantity'],
                        f"${data['value']:,.2f}"
                    ])
                
                headers = ['Category', 'Items', 'Quantity', 'Value']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
        except Exception as e:
            print(f"Error calculating stock valuation: {str(e)}")
    
    def production_status(self, args):
        """Display production status"""
        try:
            lines = self.production_monitor.get_production_lines()
            
            if not lines:
                print("No production lines found.")
                return
            
            # Format data for table
            table_data = []
            for line in lines:
                table_data.append([
                    line['name'],
                    line['current_status'],
                    f"{line['current_efficiency']:.1f}%",
                    f"{line['efficiency_target']*100:.1f}%",
                    line['daily_production'],
                    f"{line['downtime_minutes']} min"
                ])
            
            headers = ['Line Name', 'Status', 'Current Eff.', 'Target Eff.', 'Daily Prod.', 'Downtime']
            print("\nProduction Status:")
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
        except Exception as e:
            print(f"Error retrieving production status: {str(e)}")
    
    def production_summary(self, args):
        """Display production summary"""
        try:
            # Get summary for last 24 hours by default
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=1)
            
            summary = self.production_monitor.get_production_summary(start_date, end_date)
            
            print("\nProduction Summary (Last 24 Hours):")
            print("=" * 50)
            
            metrics = summary['overall_metrics']
            print(f"Total Planned: {metrics['total_planned']}")
            print(f"Total Actual: {metrics['total_actual']}")
            print(f"Total Defective: {metrics['total_defective']}")
            print(f"Overall Efficiency: {metrics['overall_efficiency']:.1f}%")
            print(f"Quality Rate: {metrics['quality_rate']:.1f}%")
            print(f"Total Downtime: {metrics['total_downtime_minutes']} minutes")
            
            # Line breakdown
            if summary['line_summary']:
                print("\nLine Performance:")
                table_data = []
                for line_name, data in summary['line_summary'].items():
                    table_data.append([
                        line_name,
                        data['planned'],
                        data['actual'],
                        data['defective'],
                        f"{data['efficiency']:.1f}%",
                        f"{data['downtime']} min"
                    ])
                
                headers = ['Line', 'Planned', 'Actual', 'Defective', 'Efficiency', 'Downtime']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
        except Exception as e:
            print(f"Error generating production summary: {str(e)}")
    
    def update_stock(self, args):
        """Update stock levels"""
        try:
            result = self.inventory_manager.update_stock(
                item_id=args.item_id,
                quantity=args.quantity,
                movement_type=args.movement_type.upper(),
                reference_number=args.reference,
                reason=args.reason
            )
            
            if result:
                print(f"Stock updated successfully for item {args.item_id}")
                print(f"Movement: {args.movement_type.upper()} {args.quantity}")
                if args.reference:
                    print(f"Reference: {args.reference}")
                if args.reason:
                    print(f"Reason: {args.reason}")
            else:
                print("Stock update failed")
                
        except Exception as e:
            print(f"Error updating stock: {str(e)}")
    
    def run_optimization(self, args):
        """Run optimization algorithms"""
        try:
            opt_type = args.type.lower()
            
            print(f"Starting {opt_type} optimization...")
            
            if opt_type == 'inventory':
                result = self.resource_allocator.optimize_inventory_allocation()
            elif opt_type == 'production':
                result = self.resource_allocator.optimize_production_schedule()
            elif opt_type == 'resource':
                result = self.resource_allocator.optimize_resource_utilization()
            else:
                print(f"Unknown optimization type: {opt_type}")
                return
            
            print(f"Optimization completed!")
            print(f"Status: {result['status']}")
            print(f"Execution time: {result.get('execution_time', 0):.2f} seconds")
            
            if 'objective_value' in result:
                print(f"Objective value: {result['objective_value']:.2f}")
            
            if 'recommendations' in result:
                print(f"Recommendations generated: {len(result['recommendations'])}")
                
        except Exception as e:
            print(f"Error running optimization: {str(e)}")
    
    def generate_report(self, args):
        """Generate comprehensive reports"""
        try:
            from ..utils.report_generator import ReportGenerator
            
            generator = ReportGenerator()
            
            report_type = args.report_type.lower()
            output_format = getattr(args, 'format', 'table')
            
            print(f"Generating {report_type} report in {output_format} format...")
            
            if report_type == 'inventory':
                result = generator.generate_inventory_report(
                    format=output_format,
                    include_movements=getattr(args, 'include_movements', False)
                )
            elif report_type == 'production':
                result = generator.generate_production_report(
                    format=output_format,
                    line_id=getattr(args, 'line_id', None)
                )
            elif report_type == 'optimization':
                result = generator.generate_optimization_report(
                    format=output_format,
                    days=getattr(args, 'days', 30)
                )
            elif report_type == 'executive':
                result = generator.generate_executive_summary(
                    format=output_format
                )
            else:
                print(f"Unknown report type: {report_type}")
                return
            
            print(f"Report generated successfully!")
            print(f"File saved: {result['metadata']['filename']}")
            
            # Display summary if table format
            if output_format == 'table' and 'summary' in result:
                print("\nReport Summary:")
                print("=" * 40)
                for key, value in result['summary'].items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
                
        except Exception as e:
            print(f"Error generating report: {str(e)}")
    
    def system_status(self, args):
        """Display system status"""
        try:
            print("\nADIENT System Status:")
            print("=" * 40)
            
            # Database status
            db_status = "Connected" if self.db_manager.check_connection() else "Disconnected"
            print(f"Database: {db_status}")
            
            # Get recent system activity
            inventory_items = self.inventory_manager.get_all_inventory_items()
            production_lines = self.production_monitor.get_production_lines()
            
            print(f"Inventory Items: {len(inventory_items)}")
            print(f"Production Lines: {len(production_lines)}")
            
            # Check for active alerts
            low_stock_items = self.inventory_manager.get_low_stock_items()
            print(f"Low Stock Alerts: {len(low_stock_items)}")
            
            print(f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"Error retrieving system status: {str(e)}")

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='ADIENT Inventory Management System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s inventory status              # Show inventory status
  %(prog)s inventory low-stock           # Show low stock items
  %(prog)s inventory reorder             # Show reorder suggestions
  %(prog)s inventory valuation           # Show stock valuation
  %(prog)s inventory update 1 50 IN      # Add 50 units to item 1
  %(prog)s production status             # Show production status
  %(prog)s production summary            # Show production summary
  %(prog)s optimize inventory            # Run inventory optimization
  %(prog)s system status                 # Show system status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Inventory commands
    inventory_parser = subparsers.add_parser('inventory', help='Inventory management')
    inventory_subparsers = inventory_parser.add_subparsers(dest='inventory_action')
    
    inventory_subparsers.add_parser('status', help='Show inventory status')
    inventory_subparsers.add_parser('low-stock', help='Show low stock items')
    inventory_subparsers.add_parser('reorder', help='Show reorder suggestions')
    inventory_subparsers.add_parser('valuation', help='Show stock valuation')
    
    update_parser = inventory_subparsers.add_parser('update', help='Update stock levels')
    update_parser.add_argument('item_id', type=int, help='Inventory item ID')
    update_parser.add_argument('quantity', type=int, help='Quantity to add/remove')
    update_parser.add_argument('movement_type', choices=['IN', 'OUT', 'ADJUSTMENT'], help='Movement type')
    update_parser.add_argument('--reference', help='Reference number')
    update_parser.add_argument('--reason', help='Reason for movement')
    
    # Production commands
    production_parser = subparsers.add_parser('production', help='Production management')
    production_subparsers = production_parser.add_subparsers(dest='production_action')
    
    production_subparsers.add_parser('status', help='Show production status')
    production_subparsers.add_parser('summary', help='Show production summary')
    
    # Optimization commands
    optimize_parser = subparsers.add_parser('optimize', help='Run optimization')
    optimize_parser.add_argument('type', choices=['inventory', 'production', 'resource'], help='Optimization type')
    
    # System commands
    subparsers.add_parser('system', help='System status').add_subparsers().add_parser('status', help='Show system status')
    
    return parser

def main():
    """Main CLI function"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        cli = ADIENTCLIInterface()
        
        # Route commands
        if args.command == 'inventory':
            if args.inventory_action == 'status':
                cli.inventory_status(args)
            elif args.inventory_action == 'low-stock':
                cli.low_stock_report(args)
            elif args.inventory_action == 'reorder':
                cli.reorder_suggestions(args)
            elif args.inventory_action == 'valuation':
                cli.stock_valuation(args)
            elif args.inventory_action == 'update':
                cli.update_stock(args)
            else:
                print("Unknown inventory action")
        
        elif args.command == 'production':
            if args.production_action == 'status':
                cli.production_status(args)
            elif args.production_action == 'summary':
                cli.production_summary(args)
            else:
                print("Unknown production action")
        
        elif args.command == 'optimize':
            cli.run_optimization(args)
        
        elif args.command == 'system':
            cli.system_status(args)
        
        else:
            print(f"Unknown command: {args.command}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"CLI error: {str(e)}")

if __name__ == "__main__":
    main()