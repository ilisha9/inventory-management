# ADIENT Inventory Management System

**Enterprise inventory management system developed during ADIENT internship (March-June 2022)**

## Project Overview

Automated inventory management system built for ADIENT automotive manufacturing facility in Kénitra, Morocco. Manages 4 production lines and 500+ inventory items with real-time monitoring and optimization.


## Features

### Inventory Management
- Real-time stock tracking and monitoring
- Automated reorder suggestions with cost analysis
- Low stock alerts with urgency scoring
- Multi-location inventory support
- Comprehensive valuation reporting

### Production Monitoring
- Live production line status tracking
- OEE and efficiency calculations
- Quality metrics and defect tracking
- Downtime analysis with root causes
- Performance benchmarking

### Optimization Engine
- Linear programming for resource allocation
- Production scheduling optimization
- Cost minimization algorithms
- Capacity planning and bottleneck analysis

### Command Line Interface
- Interactive CLI for system control
- Real-time reporting with formatted output
- System health monitoring
- Automated optimization execution

## Technology Stack

- **Backend**: Python 3.8+, SQLAlchemy ORM
- **Database**: SQLite/PostgreSQL
- **Optimization**: PuLP Linear Programming, SciPy
- **CLI**: Custom interface with tabulate formatting
- **Testing**: pytest with comprehensive coverage

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/adient-inventory-system.git
cd adient-inventory-system

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python scripts/setup_database.py

# Run demonstration
python scripts/run_example.py
```

## Usage Examples

### CLI Commands
```bash
# Inventory operations
python main.py inventory status
python main.py inventory low-stock
python main.py inventory reorder

# Production monitoring
python main.py production status
python main.py production summary

# Optimization
python main.py optimize inventory
python main.py optimize production
```

### Programmatic Usage
```python
from src.inventory import InventoryManager
from src.production import ProductionMonitor
from src.optimization import ResourceAllocator

# Initialize components
inventory = InventoryManager()
production = ProductionMonitor()
optimizer = ResourceAllocator()

# Get insights
items = inventory.get_all_inventory_items()
efficiency = production.get_efficiency_trends(days=7)
result = optimizer.optimize_inventory_allocation()
```

## System Architecture

**Core Components:**
- **Inventory Manager**: Stock tracking and reorder logic
- **Production Monitor**: Real-time line performance analysis
- **Resource Allocator**: Linear programming optimization
- **Data Validator**: Input validation and safety checks
- **CLI Interface**: Command-line user interaction

## Database Schema

**Key Tables:**
- inventory_items: Parts, stock levels, suppliers
- production_lines: Capacity, efficiency targets
- production_records: Output, quality, downtime
- stock_movements: Transaction audit trail
- alerts: Notifications and priorities

## Project Structure

```
adient-inventory-system/
├── main.py                     # Application entry
├── requirements.txt            # Dependencies
├── config/                     # Configuration
├── src/
│   ├── database/              # Models & connection
│   ├── inventory/             # Stock management
│   ├── production/            # Line monitoring
│   ├── optimization/          # Algorithms
│   ├── cli/                   # Interface
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── scripts/                   # Setup tools
```

## Testing

```bash
# Run all tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific module
pytest tests/test_inventory.py
```

## Performance Metrics

**System Performance:**
- Database queries: <50ms average
- Optimization runtime: 1-5 seconds
- Real-time updates: 1-minute intervals
- Alert generation: <2 seconds

**Business Impact:**
- 500+ inventory items managed
- 4 production lines monitored
- 24/7 operation coverage
- 98% inventory accuracy achieved

## Industrial Application

**ADIENT Implementation:**
- Automotive seat manufacturing
- 4 production lines (Assembly Line 1 & 2, QC, Packaging)
- 500+ SKUs (frames, foam, covers, fasteners)
- 3-shift operations (24/7 manufacturing)
- Multiple suppliers with optimized lead times

**Manufacturing Challenges Solved:**
- Complex BOM management for automotive seats
- Just-in-time delivery coordination
- Multi-line resource allocation
- Quality defect tracking and analysis
- Maintenance scheduling integration

## Skills Demonstrated

**Technical:**
- Database design and optimization
- Linear programming algorithms
- Real-time system monitoring
- CLI application development
- Manufacturing process integration

**Business:**
- Industrial automation knowledge
- Manufacturing domain expertise
- Performance optimization
- Cost reduction strategies
- Process improvement methodologies

## About This Project

This system was developed during my 3-month internship at ADIENT, a global automotive seating manufacturer. The project demonstrates practical application of software engineering in industrial environments, with measurable business impact and production deployment.

**Key Achievements:**
- Real-world deployment in automotive manufacturing
- Quantified performance improvements
- Professional development practices
- Industry-standard methodologies

## Contact

**Hilmi Iliass**
- Email: ilihilmi13@gmail.com
- Phone: +44 7902 464227
- Location: Cardiff, United Kingdom

## License

MIT License - see LICENSE file for details.

---

*This project represents practical intersection of software engineering and manufacturing excellence, showcasing real-world industrial automation experience.*