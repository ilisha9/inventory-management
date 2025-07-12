"""
Resource Allocation and Optimization Module for ADIENT Inventory Management System
Handles optimization algorithms for resource allocation and production scheduling
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from pulp import *
from sqlalchemy import func, and_

from ..database.connection import get_db_session
from ..database.models import (
    ProductionLine, InventoryItem, ProductionRecord, 
    ResourceAllocation, OptimizationResult, Alert
)
from ..utils.data_validator import DataValidator
from config.settings import Config

logger = logging.getLogger(__name__)

class ResourceAllocator:
    """Resource allocation and optimization engine"""
    
    def __init__(self):
        """Initialize resource allocator"""
        self.validator = DataValidator()
        self.optimization_interval = Config.OPTIMIZATION_INTERVAL
        self.max_optimization_time = Config.MAX_OPTIMIZATION_TIME
        self.is_running = False
        self.optimization_thread = None
        logger.info("Resource Allocator initialized")
    
    def run_periodic_optimization(self):
        """Start periodic optimization tasks"""
        if self.is_running:
            logger.warning("Optimization already running")
            return
        
        self.is_running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        logger.info("Periodic optimization started")
    
    def stop_optimization(self):
        """Stop periodic optimization"""
        self.is_running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=10)
        logger.info("Periodic optimization stopped")
    
    def _optimization_loop(self):
        """Main optimization loop"""
        while self.is_running:
            try:
                self.optimize_inventory_allocation()
                self.optimize_production_schedule()
                time.sleep(self.optimization_interval)
            except Exception as e:
                logger.error(f"Error in optimization loop: {str(e)}")
                time.sleep(self.optimization_interval)
    
    def optimize_inventory_allocation(self) -> Dict:
        """Optimize inventory allocation across production lines"""
        try:
            start_time = time.time()
            logger.info("Starting inventory allocation optimization")
            
            with get_db_session() as session:
                # Get current inventory and production data
                inventory_data = self._get_inventory_data(session)
                production_data = self._get_production_requirements(session)
                
                if not inventory_data or not production_data:
                    logger.warning("Insufficient data for inventory optimization")
                    return {'status': 'failed', 'reason': 'insufficient_data'}
                
                # Setup optimization problem
                prob = LpProblem("Inventory_Allocation", LpMinimize)
                
                # Decision variables: allocation[item][line] = quantity
                allocation_vars = {}
                for item_id in inventory_data:
                    allocation_vars[item_id] = {}
                    for line_id in production_data:
                        var_name = f"alloc_{item_id}_{line_id}"
                        allocation_vars[item_id][line_id] = LpVariable(
                            var_name, lowBound=0, cat='Integer'
                        )
                
                # Objective: Minimize total allocation cost and waste
                objective = 0
                for item_id in inventory_data:
                    item_cost = inventory_data[item_id]['unit_cost']
                    for line_id in production_data:
                        # Cost of allocation + penalty for overallocation
                        objective += (
                            item_cost * allocation_vars[item_id][line_id] +
                            0.1 * item_cost * allocation_vars[item_id][line_id]  # waste penalty
                        )
                
                prob += objective
                
                # Constraints
                # 1. Don't allocate more than available stock
                for item_id in inventory_data:
                    available_stock = inventory_data[item_id]['current_stock']
                    total_allocated = lpSum([
                        allocation_vars[item_id][line_id] 
                        for line_id in production_data
                    ])
                    prob += total_allocated <= available_stock
                
                # 2. Meet minimum production requirements
                for line_id in production_data:
                    for item_id in production_data[line_id].get('required_items', {}):
                        min_required = production_data[line_id]['required_items'][item_id]
                        if item_id in allocation_vars:
                            prob += allocation_vars[item_id][line_id] >= min_required
                
                # Solve the problem
                prob.solve(PULP_CBC_CMD(msg=0, timeLimit=self.max_optimization_time))
                
                # Extract results
                if prob.status == LpStatusOptimal:
                    allocation_results = self._extract_allocation_results(
                        allocation_vars, inventory_data, production_data
                    )
                    
                    # Save optimization results
                    self._save_optimization_result(
                        session, 'INVENTORY', prob, allocation_results, start_time
                    )
                    
                    # Apply allocations
                    self._apply_inventory_allocations(session, allocation_results)
                    
                    execution_time = time.time() - start_time
                    logger.info(f"Inventory optimization completed in {execution_time:.2f}s")
                    
                    return {
                        'status': 'success',
                        'objective_value': value(prob.objective),
                        'execution_time': execution_time,
                        'allocations': allocation_results
                    }
                else:
                    logger.warning("Inventory optimization failed to find optimal solution")
                    return {'status': 'failed', 'reason': 'no_optimal_solution'}
                
        except Exception as e:
            logger.error(f"Error in inventory allocation optimization: {str(e)}")
            raise
    
    def optimize_production_schedule(self) -> Dict:
        """Optimize production scheduling across lines"""
        try:
            start_time = time.time()
            logger.info("Starting production schedule optimization")
            
            with get_db_session() as session:
                # Get production lines and their capabilities
                lines_data = self._get_production_lines_data(session)
                jobs_data = self._get_pending_jobs_data(session)
                
                if not lines_data or not jobs_data:
                    logger.warning("Insufficient data for production scheduling")
                    return {'status': 'failed', 'reason': 'insufficient_data'}
                
                # Setup optimization problem
                prob = LpProblem("Production_Schedule", LpMinimize)
                
                # Decision variables: schedule[job][line][time_slot] = 1 if job assigned
                schedule_vars = {}
                time_slots = list(range(24))  # 24 hour slots
                
                for job_id in jobs_data:
                    schedule_vars[job_id] = {}
                    for line_id in lines_data:
                        schedule_vars[job_id][line_id] = {}
                        for slot in time_slots:
                            var_name = f"sched_{job_id}_{line_id}_{slot}"
                            schedule_vars[job_id][line_id][slot] = LpVariable(
                                var_name, cat='Binary'
                            )
                
                # Objective: Minimize completion time and setup costs
                objective = 0
                for job_id in jobs_data:
                    job_priority = jobs_data[job_id].get('priority', 1)
                    for line_id in lines_data:
                        setup_cost = lines_data[line_id].get('setup_cost', 10)
                        for slot in time_slots:
                            # Minimize completion time (later slots cost more)
                            # Higher priority jobs get lower cost multiplier
                            time_cost = slot * (2 - job_priority)
                            objective += (
                                (time_cost + setup_cost) * 
                                schedule_vars[job_id][line_id][slot]
                            )
                
                prob += objective
                
                # Constraints
                # 1. Each job must be assigned to exactly one line and time slot
                for job_id in jobs_data:
                    total_assignments = lpSum([
                        schedule_vars[job_id][line_id][slot]
                        for line_id in lines_data
                        for slot in time_slots
                    ])
                    prob += total_assignments == 1
                
                # 2. Each line can handle only one job per time slot
                for line_id in lines_data:
                    for slot in time_slots:
                        slot_assignments = lpSum([
                            schedule_vars[job_id][line_id][slot]
                            for job_id in jobs_data
                        ])
                        prob += slot_assignments <= 1
                
                # 3. Line capacity constraints
                for line_id in lines_data:
                    line_capacity = lines_data[line_id]['capacity_per_hour']
                    for slot in time_slots:
                        slot_demand = lpSum([
                            jobs_data[job_id]['quantity'] * 
                            schedule_vars[job_id][line_id][slot]
                            for job_id in jobs_data
                        ])
                        prob += slot_demand <= line_capacity
                
                # Solve the problem
                prob.solve(PULP_CBC_CMD(msg=0, timeLimit=self.max_optimization_time))
                
                # Extract results
                if prob.status == LpStatusOptimal:
                    schedule_results = self._extract_schedule_results(
                        schedule_vars, jobs_data, lines_data
                    )
                    
                    # Save optimization results
                    self._save_optimization_result(
                        session, 'PRODUCTION', prob, schedule_results, start_time
                    )
                    
                    # Apply schedule
                    self._apply_production_schedule(session, schedule_results)
                    
                    execution_time = time.time() - start_time
                    logger.info(f"Production scheduling completed in {execution_time:.2f}s")
                    
                    return {
                        'status': 'success',
                        'objective_value': value(prob.objective),
                        'execution_time': execution_time,
                        'schedule': schedule_results
                    }
                else:
                    logger.warning("Production scheduling failed to find optimal solution")
                    return {'status': 'failed', 'reason': 'no_optimal_solution'}
                
        except Exception as e:
            logger.error(f"Error in production schedule optimization: {str(e)}")
            raise
    
    def optimize_resource_utilization(self) -> Dict:
        """Optimize overall resource utilization"""
        try:
            start_time = time.time()
            logger.info("Starting resource utilization optimization")
            
            with get_db_session() as session:
                # Get current resource utilization data
                utilization_data = self._get_resource_utilization_data(session)
                
                if not utilization_data:
                    return {'status': 'failed', 'reason': 'no_data'}
                
                # Calculate optimization recommendations
                recommendations = []
                
                # Analyze line efficiency
                for line_data in utilization_data['lines']:
                    current_efficiency = line_data['current_efficiency']
                    target_efficiency = line_data['target_efficiency']
                    
                    if current_efficiency < target_efficiency * 0.9:  # 90% of target
                        recommendations.append({
                            'type': 'efficiency_improvement',
                            'line_id': line_data['line_id'],
                            'line_name': line_data['line_name'],
                            'current_efficiency': current_efficiency,
                            'target_efficiency': target_efficiency,
                            'improvement_potential': target_efficiency - current_efficiency,
                            'recommended_actions': [
                                'Review maintenance schedule',
                                'Optimize material flow',
                                'Training for operators'
                            ]
                        })
                
                # Analyze inventory optimization
                for item_data in utilization_data['inventory']:
                    turnover_rate = item_data.get('turnover_rate', 0)
                    
                    if turnover_rate < 4:  # Less than 4 times per year
                        recommendations.append({
                            'type': 'inventory_optimization',
                            'item_id': item_data['item_id'],
                            'part_number': item_data['part_number'],
                            'current_stock': item_data['current_stock'],
                            'turnover_rate': turnover_rate,
                            'recommended_actions': [
                                'Reduce stock levels',
                                'Review reorder points',
                                'Consider just-in-time delivery'
                            ]
                        })
                
                execution_time = time.time() - start_time
                
                # Save results
                optimization_result = {
                    'recommendations': recommendations,
                    'total_recommendations': len(recommendations),
                    'utilization_metrics': utilization_data
                }
                
                self._save_optimization_result(
                    session, 'RESOURCE', None, optimization_result, start_time
                )
                
                logger.info(f"Resource utilization optimization completed with {len(recommendations)} recommendations")
                
                return {
                    'status': 'success',
                    'execution_time': execution_time,
                    'recommendations': recommendations,
                    'metrics': utilization_data
                }
                
        except Exception as e:
            logger.error(f"Error in resource utilization optimization: {str(e)}")
            raise
    
    def get_optimization_history(self, optimization_type: str = None, 
                               days: int = 7) -> List[Dict]:
        """Get optimization history"""
        try:
            with get_db_session() as session:
                start_date = datetime.utcnow() - timedelta(days=days)
                
                query = session.query(OptimizationResult).filter(
                    OptimizationResult.created_at >= start_date
                )
                
                if optimization_type:
                    query = query.filter(
                        OptimizationResult.optimization_type == optimization_type
                    )
                
                results = query.order_by(
                    OptimizationResult.created_at.desc()
                ).all()
                
                history = []
                for result in results:
                    history.append({
                        'id': result.id,
                        'optimization_type': result.optimization_type,
                        'objective_value': result.objective_value,
                        'execution_time_seconds': result.execution_time_seconds,
                        'status': result.status,
                        'created_at': result.created_at.isoformat(),
                        'results_summary': self._summarize_results(result.results)
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting optimization history: {str(e)}")
            raise
    
    def _get_inventory_data(self, session) -> Dict:
        """Get current inventory data for optimization"""
        items = session.query(InventoryItem).filter(
            InventoryItem.is_active == True
        ).all()
        
        inventory_data = {}
        for item in items:
            inventory_data[item.id] = {
                'part_number': item.part_number,
                'current_stock': item.current_stock,
                'unit_cost': item.unit_cost,
                'reorder_point': item.reorder_point
            }
        
        return inventory_data
    
    def _get_production_requirements(self, session) -> Dict:
        """Get production requirements for active lines"""
        lines = session.query(ProductionLine).filter(
            ProductionLine.is_active == True
        ).all()
        
        production_data = {}
        for line in lines:
            # Get recent production to estimate requirements
            recent_records = session.query(ProductionRecord).filter(
                ProductionRecord.production_line_id == line.id,
                ProductionRecord.created_at >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            # Estimate required items based on recent production
            required_items = {}
            if recent_records:
                avg_production = sum(r.actual_quantity for r in recent_records) / len(recent_records)
                # Simplified: assume each unit requires certain materials
                required_items = {1: int(avg_production * 0.8), 2: int(avg_production * 0.6)}
            
            production_data[line.id] = {
                'name': line.name,
                'capacity_per_hour': line.capacity_per_hour,
                'required_items': required_items
            }
        
        return production_data
    
    def _get_production_lines_data(self, session) -> Dict:
        """Get production lines data for scheduling"""
        lines = session.query(ProductionLine).filter(
            ProductionLine.is_active == True
        ).all()
        
        lines_data = {}
        for line in lines:
            lines_data[line.id] = {
                'name': line.name,
                'capacity_per_hour': line.capacity_per_hour,
                'efficiency_target': line.efficiency_target,
                'setup_cost': 10  # Simplified setup cost
            }
        
        return lines_data
    
    def _get_pending_jobs_data(self, session) -> Dict:
        """Get pending production jobs"""
        # Simplified: create sample jobs for demonstration
        jobs_data = {
            1: {'quantity': 100, 'priority': 1, 'due_date': datetime.utcnow() + timedelta(hours=8)},
            2: {'quantity': 150, 'priority': 2, 'due_date': datetime.utcnow() + timedelta(hours=12)},
            3: {'quantity': 75, 'priority': 1, 'due_date': datetime.utcnow() + timedelta(hours=6)}
        }
        
        return jobs_data
    
    def _get_resource_utilization_data(self, session) -> Dict:
        """Get current resource utilization data"""
        # Get production line utilization
        lines = session.query(ProductionLine).filter(
            ProductionLine.is_active == True
        ).all()
        
        lines_utilization = []
        for line in lines:
            # Calculate recent efficiency
            recent_records = session.query(ProductionRecord).filter(
                ProductionRecord.production_line_id == line.id,
                ProductionRecord.created_at >= datetime.utcnow() - timedelta(days=1)
            ).all()
            
            current_efficiency = 0
            if recent_records:
                total_planned = sum(r.planned_quantity for r in recent_records)
                total_actual = sum(r.actual_quantity for r in recent_records)
                if total_planned > 0:
                    current_efficiency = (total_actual / total_planned) * 100
            
            lines_utilization.append({
                'line_id': line.id,
                'line_name': line.name,
                'current_efficiency': current_efficiency,
                'target_efficiency': line.efficiency_target * 100
            })
        
        # Get inventory utilization
        items = session.query(InventoryItem).filter(
            InventoryItem.is_active == True
        ).all()
        
        inventory_utilization = []
        for item in items:
            # Calculate turnover rate (simplified)
            turnover_rate = 4  # Placeholder
            
            inventory_utilization.append({
                'item_id': item.id,
                'part_number': item.part_number,
                'current_stock': item.current_stock,
                'turnover_rate': turnover_rate
            })
        
        return {
            'lines': lines_utilization,
            'inventory': inventory_utilization
        }
    
    def _extract_allocation_results(self, allocation_vars, inventory_data, production_data) -> Dict:
        """Extract allocation results from optimization variables"""
        results = {}
        
        for item_id in allocation_vars:
            results[item_id] = {}
            for line_id in allocation_vars[item_id]:
                allocated_qty = value(allocation_vars[item_id][line_id])
                if allocated_qty > 0:
                    results[item_id][line_id] = {
                        'allocated_quantity': int(allocated_qty),
                        'item_info': inventory_data[item_id],
                        'line_info': production_data[line_id]
                    }
        
        return results
    
    def _extract_schedule_results(self, schedule_vars, jobs_data, lines_data) -> Dict:
        """Extract schedule results from optimization variables"""
        results = {}
        
        for job_id in schedule_vars:
            for line_id in schedule_vars[job_id]:
                for slot in schedule_vars[job_id][line_id]:
                    if value(schedule_vars[job_id][line_id][slot]) == 1:
                        if job_id not in results:
                            results[job_id] = {}
                        
                        results[job_id] = {
                            'assigned_line': line_id,
                            'assigned_slot': slot,
                            'job_info': jobs_data[job_id],
                            'line_info': lines_data[line_id],
                            'scheduled_time': datetime.utcnow() + timedelta(hours=slot)
                        }
                        break
        
        return results
    
    def _save_optimization_result(self, session, opt_type: str, prob, results: Dict, start_time: float):
        """Save optimization results to database"""
        try:
            execution_time = time.time() - start_time
            objective_value = value(prob.objective) if prob else 0
            
            optimization_result = OptimizationResult(
                optimization_type=opt_type,
                parameters={'optimization_time': execution_time},
                results=results,
                objective_value=objective_value,
                execution_time_seconds=execution_time,
                status='COMPLETED'
            )
            
            session.add(optimization_result)
            session.commit()
            
            logger.info(f"Optimization result saved for type: {opt_type}")
            
        except Exception as e:
            logger.error(f"Error saving optimization result: {str(e)}")
    
    def _apply_inventory_allocations(self, session, allocation_results: Dict):
        """Apply inventory allocation results"""
        try:
            for item_id, allocations in allocation_results.items():
                for line_id, allocation_data in allocations.items():
                    allocated_qty = allocation_data['allocated_quantity']
                    
                    # Create resource allocation record
                    resource_allocation = ResourceAllocation(
                        production_line_id=line_id,
                        resource_type='MATERIAL',
                        resource_id=str(item_id),
                        allocated_quantity=allocated_qty,
                        allocation_date=datetime.utcnow(),
                        status='PLANNED'
                    )
                    
                    session.add(resource_allocation)
            
            session.commit()
            logger.info("Inventory allocations applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying inventory allocations: {str(e)}")
            session.rollback()
    
    def _apply_production_schedule(self, session, schedule_results: Dict):
        """Apply production schedule results"""
        try:
            for job_id, schedule_data in schedule_results.items():
                line_id = schedule_data['assigned_line']
                scheduled_time = schedule_data['scheduled_time']
                
                # Create resource allocation for scheduled job
                resource_allocation = ResourceAllocation(
                    production_line_id=line_id,
                    resource_type='LABOR',
                    resource_id=f'job_{job_id}',
                    allocated_quantity=1,
                    allocation_date=scheduled_time,
                    status='PLANNED'
                )
                
                session.add(resource_allocation)
            
            session.commit()
            logger.info("Production schedule applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying production schedule: {str(e)}")
            session.rollback()
    
    def _summarize_results(self, results: Dict) -> Dict:
        """Create summary of optimization results"""
        if not results:
            return {}
        
        summary = {
            'total_items': len(results),
            'optimization_type': 'unknown'
        }
        
        # Detect result type and create appropriate summary
        if 'recommendations' in results:
            summary.update({
                'optimization_type': 'resource_utilization',
                'total_recommendations': results.get('total_recommendations', 0)
            })
        elif any('allocated_quantity' in str(results).lower() for _ in [1]):
            summary.update({
                'optimization_type': 'inventory_allocation',
                'total_allocations': len([
                    alloc for item_allocs in results.values() 
                    for alloc in item_allocs.values()
                ])
            })
        elif any('assigned_line' in str(results).lower() for _ in [1]):
            summary.update({
                'optimization_type': 'production_schedule',
                'total_jobs_scheduled': len(results)
            })
        
        return summary