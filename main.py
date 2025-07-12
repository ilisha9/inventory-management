"""
ADIENT Inventory Management System
Main application entry point (CLI version)

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
import logging
from datetime import datetime
from threading import Thread

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.logging_config import setup_logging
from config.settings import Config
from src.database.connection import DatabaseManager
from src.inventory.inventory_manager import InventoryManager
from src.production.production_monitor import ProductionMonitor
from src.optimization.resource_allocator import ResourceAllocator
from src.cli.cli_interface import main as cli_main

# Setup logging
logger = setup_logging()

def initialize_system():
    """Initialize the inventory management system"""
    logger.info("Starting ADIENT Inventory Management System...")
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        logger.info("Database initialized successfully")
        
        # Initialize core components
        inventory_manager = InventoryManager()
        production_monitor = ProductionMonitor()
        resource_allocator = ResourceAllocator()
        
        logger.info("Core components initialized successfully")
        
        return {
            'inventory_manager': inventory_manager,
            'production_monitor': production_monitor,
            'resource_allocator': resource_allocator,
            'db_manager': db_manager
        }
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise

def start_background_tasks(components):
    """Start background monitoring and optimization tasks"""
    logger.info("Starting background tasks...")
    
    def production_monitoring():
        """Background task for production monitoring"""
        try:
            monitor = components['production_monitor']
            monitor.start_monitoring()
        except Exception as e:
            logger.error(f"Production monitoring error: {str(e)}")
    
    def inventory_optimization():
        """Background task for inventory optimization"""
        try:
            allocator = components['resource_allocator']
            allocator.run_periodic_optimization()
        except Exception as e:
            logger.error(f"Inventory optimization error: {str(e)}")
    
    # Start background threads
    prod_thread = Thread(target=production_monitoring, daemon=True)
    opt_thread = Thread(target=inventory_optimization, daemon=True)
    
    prod_thread.start()
    opt_thread.start()
    
    logger.info("Background tasks started successfully")

def main():
    """Main application entry point"""
    try:
        # Check if CLI arguments provided
        if len(sys.argv) > 1:
            # Run CLI interface
            cli_main()
            return
        
        # Initialize system components
        components = initialize_system()
        
        # Start background tasks
        start_background_tasks(components)
        
        print("\n" + "="*60)
        print("ADIENT Inventory Management System")
        print("="*60)
        
        # Keep the system running
        try:
            while True:
                import time
                time.sleep(10)
                # Optionally print periodic status updates
                
        except KeyboardInterrupt:
            logger.info("Application shutdown requested by user")
            print("\nShutting down gracefully...")
            
            # Stop background tasks
            components['production_monitor'].stop_monitoring()
            components['resource_allocator'].stop_optimization()
            
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            print(f"Error: {str(e)}")
            
    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user")
        print("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main())
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {Config.DATABASE_URL}")
        print("="*60)
        print("\nSystem is running with background monitoring...")
        print("Available CLI commands:")
        print("  python main.py inventory status      - Show inventory status")
        print("  python main.py production status     - Show production status")  
        print("  python main.py optimize inventory    - Run inventory optimization")
        print("  python main.py system status         - Show system status")
        print("\nPress Ctrl+C to stop the system")
        print("="*60"""
ADIENT Inventory Management System
Main application entry point

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

import sys
import os
import logging
from datetime import datetime
from threading import Thread

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.logging_config import setup_logging
from config.settings import Config
from src.database.connection import DatabaseManager
from src.dashboard.app import create_app
from src.inventory.inventory_manager import InventoryManager
from src.production.production_monitor import ProductionMonitor
from src.optimization.resource_allocator import ResourceAllocator
from src.utils.data_validator import DataValidator

# Setup logging
logger = setup_logging()

def initialize_system():
    """Initialize the inventory management system"""
    logger.info("Starting ADIENT Inventory Management System...")
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        logger.info("Database initialized successfully")
        
        # Initialize core components
        inventory_manager = InventoryManager()
        production_monitor = ProductionMonitor()
        resource_allocator = ResourceAllocator()
        
        logger.info("Core components initialized successfully")
        
        return {
            'inventory_manager': inventory_manager,
            'production_monitor': production_monitor,
            'resource_allocator': resource_allocator,
            'db_manager': db_manager
        }
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise

def start_background_tasks(components):
    """Start background monitoring and optimization tasks"""
    logger.info("Starting background tasks...")
    
    def production_monitoring():
        """Background task for production monitoring"""
        try:
            monitor = components['production_monitor']
            monitor.start_monitoring()
        except Exception as e:
            logger.error(f"Production monitoring error: {str(e)}")
    
    def inventory_optimization():
        """Background task for inventory optimization"""
        try:
            allocator = components['resource_allocator']
            allocator.run_periodic_optimization()
        except Exception as e:
            logger.error(f"Inventory optimization error: {str(e)}")
    
    # Start background threads
    prod_thread = Thread(target=production_monitoring, daemon=True)
    opt_thread = Thread(target=inventory_optimization, daemon=True)
    
    prod_thread.start()
    opt_thread.start()
    
    logger.info("Background tasks started successfully")

def main():
    """Main application entry point"""
    try:
        # Initialize system components
        components = initialize_system()
        
        # Start background tasks
        start_background_tasks(components)
        
        # Create and run Flask app
        app = create_app()
        
        logger.info("Starting web dashboard...")
        print("\n" + "="*50)
        print("ADIENT Inventory Management System")
        print("="*50)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Dashboard available at: http://localhost:5000")
        print("API documentation at: http://localhost:5000/api/docs")
        print("="*50)
        
        # Run the application
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user")
        print("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()