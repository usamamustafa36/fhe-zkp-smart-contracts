"""
Blockchain integration components.

This module provides:
- Multi-network blockchain integration (Sepolia, local, mainnet)
- Local blockchain simulator for testing
- Smart contract interfaces
"""

__version__ = '1.0.0'

from blockchain.integration import RealBlockchainIntegration
from blockchain.simulator import get_local_simulator

__all__ = ['RealBlockchainIntegration', 'get_local_simulator']
