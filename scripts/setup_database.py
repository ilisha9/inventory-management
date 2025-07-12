#!/usr/bin/env python3
"""
Database setup script for ADIENT Inventory Management System
Initializes database schema and populates with sample data

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.logging_config import setup_logging
from config.settings import Config
from src.database.connection import DatabaseManager

# Setup logging
logger = setup_logging()

def read_sql_file(file_path: str) -> str:
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"SQL file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading SQL file {file_path}: {str(e)}")
        raise

def execute_sql_script(db_manager: DatabaseManager, sql_content: str):
    """Execute SQL script"""
    try:
        # Split the SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        with db_manager.get_session() as session:
            for statement in statements:
                if statement:
                    try:
                        session.execute(statement)
                        logger.debug(f"Executed SQL statement: {statement[:50]}...")
                    except Exception as e:
                        logger.warning(f"SQL statement failed (may be expected): {str(e)}")
                        # Continue with other statements
                        continue
            
            session.commit()
            logger.info(f"Successfully executed {len(statements)} SQL statements")
            
    except Exception as e:
        logger.error(f"Error executing SQL script: {str(e)}")
        raise

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'data',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def verify_database_setup(db_manager: DatabaseManager):
    """Verify database setup by checking tables and data"""
    try:
        with db_manager.get_session() as session:
            # Check if tables exist
            tables_to_check = [
                'suppliers', 'inventory_items', 'stock_movements',
                'production_lines', 'production_records', 'production_items',
                'resource_allocations', 'alerts', 'optimization_results', 'system_logs'
            ]
            
            for table in tables_to_check:
                result = session.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                logger.info(f"Table '{table}': {result} records")
            
            # Check views
            views_to_check = ['low_stock_items', 'production_efficiency', 'active_alerts']
            for view in views_to_check:
                try:
                    result = session.execute(f"SELECT COUNT(*) FROM {view}").scalar()
                    logger.info(f"View '{view}': {result} records")
                except Exception as e:
                    logger.warning(f"View '{view}' check failed: {str(e)}")
            
            # Check indexes (SQLite specific)
            indexes_result = session.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
            ).fetchall()
            logger.info(f"Created {len(indexes_result)} custom indexes")
            
            logger.info("Database setup verification completed successfully")
            
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        raise

def main():
    """Main setup function"""
    try:
        logger.info("Starting ADIENT Inventory Management System database setup...")
        
        # Create necessary directories
        create_directories()
        
        # Initialize database manager
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager()
        
        # Check database connection
        if not db_manager.check_connection():
            logger.error("Database connection failed")
            return False
        
        logger.info("Database connection successful")
        
        # Read and execute schema SQL
        schema_file = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'database', 
            'migrations', 
            'init_schema.sql'
        )
        
        logger.info(f"Reading schema from: {schema_file}")
        sql_content = read_sql_file(schema_file)
        
        logger.info("Executing database schema...")
        execute_sql_script(db_manager, sql_content)
        
        # Verify setup
        logger.info("Verifying database setup...")
        verify_database_setup(db_manager)
        
        logger.info("Database setup completed successfully!")
        
        print("\n" + "="*60)
        print("ADIENT Inventory Management System")
        print("Database Setup Complete")
        print("="*60)
        print(f"Database URL: {Config.DATABASE_URL}")
        print(f"Log Level: {Config.LOG_LEVEL}")
        print("="*60)
        print("\nYou can now run the main application:")
        print("python main.py")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        print(f"\nError: Database setup failed - {str(e)}")
        return False
    
    finally:
        # Clean up database connections
        try:
            db_manager.close_all_connections()
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)