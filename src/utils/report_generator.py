"""
Report Generation Utilities for ADIENT Inventory Management System
Provides comprehensive reporting functionality for inventory, production, and optimization data

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils.dataframe import dataframe_to_rows
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from tabulate import tabulate
from ..database.connection import get_db_session
from ..database.models import (
    InventoryItem, ProductionLine, ProductionRecord, 
    StockMovement, Alert, OptimizationResult
)

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Comprehensive report generation for all system components"""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Report generator initialized with output directory: {self.output_dir}")
    
    def generate_inventory_report(self, format: str = "table", 
                                include_movements: bool = False,
                                date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        try:
            logger.info("Generating inventory report...")
            
            with get_db_session() as session:
                # Get inventory data
                items = session.query(InventoryItem).filter(
                    InventoryItem.is_active == True
                ).all()
                
                report_data = {
                    'metadata': {
                        'report_type': 'inventory_status',
                        'generated_at': datetime.utcnow().isoformat(),
                        'total_items': len(items),
                        'date_range': date_range
                    },
                    'summary': self._calculate_inventory_summary(items),
                    'items': self._format_inventory_items(items),
                    'categories': self._analyze_inventory_categories(items),
                    'alerts': self._get_inventory_alerts(session)
                }
                
                # Add stock movement history if requested
                if include_movements:
                    report_data['movements'] = self._get_stock_movements(session, date_range)
                
                # Generate output in requested format
                filename = self._save_report(report_data, 'inventory', format)
                report_data['metadata']['filename'] = filename
                
                logger.info(f"Inventory report generated: {filename}")
                return report_data
                
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            raise
    
    def generate_production_report(self, format: str = "table",
                                 line_id: Optional[int] = None,
                                 date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Generate comprehensive production performance report"""
        try:
            logger.info("Generating production report...")
            
            if not date_range:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                date_range = (start_date, end_date)
            
            with get_db_session() as session:
                # Base query for production records
                query = session.query(ProductionRecord).filter(
                    ProductionRecord.created_at >= date_range[0],
                    ProductionRecord.created_at <= date_range[1]
                )
                
                if line_id:
                    query = query.filter(ProductionRecord.production_line_id == line_id)
                
                records = query.all()
                
                # Get production lines
                lines_query = session.query(ProductionLine).filter(
                    ProductionLine.is_active == True
                )
                if line_id:
                    lines_query = lines_query.filter(ProductionLine.id == line_id)
                
                lines = lines_query.all()
                
                report_data = {
                    'metadata': {
                        'report_type': 'production_performance',
                        'generated_at': datetime.utcnow().isoformat(),
                        'date_range': {
                            'start': date_range[0].isoformat(),
                            'end': date_range[1].isoformat()
                        },
                        'line_id': line_id,
                        'total_records': len(records)
                    },
                    'summary': self._calculate_production_summary(records),
                    'line_performance': self._analyze_line_performance(lines, records),
                    'efficiency_trends': self._calculate_efficiency_trends(records),
                    'quality_analysis': self._analyze_quality_metrics(records),
                    'downtime_analysis': self._analyze_downtime(records)
                }
                
                # Generate output in requested format
                filename = self._save_report(report_data, 'production', format)
                report_data['metadata']['filename'] = filename
                
                logger.info(f"Production report generated: {filename}")
                return report_data
                
        except Exception as e:
            logger.error(f"Error generating production report: {str(e)}")
            raise
    
    def generate_optimization_report(self, format: str = "table",
                                   days: int = 30) -> Dict[str, Any]:
        """Generate optimization performance and results report"""
        try:
            logger.info("Generating optimization report...")
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            with get_db_session() as session:
                # Get optimization results
                results = session.query(OptimizationResult).filter(
                    OptimizationResult.created_at >= start_date,
                    OptimizationResult.created_at <= end_date
                ).order_by(OptimizationResult.created_at.desc()).all()
                
                report_data = {
                    'metadata': {
                        'report_type': 'optimization_analysis',
                        'generated_at': datetime.utcnow().isoformat(),
                        'period_days': days,
                        'total_optimizations': len(results)
                    },
                    'summary': self._calculate_optimization_summary(results),
                    'performance_trends': self._analyze_optimization_trends(results),
                    'algorithm_analysis': self._analyze_algorithm_performance(results),
                    'cost_savings': self._calculate_cost_savings(results),
                    'recommendations': self._generate_optimization_recommendations(results)
                }
                
                # Generate output in requested format
                filename = self._save_report(report_data, 'optimization', format)
                report_data['metadata']['filename'] = filename
                
                logger.info(f"Optimization report generated: {filename}")
                return report_data
                
        except Exception as e:
            logger.error(f"Error generating optimization report: {str(e)}")
            raise
    
    def generate_executive_summary(self, format: str = "table") -> Dict[str, Any]:
        """Generate executive summary combining all key metrics"""
        try:
            logger.info("Generating executive summary...")
            
            # Generate component reports
            inventory_report = self.generate_inventory_report(format="json")
            production_report = self.generate_production_report(format="json")
            optimization_report = self.generate_optimization_report(format="json")
            
            # Create executive summary
            report_data = {
                'metadata': {
                    'report_type': 'executive_summary',
                    'generated_at': datetime.utcnow().isoformat(),
                    'period': 'Last 30 days'
                },
                'key_metrics': {
                    'inventory': {
                        'total_value': inventory_report['summary']['total_value'],
                        'items_count': inventory_report['summary']['total_items'],
                        'low_stock_alerts': len([item for item in inventory_report['items'] 
                                               if item['stock_status'] == 'LOW_STOCK'])
                    },
                    'production': {
                        'overall_efficiency': production_report['summary']['overall_efficiency'],
                        'quality_rate': production_report['summary']['quality_rate'],
                        'total_downtime': production_report['summary']['total_downtime_minutes']
                    },
                    'optimization': {
                        'total_runs': optimization_report['summary']['total_optimizations'],
                        'avg_execution_time': optimization_report['summary']['avg_execution_time'],
                        'success_rate': optimization_report['summary']['success_rate']
                    }
                },
                'performance_indicators': self._calculate_kpis(),
                'alerts_summary': self._get_alerts_summary(),
                'recommendations': self._generate_executive_recommendations()
            }
            
            # Generate output in requested format
            filename = self._save_report(report_data, 'executive_summary', format)
            report_data['metadata']['filename'] = filename
            
            logger.info(f"Executive summary generated: {filename}")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            raise
    
    def _calculate_inventory_summary(self, items: List[InventoryItem]) -> Dict[str, Any]:
        """Calculate inventory summary statistics"""
        total_value = sum(item.current_stock * item.unit_cost for item in items)
        total_items = sum(item.current_stock for item in items)
        low_stock_count = sum(1 for item in items if item.current_stock <= item.reorder_point)
        out_of_stock_count = sum(1 for item in items if item.current_stock == 0)
        
        return {
            'total_value': round(total_value, 2),
            'total_items': total_items,
            'unique_parts': len(items),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'avg_stock_value': round(total_value / len(items) if items else 0, 2)
        }
    
    def _format_inventory_items(self, items: List[InventoryItem]) -> List[Dict[str, Any]]:
        """Format inventory items for reporting"""
        formatted_items = []
        
        for item in items:
            stock_status = 'NORMAL'
            if item.current_stock == 0:
                stock_status = 'OUT_OF_STOCK'
            elif item.current_stock <= item.reorder_point:
                stock_status = 'LOW_STOCK'
            elif item.current_stock >= item.maximum_stock:
                stock_status = 'OVERSTOCK'
            
            formatted_items.append({
                'part_number': item.part_number,
                'name': item.name,
                'category': item.category,
                'current_stock': item.current_stock,
                'minimum_stock': item.minimum_stock,
                'reorder_point': item.reorder_point,
                'unit_cost': item.unit_cost,
                'total_value': round(item.current_stock * item.unit_cost, 2),
                'stock_status': stock_status,
                'supplier': item.supplier.name if item.supplier else 'N/A',
                'location': item.location
            })
        
        return formatted_items
    
    def _analyze_inventory_categories(self, items: List[InventoryItem]) -> Dict[str, Any]:
        """Analyze inventory by categories"""
        categories = {}
        
        for item in items:
            category = item.category or 'Uncategorized'
            if category not in categories:
                categories[category] = {
                    'items_count': 0,
                    'total_quantity': 0,
                    'total_value': 0,
                    'avg_unit_cost': 0
                }
            
            categories[category]['items_count'] += 1
            categories[category]['total_quantity'] += item.current_stock
            categories[category]['total_value'] += item.current_stock * item.unit_cost
        
        # Calculate averages
        for category_data in categories.values():
            if category_data['items_count'] > 0:
                category_data['avg_unit_cost'] = round(
                    category_data['total_value'] / category_data['total_quantity']
                    if category_data['total_quantity'] > 0 else 0, 2
                )
            category_data['total_value'] = round(category_data['total_value'], 2)
        
        return categories
    
    def _calculate_production_summary(self, records: List[ProductionRecord]) -> Dict[str, Any]:
        """Calculate production summary statistics"""
        if not records:
            return {
                'total_planned': 0,
                'total_actual': 0,
                'total_defective': 0,
                'overall_efficiency': 0,
                'quality_rate': 0,
                'total_downtime_minutes': 0,
                'records_count': 0
            }
        
        total_planned = sum(r.planned_quantity for r in records)
        total_actual = sum(r.actual_quantity for r in records)
        total_defective = sum(r.defective_quantity for r in records)
        total_downtime = sum(r.downtime_minutes for r in records)
        
        overall_efficiency = (total_actual / total_planned * 100) if total_planned > 0 else 0
        quality_rate = ((total_actual - total_defective) / total_actual * 100) if total_actual > 0 else 0
        
        return {
            'total_planned': total_planned,
            'total_actual': total_actual,
            'total_defective': total_defective,
            'overall_efficiency': round(overall_efficiency, 2),
            'quality_rate': round(quality_rate, 2),
            'total_downtime_minutes': total_downtime,
            'records_count': len(records)
        }
    
    def _analyze_line_performance(self, lines: List[ProductionLine], 
                                records: List[ProductionRecord]) -> Dict[str, Any]:
        """Analyze performance by production line"""
        line_performance = {}
        
        for line in lines:
            line_records = [r for r in records if r.production_line_id == line.id]
            
            if line_records:
                total_planned = sum(r.planned_quantity for r in line_records)
                total_actual = sum(r.actual_quantity for r in line_records)
                total_defective = sum(r.defective_quantity for r in line_records)
                total_downtime = sum(r.downtime_minutes for r in line_records)
                
                efficiency = (total_actual / total_planned * 100) if total_planned > 0 else 0
                quality_rate = ((total_actual - total_defective) / total_actual * 100) if total_actual > 0 else 0
                
                line_performance[line.name] = {
                    'planned': total_planned,
                    'actual': total_actual,
                    'defective': total_defective,
                    'efficiency': round(efficiency, 2),
                    'target_efficiency': line.efficiency_target * 100,
                    'efficiency_variance': round(efficiency - (line.efficiency_target * 100), 2),
                    'quality_rate': round(quality_rate, 2),
                    'downtime_minutes': total_downtime,
                    'records_count': len(line_records)
                }
            else:
                line_performance[line.name] = {
                    'planned': 0, 'actual': 0, 'defective': 0,
                    'efficiency': 0, 'target_efficiency': line.efficiency_target * 100,
                    'efficiency_variance': 0, 'quality_rate': 0,
                    'downtime_minutes': 0, 'records_count': 0
                }
        
        return line_performance
    
    def _save_report(self, report_data: Dict[str, Any], 
                    report_type: str, format: str) -> str:
        """Save report in specified format"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{report_type}_report_{timestamp}"
        
        if format.lower() == "json":
            filename = f"{base_filename}.json"
            filepath = self.output_dir / filename
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        
        elif format.lower() == "csv" and PANDAS_AVAILABLE:
            filename = f"{base_filename}.csv"
            filepath = self.output_dir / filename
            self._save_as_csv(report_data, filepath)
        
        elif format.lower() == "excel" and EXCEL_AVAILABLE and PANDAS_AVAILABLE:
            filename = f"{base_filename}.xlsx"
            filepath = self.output_dir / filename
            self._save_as_excel(report_data, filepath)
        
        else:  # Default to table format
            filename = f"{base_filename}.txt"
            filepath = self.output_dir / filename
            self._save_as_table(report_data, filepath)
        
        return str(filepath)
    
    def _save_as_table(self, report_data: Dict[str, Any], filepath: Path):
        """Save report as formatted table"""
        with open(filepath, 'w') as f:
            f.write(f"ADIENT Inventory Management System\n")
            f.write(f"Report Type: {report_data['metadata']['report_type']}\n")
            f.write(f"Generated: {report_data['metadata']['generated_at']}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write summary
            if 'summary' in report_data:
                f.write("SUMMARY\n")
                f.write("-" * 40 + "\n")
                for key, value in report_data['summary'].items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")
            
            # Write detailed data based on report type
            if 'items' in report_data:
                self._write_table_section(f, "INVENTORY ITEMS", report_data['items'])
            
            if 'line_performance' in report_data:
                self._write_table_section(f, "LINE PERFORMANCE", report_data['line_performance'])
    
    def _write_table_section(self, file, title: str, data):
        """Write a section as formatted table"""
        file.write(f"{title}\n")
        file.write("-" * len(title) + "\n")
        
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            rows = [[str(item.get(h, '')) for h in headers] for item in data]
            table = tabulate(rows, headers=headers, tablefmt='grid')
            file.write(table)
        elif isinstance(data, dict):
            for key, value in data.items():
                file.write(f"{key}: {value}\n")
        
        file.write("\n\n")
    
    def _save_as_csv(self, report_data: Dict[str, Any], filepath: Path):
        """Save report as CSV using pandas"""
        # Implementation for CSV export
        pass
    
    def _save_as_excel(self, report_data: Dict[str, Any], filepath: Path):
        """Save report as Excel using openpyxl"""
        # Implementation for Excel export
        pass
    
    # Additional helper methods for other calculations...
    def _get_inventory_alerts(self, session) -> List[Dict[str, Any]]:
        """Get current inventory-related alerts"""
        alerts = session.query(Alert).filter(
            Alert.source_type == 'INVENTORY',
            Alert.is_resolved == False
        ).all()
        
        return [{
            'id': alert.id,
            'type': alert.alert_type,
            'severity': alert.severity,
            'title': alert.title,
            'created_at': alert.created_at.isoformat()
        } for alert in alerts]
    
    def _get_stock_movements(self, session, date_range: Optional[tuple]) -> List[Dict[str, Any]]:
        """Get stock movement history"""
        query = session.query(StockMovement)
        
        if date_range:
            query = query.filter(
                StockMovement.created_at >= date_range[0],
                StockMovement.created_at <= date_range[1]
            )
        
        movements = query.order_by(StockMovement.created_at.desc()).limit(1000).all()
        
        return [{
            'item_id': m.inventory_item_id,
            'part_number': m.inventory_item.part_number,
            'movement_type': m.movement_type,
            'quantity': m.quantity,
            'reference': m.reference_number,
            'created_at': m.created_at.isoformat()
        } for m in movements]
    
    def _calculate_efficiency_trends(self, records: List[ProductionRecord]) -> Dict[str, Any]:
        """Calculate efficiency trends over time"""
        # Group records by date and calculate daily efficiency
        daily_efficiency = {}
        
        for record in records:
            date_key = record.created_at.date().isoformat()
            if date_key not in daily_efficiency:
                daily_efficiency[date_key] = {'planned': 0, 'actual': 0}
            
            daily_efficiency[date_key]['planned'] += record.planned_quantity
            daily_efficiency[date_key]['actual'] += record.actual_quantity
        
        # Calculate efficiency percentages
        for date_data in daily_efficiency.values():
            if date_data['planned'] > 0:
                date_data['efficiency'] = round(
                    (date_data['actual'] / date_data['planned']) * 100, 2
                )
            else:
                date_data['efficiency'] = 0
        
        return daily_efficiency
    
    def _analyze_quality_metrics(self, records: List[ProductionRecord]) -> Dict[str, Any]:
        """Analyze quality metrics from production records"""
        if not records:
            return {'avg_quality_score': 0, 'defect_rate': 0}
        
        total_quality_score = sum(r.quality_score for r in records if r.quality_score)
        quality_records = [r for r in records if r.quality_score is not None]
        
        total_actual = sum(r.actual_quantity for r in records)
        total_defective = sum(r.defective_quantity for r in records)
        
        avg_quality_score = (total_quality_score / len(quality_records)) if quality_records else 0
        defect_rate = (total_defective / total_actual * 100) if total_actual > 0 else 0
        
        return {
            'avg_quality_score': round(avg_quality_score, 2),
            'defect_rate': round(defect_rate, 2),
            'total_defective': total_defective,
            'quality_records_count': len(quality_records)
        }
    
    def _analyze_downtime(self, records: List[ProductionRecord]) -> Dict[str, Any]:
        """Analyze downtime patterns"""
        if not records:
            return {'total_downtime': 0, 'avg_downtime': 0, 'downtime_incidents': 0}
        
        total_downtime = sum(r.downtime_minutes for r in records)
        downtime_records = [r for r in records if r.downtime_minutes > 0]
        
        return {
            'total_downtime_minutes': total_downtime,
            'avg_downtime_per_record': round(total_downtime / len(records), 2),
            'downtime_incidents': len(downtime_records),
            'downtime_percentage': round(
                (len(downtime_records) / len(records)) * 100, 2
            ) if records else 0
        }
    
    def _calculate_optimization_summary(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Calculate optimization summary statistics"""
        if not results:
            return {
                'total_optimizations': 0,
                'success_rate': 0,
                'avg_execution_time': 0,
                'avg_objective_value': 0
            }
        
        successful = [r for r in results if r.status == 'COMPLETED']
        total_execution_time = sum(r.execution_time_seconds for r in results)
        total_objective_value = sum(r.objective_value for r in successful)
        
        return {
            'total_optimizations': len(results),
            'successful_optimizations': len(successful),
            'success_rate': round((len(successful) / len(results)) * 100, 2),
            'avg_execution_time': round(total_execution_time / len(results), 2),
            'avg_objective_value': round(total_objective_value / len(successful), 2) if successful else 0
        }
    
    def _analyze_optimization_trends(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Analyze optimization performance trends"""
        # Group by optimization type
        type_analysis = {}
        
        for result in results:
            opt_type = result.optimization_type
            if opt_type not in type_analysis:
                type_analysis[opt_type] = {
                    'count': 0,
                    'avg_execution_time': 0,
                    'avg_objective_value': 0,
                    'success_rate': 0
                }
            
            type_analysis[opt_type]['count'] += 1
            type_analysis[opt_type]['avg_execution_time'] += result.execution_time_seconds
            if result.status == 'COMPLETED':
                type_analysis[opt_type]['avg_objective_value'] += result.objective_value
        
        # Calculate averages
        for data in type_analysis.values():
            if data['count'] > 0:
                data['avg_execution_time'] = round(data['avg_execution_time'] / data['count'], 2)
                data['avg_objective_value'] = round(data['avg_objective_value'] / data['count'], 2)
        
        return type_analysis
    
    def _analyze_algorithm_performance(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Analyze algorithm performance characteristics"""
        # Implementation for algorithm analysis
        return {}
    
    def _calculate_cost_savings(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Calculate cost savings from optimization"""
        # Implementation for cost savings calculation
        return {}
    
    def _generate_optimization_recommendations(self, results: List[OptimizationResult]) -> List[str]:
        """Generate recommendations based on optimization results"""
        recommendations = []
        
        if not results:
            recommendations.append("No optimization data available for analysis")
            return recommendations
        
        # Analyze execution times
        avg_execution_time = sum(r.execution_time_seconds for r in results) / len(results)
        if avg_execution_time > 60:  # More than 1 minute
            recommendations.append("Consider optimizing algorithm parameters to reduce execution time")
        
        # Analyze success rate
        success_rate = len([r for r in results if r.status == 'COMPLETED']) / len(results) * 100
        if success_rate < 90:
            recommendations.append("Investigate optimization failures to improve reliability")
        
        return recommendations
    
    def _calculate_kpis(self) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        # Implementation for KPI calculation
        return {}
    
    def _get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of current alerts"""
        # Implementation for alerts summary
        return {}
    
    def _generate_executive_recommendations(self) -> List[str]:
        """Generate executive-level recommendations"""
        return [
            "Continue monitoring inventory accuracy improvements",
            "Focus on production efficiency optimization",
            "Implement predictive maintenance scheduling",
            "Expand optimization to additional production lines"
        ]