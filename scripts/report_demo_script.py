#!/usr/bin/env python3
"""
Report Generation Demonstration Script for ADIENT Inventory Management System
Shows how to generate comprehensive reports for inventory, production, and optimization

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.logging_config import setup_logging
from src.database.connection import DatabaseManager
from src.utils.report_generator import ReportGenerator

# Setup logging
logger = setup_logging()

def demonstrate_inventory_reports():
    """Demonstrate inventory report generation"""
    print("\n" + "="*60)
    print("INVENTORY REPORTING DEMONSTRATION")
    print("="*60)
    
    generator = ReportGenerator(output_dir="demo_reports")
    
    try:
        # Generate basic inventory report
        print("\n1. Generating Basic Inventory Report...")
        inventory_report = generator.generate_inventory_report(format="table")
        
        print(f"✅ Report saved: {inventory_report['metadata']['filename']}")
        print(f"📊 Total Items: {inventory_report['summary']['total_items']}")
        print(f"💰 Total Value: ${inventory_report['summary']['total_value']:,.2f}")
        print(f"⚠️  Low Stock Items: {inventory_report['summary']['low_stock_count']}")
        
        # Generate detailed inventory report with movements
        print("\n2. Generating Detailed Inventory Report with Movements...")
        detailed_report = generator.generate_inventory_report(
            format="json",
            include_movements=True,
            date_range=(datetime.utcnow() - timedelta(days=7), datetime.utcnow())
        )
        
        print(f"✅ Detailed report saved: {detailed_report['metadata']['filename']}")
        print(f"📋 Categories analyzed: {len(detailed_report['categories'])}")
        print(f"🚨 Active alerts: {len(detailed_report['alerts'])}")
        
        # Display category breakdown
        if detailed_report['categories']:
            print("\n📊 Category Breakdown:")
            for category, data in detailed_report['categories'].items():
                print(f"   {category}: {data['items_count']} items, ${data['total_value']:,.2f}")
    
    except Exception as e:
        print(f"❌ Error generating inventory reports: {str(e)}")

def demonstrate_production_reports():
    """Demonstrate production report generation"""
    print("\n" + "="*60)
    print("PRODUCTION REPORTING DEMONSTRATION")
    print("="*60)
    
    generator = ReportGenerator(output_dir="demo_reports")
    
    try:
        # Generate production performance report
        print("\n1. Generating Production Performance Report...")
        production_report = generator.generate_production_report(
            format="table",
            date_range=(datetime.utcnow() - timedelta(days=7), datetime.utcnow())
        )
        
        print(f"✅ Report saved: {production_report['metadata']['filename']}")
        print(f"📈 Overall Efficiency: {production_report['summary']['overall_efficiency']:.1f}%")
        print(f"🎯 Quality Rate: {production_report['summary']['quality_rate']:.1f}%")
        print(f"⏱️  Total Downtime: {production_report['summary']['total_downtime_minutes']} minutes")
        
        # Generate line-specific report
        print("\n2. Generating Line-Specific Performance Report...")
        line_report = generator.generate_production_report(
            format="json",
            line_id=1,  # Assembly Line 1
            date_range=(datetime.utcnow() - timedelta(days=30), datetime.utcnow())
        )
        
        print(f"✅ Line report saved: {line_report['metadata']['filename']}")
        
        # Display line performance
        if line_report['line_performance']:
            print("\n🏭 Line Performance Summary:")
            for line_name, data in line_report['line_performance'].items():
                efficiency_status = "✅" if data['efficiency'] >= data['target_efficiency'] else "⚠️"
                print(f"   {efficiency_status} {line_name}: {data['efficiency']:.1f}% efficiency")
                print(f"      Target: {data['target_efficiency']:.1f}%, Variance: {data['efficiency_variance']:+.1f}%")
    
    except Exception as e:
        print(f"❌ Error generating production reports: {str(e)}")

def demonstrate_optimization_reports():
    """Demonstrate optimization report generation"""
    print("\n" + "="*60)
    print("OPTIMIZATION REPORTING DEMONSTRATION")
    print("="*60)
    
    generator = ReportGenerator(output_dir="demo_reports")
    
    try:
        # Generate optimization analysis report
        print("\n1. Generating Optimization Analysis Report...")
        optimization_report = generator.generate_optimization_report(
            format="table",
            days=30
        )
        
        print(f"✅ Report saved: {optimization_report['metadata']['filename']}")
        print(f"🔧 Total Optimizations: {optimization_report['summary']['total_optimizations']}")
        print(f"✅ Success Rate: {optimization_report['summary']['success_rate']:.1f}%")
        print(f"⏱️  Avg Execution Time: {optimization_report['summary']['avg_execution_time']:.2f}s")
        
        # Display performance trends
        if optimization_report['performance_trends']:
            print("\n📈 Optimization Performance by Type:")
            for opt_type, data in optimization_report['performance_trends'].items():
                print(f"   {opt_type.title()}: {data['count']} runs, {data['avg_execution_time']:.2f}s avg")
    
    except Exception as e:
        print(f"❌ Error generating optimization reports: {str(e)}")

def demonstrate_executive_summary():
    """Demonstrate executive summary generation"""
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY DEMONSTRATION")
    print("="*60)
    
    generator = ReportGenerator(output_dir="demo_reports")
    
    try:
        # Generate comprehensive executive summary
        print("\n1. Generating Executive Summary Report...")
        exec_report = generator.generate_executive_summary(format="table")
        
        print(f"✅ Executive summary saved: {exec_report['metadata']['filename']}")
        
        # Display key metrics
        if 'key_metrics' in exec_report:
            print("\n📊 Key Performance Indicators:")
            
            inventory_metrics = exec_report['key_metrics']['inventory']
            print(f"   💰 Inventory Value: ${inventory_metrics['total_value']:,.2f}")
            print(f"   📦 Total Items: {inventory_metrics['items_count']:,}")
            print(f"   ⚠️  Low Stock Alerts: {inventory_metrics['low_stock_alerts']}")
            
            production_metrics = exec_report['key_metrics']['production']
            print(f"   📈 Production Efficiency: {production_metrics['overall_efficiency']:.1f}%")
            print(f"   🎯 Quality Rate: {production_metrics['quality_rate']:.1f}%")
            print(f"   ⏱️  Total Downtime: {production_metrics['total_downtime']} min")
            
            optimization_metrics = exec_report['key_metrics']['optimization']
            print(f"   🔧 Optimization Runs: {optimization_metrics['total_runs']}")
            print(f"   ⚡ Avg Execution Time: {optimization_metrics['avg_execution_time']:.2f}s")
            print(f"   ✅ Success Rate: {optimization_metrics['success_rate']:.1f}%")
        
        # Display recommendations
        if 'recommendations' in exec_report:
            print("\n💡 Executive Recommendations:")
            for i, recommendation in enumerate(exec_report['recommendations'], 1):
                print(f"   {i}. {recommendation}")
    
    except Exception as e:
        print(f"❌ Error generating executive summary: {str(e)}")

def demonstrate_multiple_formats():
    """Demonstrate report generation in multiple formats"""
    print("\n" + "="*60)
    print("MULTIPLE FORMAT DEMONSTRATION")
    print("="*60)
    
    generator = ReportGenerator(output_dir="demo_reports")
    
    formats = ['table', 'json']
    
    # Add Excel and CSV if libraries are available
    try:
        import pandas as pd
        formats.append('csv')
        print("📊 CSV format available")
    except ImportError:
        print("⚠️  CSV format not available (pandas not installed)")
    
    try:
        import openpyxl
        if 'csv' in formats:  # CSV requires pandas too
            formats.append('excel')
            print("📈 Excel format available")
    except ImportError:
        print("⚠️  Excel format not available (openpyxl not installed)")
    
    try:
        print(f"\n🔄 Generating inventory reports in {len(formats)} formats...")
        
        for fmt in formats:
            print(f"   📄 Generating {fmt.upper()} format...")
            report = generator.generate_inventory_report(format=fmt)
            print(f"   ✅ Saved: {os.path.basename(report['metadata']['filename'])}")
    
    except Exception as e:
        print(f"❌ Error generating multiple format reports: {str(e)}")

def main():
    """Main demonstration function"""
    print("ADIENT Inventory Management System")
    print("Report Generation Comprehensive Demonstration")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize database
        print("\n🔧 Initializing system...")
        db_manager = DatabaseManager()
        if not db_manager.check_connection():
            print("❌ Database connection failed")
            return
        
        print("✅ System initialized successfully!")
        
        # Create reports directory
        os.makedirs("demo_reports", exist_ok=True)
        print("📁 Reports directory created")
        
        # Run all demonstrations
        demonstrate_inventory_reports()
        demonstrate_production_reports()
        demonstrate_optimization_reports()
        demonstrate_executive_summary()
        demonstrate_multiple_formats()
        
        print("\n" + "="*70)
        print("✅ REPORT GENERATION DEMONSTRATION COMPLETED")
        print("="*70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📁 All reports saved in: ./demo_reports/")
        print("\n🎯 This demonstration showed:")
        print("   ✅ Comprehensive inventory reporting")
        print("   ✅ Production performance analysis")
        print("   ✅ Optimization results tracking")
        print("   ✅ Executive-level summaries")
        print("   ✅ Multiple output formats (table, JSON, CSV, Excel)")
        print("\n💼 Perfect for:")
        print("   • Management reporting and KPI tracking")
        print("   • Performance analysis and optimization")
        print("   • Compliance and audit documentation")
        print("   • Data export for external systems")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {str(e)}")
        logger.error(f"Report demonstration error: {str(e)}")
    
    finally:
        # Clean up
        try:
            db_manager.close_all_connections()
        except:
            pass

if __name__ == "__main__":
    main()