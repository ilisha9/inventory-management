"""
Database connection and session management for ADIENT Inventory Management System
"""

import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from config.settings import Config
from .models import Base, create_tables

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager class for handling connections and sessions"""
    
    def __init__(self, database_url=None):
        """Initialize database manager"""
        self.database_url = database_url or Config.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self.Session = None
        self._setup_engine()
        self._setup_session()
    
    def _setup_engine(self):
        """Setup database engine with configuration"""
        try:
            if self.database_url.startswith('sqlite'):
                # SQLite specific configuration
                self.engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={
                        'check_same_thread': False,
                        'timeout': 30
                    },
                    echo=Config.DEBUG
                )
                
                # Enable foreign key support for SQLite
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
                    
            else:
                # PostgreSQL configuration
                self.engine = create_engine(
                    self.database_url,
                    pool_size=Config.DATABASE_POOL_SIZE,
                    max_overflow=Config.DATABASE_MAX_OVERFLOW,
                    pool_pre_ping=True,
                    echo=Config.DEBUG
                )
            
            logger.info(f"Database engine created successfully: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise
    
    def _setup_session(self):
        """Setup database session"""
        try:
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            self.Session = scoped_session(self.SessionLocal)
            logger.info("Database session configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure database session: {str(e)}")
            raise
    
    def initialize_database(self):
        """Initialize database tables and seed data"""
        try:
            # Create tables
            create_tables(self.engine)
            logger.info("Database tables created successfully")
            
            # Seed initial data
            self._seed_initial_data()
            logger.info("Initial data seeded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _seed_initial_data(self):
        """Seed initial data for development/testing"""
        from .models import (
            Supplier, InventoryItem, ProductionLine, 
            Alert, SystemLog
        )
        
        with self.get_session() as session:
            try:
                # Check if data already exists
                if session.query(Supplier).first():
                    return
                
                # Create sample suppliers
                suppliers = [
                    Supplier(
                        name="ADIENT Supplier A",
                        contact_person="John Smith",
                        email="john@suppliera.com",
                        phone="+1-555-0101",
                        address="123 Industrial Ave, Detroit, MI",
                        lead_time_days=5
                    ),
                    Supplier(
                        name="ADIENT Supplier B",
                        contact_person="Jane Doe",
                        email="jane@supplierb.com",
                        phone="+1-555-0102",
                        address="456 Manufacturing St, Chicago, IL",
                        lead_time_days=7
                    )
                ]
                
                for supplier in suppliers:
                    session.add(supplier)
                session.flush()
                
                # Create sample inventory items
                inventory_items = [
                    InventoryItem(
                        part_number="SEAT-001",
                        name="Driver Seat Frame",
                        description="Steel frame for driver seat",
                        category="Seat Components",
                        unit_of_measure="pieces",
                        unit_cost=85.50,
                        current_stock=150,
                        minimum_stock=25,
                        maximum_stock=300,
                        reorder_point=50,
                        reorder_quantity=100,
                        supplier_id=suppliers[0].id,
                        location="Warehouse A-1"
                    ),
                    InventoryItem(
                        part_number="FOAM-002",
                        name="Seat Foam Cushion",
                        description="High-density foam for seat cushioning",
                        category="Seat Components",
                        unit_of_measure="pieces",
                        unit_cost=25.75,
                        current_stock=80,
                        minimum_stock=15,
                        maximum_stock=200,
                        reorder_point=30,
                        reorder_quantity=75,
                        supplier_id=suppliers[1].id,
                        location="Warehouse A-2"
                    ),
                    InventoryItem(
                        part_number="COVER-003",
                        name="Leather Seat Cover",
                        description="Premium leather seat cover",
                        category="Seat Components",
                        unit_of_measure="pieces",
                        unit_cost=120.00,
                        current_stock=45,
                        minimum_stock=10,
                        maximum_stock=150,
                        reorder_point=20,
                        reorder_quantity=50,
                        supplier_id=suppliers[0].id,
                        location="Warehouse B-1"
                    )
                ]
                
                for item in inventory_items:
                    session.add(item)
                session.flush()
                
                # Create sample production lines
                production_lines = [
                    ProductionLine(
                        name="Assembly Line 1",
                        description="Main seat assembly line",
                        capacity_per_hour=25,
                        efficiency_target=0.90,
                        maintenance_schedule="Weekly"
                    ),
                    ProductionLine(
                        name="Assembly Line 2",
                        description="Secondary seat assembly line",
                        capacity_per_hour=20,
                        efficiency_target=0.85,
                        maintenance_schedule="Bi-weekly"
                    ),
                    ProductionLine(
                        name="Quality Control Line",
                        description="Final quality inspection line",
                        capacity_per_hour=30,
                        efficiency_target=0.95,
                        maintenance_schedule="Monthly"
                    )
                ]
                
                for line in production_lines:
                    session.add(line)
                
                session.commit()
                logger.info("Sample data created successfully")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to seed initial data: {str(e)}")
                raise
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_scoped_session(self):
        """Get scoped session for thread-safe operations"""
        return self.Session()
    
    def remove_scoped_session(self):
        """Remove scoped session"""
        self.Session.remove()
    
    def close_all_connections(self):
        """Close all database connections"""
        try:
            if self.engine:
                self.engine.dispose()
            if self.Session:
                self.Session.remove()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
    
    def check_connection(self):
        """Check database connection health"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    def execute_raw_query(self, query, params=None):
        """Execute raw SQL query"""
        try:
            with self.get_session() as session:
                result = session.execute(query, params or {})
                return result.fetchall()
        except Exception as e:
            logger.error(f"Raw query execution failed: {str(e)}")
            raise

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db_session():
    """Get database session"""
    return db_manager.get_session()

def get_scoped_session():
    """Get scoped database session"""
    return db_manager.get_scoped_session()

def close_db_connections():
    """Close all database connections"""
    db_manager.close_all_connections()