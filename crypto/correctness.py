#!/usr/bin/env python3
"""
Correctness Assertions for FHE Operations

THESIS REFERENCE: Chapter 5, Section 5.2 - Correctness Evaluation

CORRECTNESS DEFINITION:
======================
For homomorphic encryption to be correct, decryption must preserve the result
of operations performed on encrypted data:

    decrypt(Enc(x) ⊕ Enc(y)) ≈ f(x, y) ± ε

Where:
- Enc(·) is the encryption function
- ⊕ is the homomorphic operation (addition, multiplication, etc.)
- f(·) is the corresponding plaintext operation
- ε is the approximation error (scheme-dependent)

SCHEME-SPECIFIC CORRECTNESS:
===========================

1. BFV (Exact Integer Arithmetic):
   - ε = 0 for all operations within noise budget
   - decrypt(Enc(x) + Enc(y)) = x + y (exact)
   - decrypt(Enc(x) × Enc(y)) = x × y (exact)
   - Limitation: Noise accumulation → decryption failure

2. CKKS (Approximate Real Arithmetic):
   - ε > 0, depends on global_scale and precision_bits
   - decrypt(Enc(x) + Enc(y)) ≈ x + y ± ε_add
   - decrypt(Enc(x) × Enc(y)) ≈ x × y ± ε_mul
   - ε_mul > ε_add (multiplication introduces more error)

PRECISION PARAMETERS (CKKS):
============================
- global_scale: Scaling factor for encoding (2^40 typical)
- precision_bits: Effective precision in bits (~40 bits ≈ 12 decimal digits)
- poly_modulus_degree: Security parameter (4096, 8192, etc.)

Higher global_scale → Better precision, higher noise
Lower global_scale → Less precision, longer computation chain

NOISE GROWTH:
=============
Each operation increases noise:
- Addition: noise_out ≈ noise_in (minimal growth)
- Multiplication: noise_out ≈ noise_in² (significant growth)
- Depth: Number of multiplications sustainable before decryption fails

ACADEMIC EVALUATION METRICS:
===========================
1. Absolute Error: |decrypt(Enc(op)) - expected|
2. Relative Error: |error| / |expected|
3. Precision Bits: -log₂(relative_error)
4. Success Rate: Percentage of operations within ε tolerance

THESIS REFERENCE MAPPING:
=========================
- Section 3.1.2: FHE Schemes (CKKS/BFV)
- Section 5.2.1: Correctness Assertions
- Section 5.2.2: Precision Analysis
- Section 5.2.3: Noise Growth Evaluation
"""

import numpy as np
from typing import Dict, Tuple, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorrectnessValidator:
    """
    Validates correctness of FHE operations against plaintext ground truth.
    
    THESIS REFERENCE: Chapter 5, Section 5.2
    """
    
    def __init__(self, scheme_name: str = "CKKS", precision_bits: int = 40):
        """
        Initialize correctness validator.
        
        Args:
            scheme_name: FHE scheme ("CKKS" or "BFV")
            precision_bits: Expected precision in bits
        """
        self.scheme = scheme_name
        self.precision_bits = precision_bits
        
        # Scheme-specific error tolerances
        if scheme_name == "BFV":
            self.epsilon_add = 0.0      # Exact arithmetic
            self.epsilon_mul = 0.0      # Exact arithmetic
        elif scheme_name == "CKKS":
            # Approximate arithmetic tolerances
            self.epsilon_add = 1e-6     # Addition error ~10^-6
            self.epsilon_mul = 1e-3     # Multiplication error ~10^-3
        else:
            raise ValueError(f"Unknown scheme: {scheme_name}")
        
        # Statistics tracking    
        self.test_count = 0
        self.pass_count = 0
        self.errors = []
    
    def assert_addition_correctness(
        self, 
        x: float, 
        y: float, 
        result: float,
        custom_epsilon: float = None
    ) -> Tuple[bool, float]:
        """
        Assert FHE addition preserves correctness within epsilon.
        
        Validates: decrypt(Enc(x) + Enc(y)) ≈ (x + y) ± ε
        
        Args:
            x: First plaintext operand
            y: Second plaintext operand
            result: Decrypted result
            custom_epsilon: Override default tolerance
            
        Returns:
            (is_correct, absolute_error) tuple
            
        THESIS REFERENCE: Section 5.2.1 - Addition Correctness
        """
        epsilon = custom_epsilon if custom_epsilon is not None else self.epsilon_add
        expected = x + y
        error = abs(result - expected)
        is_correct = error <= epsilon
        
        self.test_count += 1
        if is_correct:
            self.pass_count += 1
        self.errors.append(error)
        
        if not is_correct:
            logger.warning(
                f"Addition correctness violation: "
                f"|{result} - {expected}| = {error} > ε={epsilon}"
            )
        
        return is_correct, error
    
    def assert_multiplication_correctness(
        self,
        x: float,
        y: float,
        result: float,
        custom_epsilon: float = None
    ) -> Tuple[bool, float]:
        """
        Assert FHE multiplication preserves correctness within epsilon.
        
        Validates: decrypt(Enc(x) × Enc(y)) ≈ (x × y) ±  ε
        
        Note: Multiplication typically has higher error than addition.
        
        THESIS REFERENCE: Section 5.2.1 - Multiplication Correctness
        """
        epsilon = custom_epsilon if custom_epsilon is not None else self.epsilon_mul
        expected = x * y
        error = abs(result - expected)
        
        # Avoid division by zero in relative error
        if abs(expected) > 1e-10:
            relative_error = error / abs(expected)
        else:
            relative_error = error
        
        is_correct = error <= epsilon
        
        self.test_count += 1
        if is_correct:
            self.pass_count += 1
        self.errors.append(error)
        
        if not is_correct:
            logger.warning(
                f"Multiplication correctness violation: "
                f"|{result} - {expected}| = {error} > ε={epsilon} "
                f"(relative: {relative_error:.2e})"
            )
        
        return is_correct, error
    
    def calculate_precision_bits(self, error: float, value: float) -> float:
        """
        Calculate effective precision in bits.
        
        Precision = -log₂(relative_error)
        
        THESIS REFERENCE: Section 5.2.2 - Precision Analysis
        """
        if abs(value) < 1e-10 or error == 0:
            return float('inf')  # Perfect precision
        
        relative_error = error / abs(value)
        precision = -np.log2(relative_error) if relative_error > 0 else float('inf')
        return precision
    
    def get_statistics(self) -> Dict:
        """
        Get correctness validation statistics for thesis reporting.
        
        Returns dictionary with:
        - Total tests
        - Passed tests
        - Success rate
        - Error statistics (mean, std, max)
        - Effective precision
        
        THESIS REFERENCE: Chapter 5, Table 5.1 - Correctness Results
        """
        if self.test_count == 0:
            return {
                'total_tests': 0,
                'passed_tests': 0,
                'success_rate': 0.0,
                'mean_error': 0.0,
                'std_error': 0.0,
                'max_error': 0.0,
                'min_error': 0.0
            }
        
        errors_array = np.array(self.errors)
        
        return {
            'scheme': self.scheme,
            'precision_bits_expected': self.precision_bits,
            'total_tests': self.test_count,
            'passed_tests': self.pass_count,
            'failed_tests': self.test_count - self.pass_count,
            'success_rate': (self.pass_count / self.test_count) * 100,
            'mean_absolute_error': float(np.mean(errors_array)),
            'std_absolute_error': float(np.std(errors_array)),
            'max_absolute_error': float(np.max(errors_array)),
            'min_absolute_error': float(np.min(errors_array)),
            'median_absolute_error': float(np.median(errors_array))
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.test_count = 0
        self.pass_count = 0
        self.errors = []


def document_precision_parameters(fhe_engine) -> Dict:
    """
    Document FHE precision parameters affecting correctness.
    
    Args:
        fhe_engine: AdvancedFHE instance
        
    Returns:
        Dictionary of precision-related parameters
        
    THESIS REFERENCE: Section 5.2.2 - Precision Configuration
    """
    context = fhe_engine.context
    
    params = {
        'scheme': fhe_engine.scheme.value,
        'poly_modulus_degree': context.poly_modulus_degree(),
        'precision_bits_configured': fhe_engine.precision_bits,
    }
    
    # CKKS-specific parameters
    if fhe_engine.scheme.value == "CKKS":
        params.update({
            'global_scale': context.global_scale(),
            'scale_bits': int(np.log2(context.global_scale())),
            'theoretical_precision_decimal': fhe_engine.precision_bits / np.log2(10),  # ~12 digits for 40 bits
            'noise_budget_note': 'Decreases with each multiplication'
        })
    
    # BFV-specific parameters
    elif fhe_engine.scheme.value == "BFV":
        params.update({
            'plain_modulus': context.plain_modulus(),
            'arithmetic_type': 'Exact integer',
            'noise_budget_note': 'Operations consume noise budget; exact until exhausted'
        })
    
    return params


def analyze_noise_growth(operations_chain: List[str]) -> Dict:
    """
    Conceptual analysis of noise growth through operation chain.
    
    This is a THEORETICAL analysis for documentation purposes.
    Actual noise tracking requires access to TenSEAL internals.
    
    Args:
        operations_chain: List of operations ['add', 'mul', 'add', ...]
        
    Returns:
        Estimated noise growth characteristics
        
    THESIS REFERENCE: Section 5.2.3 - Noise Growth Analysis
    """
    addition_count = operations_chain.count('add')
    multiplication_count = operations_chain.count('mul')
    
    # Conceptual noise growth (not actual noise budget)
    # Real analysis requires FHE library internals
    
    return {
        'operation_depth': len(operations_chain),
        'multiplicative_depth': multiplication_count,
        'addition_count': addition_count,
        'multiplication_count': multiplication_count,
        'noise_growth_factor_estimate': 2 ** multiplication_count,  # Exponential in mult depth
        'note': 'Conceptual analysis - actual noise depends on parameters'
    }


# Example usage for thesis evaluation
if __name__ == "__main__":
    print("="*80)
    print("FHE Correctness Validation - Thesis Evaluation Tool")
    print("="*80)
    
    # Create validator
    validator = CorrectnessValidator(scheme_name="CKKS", precision_bits=40)
    
    # Test addition correctness
    print("\nTest 1: Addition Correctness")
    x, y = 100.5, 50.25
    simulated_result = x + y + 1e-7  # Simulate small error
    is_correct, error = validator.assert_addition_correctness(x, y, simulated_result)
    print(f"  {x} + {y} = {simulated_result}")
    print(f"  Error: {error:.2e}")
    print(f"  Status: {'✅ PASS' if is_correct else '❌ FAIL'}")
    
    # Test multiplication correctness
    print("\nTest 2: Multiplication Correctness")
    x, y = 10.5, 5.0
    simulated_result = x * y + 1e-4  # Simulate larger error
    is_correct, error = validator.assert_multiplication_correctness(x, y, simulated_result)
    precision = validator.calculate_precision_bits(error, x * y)
    print(f"  {x} × {y} = {simulated_result}")
    print(f"  Error: {error:.2e}")
    print(f"  Precision: {precision:.1f} bits")
    print(f"  Status: {'✅ PASS' if is_correct else '❌ FAIL'}")
    
    # Get statistics
    print("\nCorrectness Statistics:")
    stats = validator.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.6f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "="*80)
