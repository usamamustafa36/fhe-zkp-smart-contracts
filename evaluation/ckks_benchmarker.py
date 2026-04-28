#!/usr/bin/env python3
"""
CKKS/FHE Performance Benchmarker

Measures comprehensive CKKS performance metrics for thesis:
- Encryption/decryption time
- Homomorphic addition/multiplication latency
- Ciphertext size
- Noise budget tracking
- Approximation error
"""

import time
import sys
import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from crypto.fhe_engine import AdvancedFHE, FHEScheme


class CKKSBenchmarker:
    """Comprehensive CKKS performance benchmarking for thesis."""
    
    def __init__(self, iterations: int = 10):
        """
        Initialize CKKS benchmarker.
        
        Args:
            iterations: Number of measurement iterations per test
        """
        self.iterations = iterations
        self.fhe = AdvancedFHE(scheme=FHEScheme.CKKS, precision_bits=40)
        self.results = []
        
        print(f"CKKS Benchmarker initialized (iterations={iterations})")
    
    def benchmark_encryption(self, n_values: int = 100) -> Dict:
        """Benchmark encryption time."""
        print(f"\n[CKKS] Encryption benchmark (n={n_values})...")
        
        values = [float(i) for i in range(n_values)]
        latencies = []
        
        for i in range(self.iterations):
            start = time.time()
            encrypted = self.fhe.encrypt_batch_optimized(values)
            latency = time.time() - start
            latencies.append(latency)
        
        result = {
            'operation': 'encryption',
            'n_values': n_values,
            'mean_time_sec': float(np.mean(latencies)),
            'std_time_sec': float(np.std(latencies)),
            'time_per_value_ms': float(np.mean(latencies) / n_values * 1000),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"  Mean: {result['mean_time_sec']:.4f}s ({result['time_per_value_ms']:.3f}ms/value)")
        return result
    
    def benchmark_decryption(self, n_values: int = 100) -> Dict:
        """Benchmark decryption time."""
        print(f"\n[CKKS] Decryption benchmark (n={n_values})...")
        
        values = [float(i) for i in range(n_values)]
        encrypted = self.fhe.encrypt_batch_optimized(values)
        
        latencies = []
        for i in range(self.iterations):
            start = time.time()
            decrypted = self.fhe.decrypt_batch_optimized(encrypted)
            latency = time.time() - start
            latencies.append(latency)
        
        result = {
            'operation': 'decryption',
            'n_values': n_values,
            'mean_time_sec': float(np.mean(latencies)),
            'std_time_sec': float(np.std(latencies)),
            'time_per_value_ms': float(np.mean(latencies) / n_values * 1000),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"  Mean: {result['mean_time_sec']:.4f}s ({result['time_per_value_ms']:.3f}ms/value)")
        return result
    
    def benchmark_addition(self, n_operations: int = 100) -> Dict:
        """Benchmark homomorphic addition."""
        print(f"\n[CKKS] Addition benchmark (n={n_operations})...")
        
        values_a = [float(i) for i in range(n_operations)]
        values_b = [float(i+1) for i in range(n_operations)]
        
        enc_a = self.fhe.encrypt_batch_optimized(values_a)
        enc_b = self.fhe.encrypt_batch_optimized(values_b)
        
        latencies = []
        for i in range(self.iterations):
            start = time.time()
            result_enc = self.fhe.add_encrypted_batch_optimized(enc_a, enc_b)
            latency = time.time() - start
            latencies.append(latency)
        
        result = {
            'operation': 'addition',
            'n_operations': n_operations,
            'mean_time_sec': float(np.mean(latencies)),
            'std_time_sec': float(np.std(latencies)),
            'time_per_op_ms': float(np.mean(latencies) / n_operations * 1000),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"  Mean: {result['mean_time_sec']:.4f}s ({result['time_per_op_ms']:.3f}ms/op)")
        return result
    
    def benchmark_multiplication(self, n_operations: int = 50) -> Dict:
        """Benchmark homomorphic multiplication."""
        print(f"\n[CKKS] Multiplication benchmark (n={n_operations})...")
        
        values_a = [float(i+1) for i in range(n_operations)]
        values_b = [2.0 for _ in range(n_operations)]
        
        enc_a = self.fhe.encrypt_batch_optimized(values_a)
        enc_b = self.fhe.encrypt_batch_optimized(values_b)
        
        latencies = []
        for i in range(self.iterations):
            start = time.time()
            try:
                result_enc = self.fhe.multiply_encrypted_batch(enc_a, enc_b)
                latency = time.time() - start
                latencies.append(latency)
            except Exception as e:
                print(f"  Warning: Multiplication failed - {e}")
                break
        
        if latencies:
            result = {
                'operation': 'multiplication',
                'n_operations': n_operations,
                'mean_time_sec': float(np.mean(latencies)),
                'std_time_sec': float(np.std(latencies)),
                'time_per_op_ms': float(np.mean(latencies) / n_operations * 1000),
                'timestamp': datetime.now().isoformat()
            }
            print(f"  Mean: {result['mean_time_sec']:.4f}s ({result['time_per_op_ms']:.3f}ms/op)")
        else:
            result = {
                'operation': 'multiplication',
                'error': 'Multiplication not supported or failed',
                'timestamp': datetime.now().isoformat()
            }
        
        self.results.append(result)
        return result
    
    def measure_ciphertext_size(self) -> Dict:
        """Measure ciphertext size vs plaintext."""
        print(f"\n[CKKS] Ciphertext size measurement...")
        
        plaintext_value = 42.0
        plaintext_size_bytes = sys.getsizeof(plaintext_value)
        
        # Encrypt single value
        encrypted = self.fhe.encrypt_batch_optimized([plaintext_value])
        ciphertext = encrypted[0]
        
        # Serialize to measure size
        serialized = ciphertext.serialize()
        ciphertext_size_bytes = len(serialized)
        
        expansion_ratio = ciphertext_size_bytes / plaintext_size_bytes
        
        result = {
            'metric': 'ciphertext_size',
            'plaintext_size_bytes': plaintext_size_bytes,
            'ciphertext_size_bytes': ciphertext_size_bytes,
            'expansion_ratio': float(expansion_ratio),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"  Plaintext: {plaintext_size_bytes} bytes")
        print(f"  Ciphertext: {ciphertext_size_bytes} bytes")
        print(f"  Expansion: {expansion_ratio:.2f}x")
        return result
    
    def measure_noise_budget(self, depths: List[int] = [1, 2, 3, 4, 5]) -> List[Dict]:
        """
        Simulate noise budget degradation with multiplicative depth.
        
        Note: TenSEAL doesn't expose noise budget directly, so we simulate
        based on theoretical CKKS behavior.
        """
        print(f"\n[CKKS] Noise budget simulation...")
        
        noise_results = []
        initial_budget = 100.0  # Simulated initial budget
        
        for depth in depths:
            # Theoretical noise growth: exponential with depth
            # Each multiplication roughly halves remaining budget
            remaining_budget = initial_budget * (0.5 ** depth)
            
            result = {
                'metric': 'noise_budget',
                'multiplicative_depth': depth,
                'remaining_budget_percent': float(remaining_budget),
                'timestamp': datetime.now().isoformat()
            }
            
            noise_results.append(result)
            self.results.append(result)
            print(f"  Depth {depth}: {remaining_budget:.2f}% budget remaining")
        
        return noise_results
    
    def measure_approximation_error(self, depths: List[int] = [1, 2, 3, 4, 5]) -> List[Dict]:
        """Measure approximation error at different multiplicative depths."""
        print(f"\n[CKKS] Approximation error measurement...")
        
        error_results = []
        test_value = 10.0
        
        for depth in depths:
            try:
                # Encrypt and perform depth multiplications
                encrypted = self.fhe.encrypt_batch_optimized([test_value])
                
                expected_result = test_value
                for _ in range(depth):
                    encrypted = self.fhe.multiply_encrypted_batch(
                        encrypted, 
                        self.fhe.encrypt_batch_optimized([2.0])
                    )
                    expected_result *= 2.0
                
                # Decrypt and measure error
                decrypted = self.fhe.decrypt_batch_optimized(encrypted)[0]
                
                absolute_error = abs(decrypted - expected_result)
                relative_error = absolute_error / expected_result if expected_result != 0 else 0
                
                result = {
                    'metric': 'approximation_error',
                    'multiplicative_depth': depth,
                    'expected_value': float(expected_result),
                    'actual_value': float(decrypted),
                    'absolute_error': float(absolute_error),
                    'relative_error': float(relative_error),
                    'timestamp': datetime.now().isoformat()
                }
                
                error_results.append(result)
                self.results.append(result)
                print(f"  Depth {depth}: abs_error={absolute_error:.6f}, rel_error={relative_error:.6e}")
                
            except Exception as e:
                print(f"  Depth {depth}: Skipped (scale error - {str(e)[:50]})")
                # Record partial result
                result = {
                    'metric': 'approximation_error',
                    'multiplicative_depth': depth,
                    'error': f'Scale error at depth {depth}',
                    'timestamp': datetime.now().isoformat()
                }
                error_results.append(result)
                self.results.append(result)
                # Stop testing deeper levels
                break
        
        return error_results
    
    def run_all_benchmarks(self) -> List[Dict]:
        """Run complete CKKS benchmark suite."""
        print("="*80)
        print("CKKS/FHE PERFORMANCE BENCHMARK")
        print("="*80)
        
        self.benchmark_encryption(n_values=100)
        self.benchmark_decryption(n_values=100)
        self.benchmark_addition(n_operations=100)
        self.benchmark_multiplication(n_operations=50)
        self.measure_ciphertext_size()
        self.measure_noise_budget()
        self.measure_approximation_error()
        
        print("\n" + "="*80)
        print("CKKS Benchmark Complete")
        print("="*80)
        
        return self.results
    
    def save_results(self, output_dir: str = 'evaluation/results/performance') -> str:
        """Save results to CSV."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = output_path / f"performance_ckks_{timestamp}.csv"
        
        if self.results:
            # Get all unique keys
            all_keys = set()
            for result in self.results:
                all_keys.update(result.keys())
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(self.results)
            
            print(f"\n✅ Results saved: {csv_file}")
            return str(csv_file)
        
        return ""


if __name__ == "__main__":
    benchmarker = CKKSBenchmarker(iterations=10)
    benchmarker.run_all_benchmarks()
    benchmarker.save_results()
