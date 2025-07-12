"""
Optimization package for ADIENT Inventory Management System

This package provides advanced optimization algorithms for manufacturing operations including:
- Resource allocation optimization using linear programming
- Production scheduling and sequencing optimization
- Inventory level optimization and reorder point calculation
- Multi-objective optimization for cost, efficiency, and quality
- Constraint-based optimization for complex manufacturing scenarios

Components:
- resource_allocator: Core optimization engine for resource allocation
- production_scheduler: Production scheduling and sequencing algorithms
- algorithms: Optimization algorithms and mathematical models

Optimization Techniques:
- Linear Programming (LP) using PuLP
- Integer Programming for discrete decisions
- Multi-objective optimization
- Constraint satisfaction problems
- Heuristic optimization algorithms

Key Optimization Areas:
- Inventory allocation across production lines
- Production scheduling to minimize makespan
- Resource utilization optimization
- Cost minimization while meeting quality targets
- Capacity planning and bottleneck analysis

Mathematical Models:
- Economic Order Quantity (EOQ) optimization
- Just-In-Time (JIT) inventory models
- Critical Path Method (CPM) for scheduling
- Resource-constrained project scheduling

Author: Hilmi Iliass
Date: March 2022 - June 2022
"""

from .resource_allocator import ResourceAllocator

# Import other components when they are implemented
try:
    from .production_scheduler import ProductionScheduler
except ImportError:
    ProductionScheduler = None

try:
    from .algorithms import OptimizationAlgorithms
except ImportError:
    OptimizationAlgorithms = None

__all__ = [
    'ResourceAllocator',
]

# Add optional components if available
if ProductionScheduler:
    __all__.append('ProductionScheduler')
    
if OptimizationAlgorithms:
    __all__.append('OptimizationAlgorithms')

# Package metadata
__version__ = "1.0.0"
__description__ = "Optimization algorithms and resource allocation for manufacturing systems"

# Optimization configuration constants
DEFAULT_OPTIMIZATION_INTERVAL = 3600  # 1 hour
DEFAULT_MAX_OPTIMIZATION_TIME = 300   # 5 minutes
DEFAULT_OPTIMIZATION_TOLERANCE = 1e-6

# Algorithm selection constants
OPTIMIZATION_METHODS = {
    'LINEAR_PROGRAMMING': 'pulp',
    'INTEGER_PROGRAMMING': 'pulp_integer',
    'MIXED_INTEGER': 'pulp_mixed',
    'HEURISTIC': 'genetic_algorithm',
    'SIMULATED_ANNEALING': 'sa'
}

# Cost factors for optimization
COST_FACTORS = {
    'INVENTORY_HOLDING': 0.2,  # 20% annual holding cost
    'STOCKOUT_PENALTY': 10.0,  # High penalty for stockouts
    'SETUP_COST': 100.0,       # Setup cost per production run
    'OVERTIME_MULTIPLIER': 1.5  # Overtime cost multiplier
}