"""
Inventory Management Module for ADIENT Inventory Management System
Handles stock tracking, reorder management, and automated inventory optimization
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from ..database.connection import get_db_session
from ..database.models import (
    InventoryItem, StockMovement, Supplier, Alert, 
    ProductionItem, ProductionRecord
)
from ..utils.data_validator import DataValidator
from config.settings import Config

logger = logging.getLogger(__name__)

class InventoryManager:
    """Main inventory management class"""
    
    def __init__(self):
        """Initialize inventory manager"""
        self.validator = DataValidator()
        self.low_stock_threshold = Config.LOW_STOCK_THRESHOLD_PERCENTAGE
        self.reorder_safety_factor = Config.REORDER_POINT_SAFETY_FACTOR
        logger.info("Inventory Manager initialized")
    
    def get_all_inventory_items(self) -> List[Dict]:
        """Get all inventory items with current stock information"""
        try:
            with get_db_session() as session:
                items = session.query(InventoryItem).filter(
                    InventoryItem.is_active == True
                ).all()
                
                result = []
                for item in items:
                    stock_info = self._calculate_stock_metrics(item)
                    result.append({
                        'id': item.id,
                        'part_number': item.part_number,
                        'name': item.name,
                        'description': item.description,
                        'category': item.category,
                        'current_stock': item.current_stock,
                        'minimum_stock': item.minimum_stock,
                        'maximum_stock': item.maximum_stock,
                        'reorder_point': item.reorder_point,
                        'unit_cost': item.unit_cost,
                        'location': item.location,
                        'supplier_name': item.supplier.name if item.supplier else None,
                        'stock_status': stock_info['status'],
                        'days_of_supply': stock_info['days_of_supply'],
                        'reorder_needed': stock_info['reorder_needed']
                    })
                
                logger.info(f"Retrieved {len(result)} inventory items")
                return result
                
        except Exception as e:
            logger.error(f"Error getting inventory items: {str(e)}")
            raise
    
    def get_inventory_item(self, item_id: int) -> Optional[Dict]:
        """Get specific inventory item by ID"""
        try:
            with get_db_session() as session:
                item = session.query(InventoryItem).filter(
                    InventoryItem.id == item_id,
                    InventoryItem.is_active == True
                ).first()
                
                if not item:
                    return None
                
                stock_info = self._calculate_stock_metrics(item)
                recent_movements = self._get_recent_movements(session, item_id)
                
                return {
                    'id': item.id,
                    'part_number': item.part_number,
                    'name': item.name,
                    'description': item.description,
                    'category': item.category,
                    'current_stock': item.current_stock,
                    'minimum_stock': item.minimum_stock,
                    'maximum_stock': item.maximum_stock,
                    'reorder_point': item.reorder_point,
                    'reorder_quantity': item.reorder_quantity,
                    'unit_cost': item.unit_cost,
                    'location': item.location,
                    'supplier': {
                        'id': item.supplier.id if item.supplier else None,
                        'name': item.supplier.name if item.supplier else None,
                        'lead_time_days': item.supplier.lead_time_days if item.supplier else None
                    },
                    'stock_metrics': stock_info,
                    'recent_movements': recent_movements
                }
                
        except Exception as e:
            logger.error(f"Error getting inventory item {item_id}: {str(e)}")
            raise
    
    def update_stock(self, item_id: int, quantity: int, movement_type: str, 
                    reference_number: str = None, reason: str = None, 
                    user_id: str = None) -> bool:
        """Update inventory stock levels"""
        try:
            if not self.validator.validate_stock_movement(quantity, movement_type):
                raise ValueError("Invalid stock movement data")
            
            with get_db_session() as session:
                item = session.query(InventoryItem).filter(
                    InventoryItem.id == item_id
                ).first()
                
                if not item:
                    raise ValueError(f"Inventory item {item_id} not found")
                
                # Calculate new stock level
                if movement_type == 'IN':
                    new_stock = item.current_stock + quantity
                elif movement_type == 'OUT':
                    new_stock = item.current_stock - quantity
                    if new_stock < 0:
                        raise ValueError("Insufficient stock for OUT movement")
                elif movement_type == 'ADJUSTMENT':
                    new_stock = quantity
                else:
                    raise ValueError(f"Invalid movement type: {movement_type}")
                
                # Update stock level
                old_stock = item.current_stock
                item.current_stock = new_stock
                item.updated_at = datetime.utcnow()
                
                # Create stock movement record
                movement = StockMovement(
                    inventory_item_id=item_id,
                    movement_type=movement_type,
                    quantity=quantity if movement_type != 'ADJUSTMENT' else (new_stock - old_stock),
                    reference_number=reference_number,
                    reason=reason,
                    user_id=user_id
                )
                session.add(movement)
                
                # Check if alert needed
                self._check_stock_alerts(session, item)
                
                session.commit()
                logger.info(f"Stock updated for item {item_id}: {old_stock} -> {new_stock}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating stock for item {item_id}: {str(e)}")
            raise
    
    def get_low_stock_items(self) -> List[Dict]:
        """Get items with low stock levels"""
        try:
            with get_db_session() as session:
                items = session.query(InventoryItem).filter(
                    InventoryItem.is_active == True,
                    InventoryItem.current_stock <= InventoryItem.reorder_point
                ).all()
                
                result = []
                for item in items:
                    stock_info = self._calculate_stock_metrics(item)
                    result.append({
                        'id': item.id,
                        'part_number': item.part_number,
                        'name': item.name,
                        'current_stock': item.current_stock,
                        'reorder_point': item.reorder_point,
                        'reorder_quantity': item.reorder_quantity,
                        'supplier_name': item.supplier.name if item.supplier else None,
                        'lead_time_days': item.supplier.lead_time_days if item.supplier else 0,
                        'days_of_supply': stock_info['days_of_supply'],
                        'urgency_score': stock_info['urgency_score']
                    })
                
                # Sort by urgency score (highest first)
                result.sort(key=lambda x: x['urgency_score'], reverse=True)
                
                logger.info(f"Found {len(result)} low stock items")
                return result
                
        except Exception as e:
            logger.error(f"Error getting low stock items: {str(e)}")
            raise
    
    def generate_reorder_suggestions(self) -> List[Dict]:
        """Generate automatic reorder suggestions"""
        try:
            low_stock_items = self.get_low_stock_items()
            suggestions = []
            
            for item in low_stock_items:
                # Calculate optimal reorder quantity
                suggested_quantity = self._calculate_optimal_reorder_quantity(item)
                
                suggestions.append({
                    'item_id': item['id'],
                    'part_number': item['part_number'],
                    'name': item['name'],
                    'current_stock': item['current_stock'],
                    'reorder_point': item['reorder_point'],
                    'suggested_quantity': suggested_quantity,
                    'estimated_cost': suggested_quantity * self._get_item_cost(item['id']),
                    'supplier_name': item['supplier_name'],
                    'lead_time_days': item['lead_time_days'],
                    'urgency_score': item['urgency_score']
                })
            
            logger.info(f"Generated {len(suggestions)} reorder suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating reorder suggestions: {str(e)}")
            raise
    
    def get_stock_valuation(self) -> Dict:
        """Calculate total inventory valuation"""
        try:
            with get_db_session() as session:
                items = session.query(InventoryItem).filter(
                    InventoryItem.is_active == True
                ).all()
                
                total_value = 0
                total_items = 0
                category_breakdown = {}
                
                for item in items:
                    item_value = item.current_stock * item.unit_cost
                    total_value += item_value
                    total_items += item.current_stock
                    
                    if item.category:
                        if item.category not in category_breakdown:
                            category_breakdown[item.category] = {
                                'value': 0,
                                'quantity': 0,
                                'items_count': 0
                            }
                        category_breakdown[item.category]['value'] += item_value
                        category_breakdown[item.category]['quantity'] += item.current_stock
                        category_breakdown[item.category]['items_count'] += 1
                
                return {
                    'total_value': round(total_value, 2),
                    'total_items': total_items,
                    'unique_parts': len(items),
                    'category_breakdown': category_breakdown,
                    'calculated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error calculating stock valuation: {str(e)}")
            raise
    
    def get_stock_movement_history(self, item_id: int = None, 
                                  start_date: datetime = None, 
                                  end_date: datetime = None) -> List[Dict]:
        """Get stock movement history"""
        try:
            with get_db_session() as session:
                query = session.query(StockMovement)
                
                if item_id:
                    query = query.filter(StockMovement.inventory_item_id == item_id)
                
                if start_date:
                    query = query.filter(StockMovement.created_at >= start_date)
                
                if end_date:
                    query = query.filter(StockMovement.created_at <= end_date)
                
                movements = query.order_by(StockMovement.created_at.desc()).limit(1000).all()
                
                result = []
                for movement in movements:
                    result.append({
                        'id': movement.id,
                        'item_id': movement.inventory_item_id,
                        'part_number': movement.inventory_item.part_number,
                        'item_name': movement.inventory_item.name,
                        'movement_type': movement.movement_type,
                        'quantity': movement.quantity,
                        'reference_number': movement.reference_number,
                        'reason': movement.reason,
                        'user_id': movement.user_id,
                        'created_at': movement.created_at.isoformat()
                    })
                
                logger.info(f"Retrieved {len(result)} stock movements")
                return result
                
        except Exception as e:
            logger.error(f"Error getting stock movement history: {str(e)}")
            raise
    
    def _calculate_stock_metrics(self, item: InventoryItem) -> Dict:
        """Calculate stock metrics for an item"""
        # Calculate average daily consumption
        avg_daily_consumption = self._calculate_average_consumption(item.id)
        
        # Calculate days of supply
        days_of_supply = 0
        if avg_daily_consumption > 0:
            days_of_supply = item.current_stock / avg_daily_consumption
        
        # Determine stock status
        if item.current_stock <= 0:
            status = 'OUT_OF_STOCK'
        elif item.current_stock <= item.reorder_point:
            status = 'LOW_STOCK'
        elif item.current_stock >= item.maximum_stock:
            status = 'OVERSTOCK'
        else:
            status = 'NORMAL'
        
        # Calculate urgency score (0-100)
        urgency_score = 0
        if item.current_stock <= item.reorder_point:
            urgency_score = max(0, 100 - (item.current_stock / max(item.reorder_point, 1)) * 100)
        
        return {
            'status': status,
            'days_of_supply': round(days_of_supply, 1),
            'avg_daily_consumption': round(avg_daily_consumption, 2),
            'reorder_needed': item.current_stock <= item.reorder_point,
            'urgency_score': round(urgency_score, 1)
        }
    
    def _calculate_average_consumption(self, item_id: int, days: int = 30) -> float:
        """Calculate average daily consumption for an item"""
        try:
            with get_db_session() as session:
                start_date = datetime.utcnow() - timedelta(days=days)
                
                # Get total consumption (OUT movements) in the period
                total_out = session.query(func.sum(StockMovement.quantity)).filter(
                    StockMovement.inventory_item_id == item_id,
                    StockMovement.movement_type == 'OUT',
                    StockMovement.created_at >= start_date
                ).scalar() or 0
                
                return total_out / days
                
        except Exception as e:
            logger.error(f"Error calculating average consumption for item {item_id}: {str(e)}")
            return 0
    
    def _get_recent_movements(self, session: Session, item_id: int, limit: int = 10) -> List[Dict]:
        """Get recent stock movements for an item"""
        movements = session.query(StockMovement).filter(
            StockMovement.inventory_item_id == item_id
        ).order_by(StockMovement.created_at.desc()).limit(limit).all()
        
        return [{
            'movement_type': m.movement_type,
            'quantity': m.quantity,
            'reference_number': m.reference_number,
            'reason': m.reason,
            'created_at': m.created_at.isoformat()
        } for m in movements]
    
    def _check_stock_alerts(self, session: Session, item: InventoryItem):
        """Check and create stock alerts if needed"""
        try:
            # Check for low stock alert
            if item.current_stock <= item.reorder_point:
                # Check if alert already exists
                existing_alert = session.query(Alert).filter(
                    Alert.source_id == str(item.id),
                    Alert.source_type == 'INVENTORY',
                    Alert.alert_type == 'LOW_STOCK',
                    Alert.is_resolved == False
                ).first()
                
                if not existing_alert:
                    alert = Alert(
                        alert_type='LOW_STOCK',
                        severity='HIGH' if item.current_stock <= 0 else 'MEDIUM',
                        title=f"Low Stock Alert: {item.name}",
                        message=f"Stock level ({item.current_stock}) is at or below reorder point ({item.reorder_point})",
                        source_id=str(item.id),
                        source_type='INVENTORY'
                    )
                    session.add(alert)
                    
        except Exception as e:
            logger.error(f"Error checking stock alerts for item {item.id}: {str(e)}")
    
    def _calculate_optimal_reorder_quantity(self, item: Dict) -> int:
        """Calculate optimal reorder quantity using EOQ principles"""
        # Simple reorder quantity calculation
        # In a real system, this would use Economic Order Quantity (EOQ) formula
        base_quantity = item['reorder_quantity']
        current_stock = item['current_stock']
        reorder_point = item['reorder_point']
        
        # Adjust quantity based on current stock deficit
        deficit = max(0, reorder_point - current_stock)
        suggested_quantity = base_quantity + deficit
        
        return suggested_quantity
    
    def _get_item_cost(self, item_id: int) -> float:
        """Get unit cost for an item"""
        try:
            with get_db_session() as session:
                item = session.query(InventoryItem).filter(
                    InventoryItem.id == item_id
                ).first()
                return item.unit_cost if item else 0.0
        except Exception as e:
            logger.error(f"Error getting item cost for {item_id}: {str(e)}")
            return 0.0