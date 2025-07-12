"""
Data Validation Utilities for ADIENT Inventory Management System
Provides validation functions for various data inputs
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation utility class"""
    
    def __init__(self):
        """Initialize data validator"""
        self.part_number_pattern = re.compile(r'^[A-Z0-9\-]{3,20}$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^[\+]?[1-9][\d]{0,15}$')
        
    def validate_inventory_item(self, data: Dict) -> bool:
        """Validate inventory item data"""
        try:
            required_fields = ['part_number', 'name', 'unit_cost']
            
            # Check required fields
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate part number format
            if not self.part_number_pattern.match(data['part_number']):
                logger.error(f"Invalid part number format: {data['part_number']}")
                return False
            
            # Validate name length
            if len(data['name']) < 3 or len(data['name']) > 200:
                logger.error(f"Invalid name length: {len(data['name'])}")
                return False
            
            # Validate unit cost
            if not isinstance(data['unit_cost'], (int, float)) or data['unit_cost'] < 0:
                logger.error(f"Invalid unit cost: {data['unit_cost']}")
                return False
            
            # Validate stock quantities if provided
            stock_fields = ['current_stock', 'minimum_stock', 'maximum_stock', 'reorder_point', 'reorder_quantity']
            for field in stock_fields:
                if field in data and data[field] is not None:
                    if not isinstance(data[field], int) or data[field] < 0:
                        logger.error(f"Invalid {field}: {data[field]}")
                        return False
            
            # Validate category if provided
            if 'category' in data and data['category']:
                if len(data['category']) > 100:
                    logger.error(f"Category too long: {len(data['category'])}")
                    return False
            
            # Validate unit of measure if provided
            if 'unit_of_measure' in data and data['unit_of_measure']:
                valid_units = ['pieces', 'kg', 'liters', 'meters', 'boxes', 'rolls']
                if data['unit_of_measure'] not in valid_units:
                    logger.warning(f"Non-standard unit of measure: {data['unit_of_measure']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating inventory item: {str(e)}")
            return False
    
    def validate_stock_movement(self, quantity: int, movement_type: str) -> bool:
        """Validate stock movement data"""
        try:
            # Validate quantity
            if not isinstance(quantity, int):
                logger.error(f"Invalid quantity type: {type(quantity)}")
                return False
            
            # For adjustment movements, quantity can be any non-negative value
            # For IN/OUT movements, quantity must be positive
            if movement_type in ['IN', 'OUT'] and quantity <= 0:
                logger.error(f"Invalid quantity for {movement_type} movement: {quantity}")
                return False
            
            if movement_type == 'ADJUSTMENT' and quantity < 0:
                logger.error(f"Invalid quantity for adjustment: {quantity}")
                return False
            
            # Validate movement type
            valid_types = ['IN', 'OUT', 'ADJUSTMENT']
            if movement_type not in valid_types:
                logger.error(f"Invalid movement type: {movement_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating stock movement: {str(e)}")
            return False
    
    def validate_production_data(self, data: Dict) -> bool:
        """Validate production record data"""
        try:
            # Validate quantities
            quantity_fields = ['planned_quantity', 'actual_quantity', 'defective_quantity']
            for field in quantity_fields:
                if field in data and data[field] is not None:
                    if not isinstance(data[field], int) or data[field] < 0:
                        logger.error(f"Invalid {field}: {data[field]}")
                        return False
            
            # Validate defective quantity doesn't exceed actual quantity
            if ('defective_quantity' in data and 'actual_quantity' in data and 
                data['defective_quantity'] is not None and data['actual_quantity'] is not None):
                if data['defective_quantity'] > data['actual_quantity']:
                    logger.error("Defective quantity cannot exceed actual quantity")
                    return False
            
            # Validate downtime minutes
            if 'downtime_minutes' in data and data['downtime_minutes'] is not None:
                if not isinstance(data['downtime_minutes'], int) or data['downtime_minutes'] < 0:
                    logger.error(f"Invalid downtime minutes: {data['downtime_minutes']}")
                    return False
            
            # Validate quality score
            if 'quality_score' in data and data['quality_score'] is not None:
                if not isinstance(data['quality_score'], (int, float)) or not (0 <= data['quality_score'] <= 100):
                    logger.error(f"Invalid quality score: {data['quality_score']}")
                    return False
            
            # Validate timestamps
            time_fields = ['start_time', 'end_time']
            for field in time_fields:
                if field in data and data[field] is not None:
                    if not isinstance(data[field], datetime):
                        try:
                            # Try to parse as ISO string
                            datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            logger.error(f"Invalid {field} format: {data[field]}")
                            return False
            
            # Validate start_time <= end_time if both provided
            if ('start_time' in data and 'end_time' in data and 
                data['start_time'] is not None and data['end_time'] is not None):
                start_time = data['start_time']
                end_time = data['end_time']
                
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                if start_time > end_time:
                    logger.error("Start time cannot be after end time")
                    return False
            
            # Validate product_id if provided
            if 'product_id' in data and data['product_id']:
                if not isinstance(data['product_id'], str) or len(data['product_id']) > 50:
                    logger.error(f"Invalid product_id: {data['product_id']}")
                    return False
            
            # Validate shift_id if provided
            if 'shift_id' in data and data['shift_id']:
                if not isinstance(data['shift_id'], str) or len(data['shift_id']) > 20:
                    logger.error(f"Invalid shift_id: {data['shift_id']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating production data: {str(e)}")
            return False
    
    def validate_supplier_data(self, data: Dict) -> bool:
        """Validate supplier data"""
        try:
            # Check required fields
            if 'name' not in data or not data['name']:
                logger.error("Supplier name is required")
                return False
            
            # Validate name length
            if len(data['name']) < 2 or len(data['name']) > 200:
                logger.error(f"Invalid supplier name length: {len(data['name'])}")
                return False
            
            # Validate email if provided
            if 'email' in data and data['email']:
                if not self.email_pattern.match(data['email']):
                    logger.error(f"Invalid email format: {data['email']}")
                    return False
            
            # Validate phone if provided
            if 'phone' in data and data['phone']:
                # Remove common formatting characters
                clean_phone = re.sub(r'[\s\-\(\)]', '', data['phone'])
                if not self.phone_pattern.match(clean_phone):
                    logger.error(f"Invalid phone format: {data['phone']}")
                    return False
            
            # Validate lead time
            if 'lead_time_days' in data and data['lead_time_days'] is not None:
                if not isinstance(data['lead_time_days'], int) or data['lead_time_days'] < 0:
                    logger.error(f"Invalid lead time: {data['lead_time_days']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating supplier data: {str(e)}")
            return False
    
    def validate_production_line_data(self, data: Dict) -> bool:
        """Validate production line data"""
        try:
            # Check required fields
            required_fields = ['name', 'capacity_per_hour']
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate name
            if len(data['name']) < 3 or len(data['name']) > 100:
                logger.error(f"Invalid name length: {len(data['name'])}")
                return False
            
            # Validate capacity
            if not isinstance(data['capacity_per_hour'], int) or data['capacity_per_hour'] <= 0:
                logger.error(f"Invalid capacity: {data['capacity_per_hour']}")
                return False
            
            # Validate efficiency target if provided
            if 'efficiency_target' in data and data['efficiency_target'] is not None:
                if not isinstance(data['efficiency_target'], (int, float)) or not (0 <= data['efficiency_target'] <= 1):
                    logger.error(f"Invalid efficiency target: {data['efficiency_target']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating production line data: {str(e)}")
            return False
    
    def validate_alert_data(self, data: Dict) -> bool:
        """Validate alert data"""
        try:
            # Check required fields
            required_fields = ['alert_type', 'title', 'message']
            for field in required_fields:
                if field not in data or not data[field]:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate alert type
            valid_types = ['LOW_STOCK', 'PRODUCTION_ISSUE', 'MAINTENANCE', 'QUALITY', 'SYSTEM']
            if data['alert_type'] not in valid_types:
                logger.error(f"Invalid alert type: {data['alert_type']}")
                return False
            
            # Validate severity
            if 'severity' in data and data['severity']:
                valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                if data['severity'] not in valid_severities:
                    logger.error(f"Invalid severity: {data['severity']}")
                    return False
            
            # Validate title length
            if len(data['title']) > 200:
                logger.error(f"Title too long: {len(data['title'])}")
                return False
            
            # Validate message length
            if len(data['message']) > 1000:
                logger.error(f"Message too long: {len(data['message'])}")
                return False
            
            # Validate source type if provided
            if 'source_type' in data and data['source_type']:
                valid_sources = ['INVENTORY', 'PRODUCTION', 'SYSTEM']
                if data['source_type'] not in valid_sources:
                    logger.error(f"Invalid source type: {data['source_type']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating alert data: {str(e)}")
            return False
    
    def validate_date_range(self, start_date: Any, end_date: Any) -> bool:
        """Validate date range"""
        try:
            # Convert strings to datetime if needed
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Check if both are datetime objects
            if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
                logger.error("Invalid date format")
                return False
            
            # Check if start_date <= end_date
            if start_date > end_date:
                logger.error("Start date cannot be after end date")
                return False
            
            # Check if dates are not too far in the future
            now = datetime.utcnow()
            if start_date > now + timedelta(days=365):
                logger.error("Start date too far in the future")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating date range: {str(e)}")
            return False
    
    def sanitize_string(self, value: str, max_length: int = None) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', value)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Apply length limit if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def validate_numeric_range(self, value: Any, min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric value within range"""
        try:
            if not isinstance(value, (int, float)):
                return False
            
            if min_val is not None and value < min_val:
                return False
            
            if max_val is not None and value > max_val:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating numeric range: {str(e)}")
            return False