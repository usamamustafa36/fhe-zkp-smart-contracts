"""
Core cryptographic components for privacy-preserving smart contracts.

This module provides:
- FHE (Fully Homomorphic Encryption) engine with CKKS/BFV schemes
- Entropy analysis for security validation
- ZKP (Zero-Knowledge Proof) input validation
- Privacy-preserving contract framework
"""

__version__ = '1.0.0'
__author__ = 'Master\'s Thesis Project'

from core.fhe_engine import AdvancedFHE, FHEScheme
from core.entropy import shannon_entropy

__all__ = ['AdvancedFHE', 'FHEScheme', 'shannon_entropy']
