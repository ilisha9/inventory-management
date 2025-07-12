"""
Database models for ADIENT Inventory Management System
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class InventoryItem(Base):
    """Inventory items table"""
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    part_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit_of_measure = Column(String(20), default='pieces')
    unit_cost = Column(Float, default=0.0)
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=0)
    maximum_stock = Column(Integer, default=1000)
    reorder_point = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    location = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="inventory_items")
    stock_movements = relationship("StockMovement", back_populates="inventory_item")
    production_items = relationship("ProductionItem", back_populates="inventory_item")

class Supplier(Base):
    """Suppliers table"""
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    lead_time_days = Column(Integer, default=7)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="supplier")

class StockMovement(Base):
    """Stock movements table"""
    __tablename__ = 'stock_movements'
    
    id = Column(Integer, primary_key=True)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    movement_type = Column(String(20), nullable=False)  # 'IN', 'OUT', 'ADJUSTMENT'
    quantity = Column(Integer, nullable=False)
    reference_number = Column(String(50))
    reason = Column(String(200))
    user_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="stock_movements")

class ProductionLine(Base):
    """Production lines table"""
    __tablename__ = 'production_lines'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    capacity_per_hour = Column(Integer, default=0)
    efficiency_target = Column(Float, default=0.85)
    is_active = Column(Boolean, default=True)
    maintenance_schedule = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    production_records = relationship("ProductionRecord", back_populates="production_line")
    resource_allocations = relationship("ResourceAllocation", back_populates="production_line")

class ProductionRecord(Base):
    """Production records table"""
    __tablename__ = 'production_records'
    
    id = Column(Integer, primary_key=True)
    production_line_id = Column(Integer, ForeignKey('production_lines.id'), nullable=False)
    product_id = Column(String(50), nullable=False)
    shift_id = Column(String(20))
    planned_quantity = Column(Integer, default=0)
    actual_quantity = Column(Integer, default=0)
    defective_quantity = Column(Integer, default=0)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    efficiency = Column(Float, default=0.0)
    downtime_minutes = Column(Integer, default=0)
    downtime_reason = Column(Text)
    quality_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_line = relationship("ProductionLine", back_populates="production_records")
    production_items = relationship("ProductionItem", back_populates="production_record")

class ProductionItem(Base):
    """Production items table (materials used in production)"""
    __tablename__ = 'production_items'
    
    id = Column(Integer, primary_key=True)
    production_record_id = Column(Integer, ForeignKey('production_records.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    planned_quantity = Column(Integer, default=0)
    actual_quantity = Column(Integer, default=0)
    waste_quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_record = relationship("ProductionRecord", back_populates="production_items")
    inventory_item = relationship("InventoryItem", back_populates="production_items")

class ResourceAllocation(Base):
    """Resource allocation table"""
    __tablename__ = 'resource_allocations'
    
    id = Column(Integer, primary_key=True)
    production_line_id = Column(Integer, ForeignKey('production_lines.id'), nullable=False)
    resource_type = Column(String(50), nullable=False)  # 'LABOR', 'EQUIPMENT', 'MATERIAL'
    resource_id = Column(String(50), nullable=False)
    allocated_quantity = Column(Float, default=0.0)
    allocation_date = Column(DateTime, nullable=False)
    shift_id = Column(String(20))
    status = Column(String(20), default='PLANNED')  # 'PLANNED', 'ACTIVE', 'COMPLETED'
    efficiency_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    production_line = relationship("ProductionLine", back_populates="resource_allocations")

class Alert(Base):
    """Alerts table"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)  # 'LOW_STOCK', 'PRODUCTION_ISSUE', 'MAINTENANCE'
    severity = Column(String(20), default='MEDIUM')  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    source_id = Column(String(50))  # Reference to source item/line
    source_type = Column(String(50))  # 'INVENTORY', 'PRODUCTION', 'SYSTEM'
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(50))
    acknowledged_at = Column(DateTime)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(String(50))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class OptimizationResult(Base):
    """Optimization results table"""
    __tablename__ = 'optimization_results'
    
    id = Column(Integer, primary_key=True)
    optimization_type = Column(String(50), nullable=False)  # 'INVENTORY', 'PRODUCTION', 'RESOURCE'
    parameters = Column(JSON)
    results = Column(JSON)
    objective_value = Column(Float, default=0.0)
    execution_time_seconds = Column(Float, default=0.0)
    status = Column(String(20), default='COMPLETED')  # 'RUNNING', 'COMPLETED', 'FAILED'
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    """System logs table"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    log_level = Column(String(20), nullable=False)  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    module = Column(String(100))
    message = Column(Text, nullable=False)
    user_id = Column(String(50))
    ip_address = Column(String(45))
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def create_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(engine)