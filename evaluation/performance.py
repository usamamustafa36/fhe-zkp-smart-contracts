#!/usr/bin/env python3
"""
Performance Benchmarking for FHE Operations

THESIS REFERENCE: Chapter 5, Section 5.3 - Performance Analysis

This module provides systematic performance evaluation of:
- Encryption latency (single value, batch operations)
- Homomorphic computation latency (addition, multiplication)
- Decryption latency  
- Throughput (operations per second)
- Comparison across FHE schemes (CKKS vs BFV)

Output formats:
- JSON: Machine-readable for processing
- CSV: Spreadsheet-compatible for thesis tables
- Console: Human-readable summary

EVALUATION METHODOLOGY:
======================
1. Fixed parameters across all runs (reproducibility)
2. Warm-up iterations (cache effects)
3. Multiple measurements (statistical validity)
4. Standard deviation reporting (variance)
5. Controlled batch sizes (10, 100, 1000)

METRICS COLLECTED:
=================
- Latency: Time per single operation (ms)
- Throughput: Operations per second
- Batch efficiency: Speedup from batching
- Memory usage: Peak RAM consumption
"""

import time
import json
import csv
import psutil
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Import from new structure
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto.fhe_engine import AdvancedFHE, FHEScheme


class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking for thesis evaluation.
    
    THESIS REFERENCE: Chapter 5, Section 5.3
    """
    
    def __init__(
        self, 
        scheme: FHEScheme = FHEScheme.CKKS,
        precision_bits: int = 40,
        warmup_iterations: int = 5,
        measurement_iterations: int = 10
    ):
        """
        Initialize performance benchmark.
        
        Args:
            scheme: FHE scheme to benchmark
            precision_bits: Precision configuration
            warmup_iterations: Warmup runs (discarded)
            measurement_iterations: Measurement runs (averaged)
        """
        self.scheme = scheme
        self.fhe = AdvancedFHE(scheme=scheme, precision_bits=precision_bits)
        self.warmup_iterations = warmup_iterations
        self.measurement_iterations = measurement_iterations
        self.results = []
        
        print(f"Performance Benchmark Initialized:")
        print(f"  Scheme: {scheme.value}")
        print(f"  Precision: {precision_bits} bits")
        print(f"  Warmup iterations: {warmup_iterations}")
        print(f"  Measurement iterations: {measurement_iterations}")
    
    def benchmark_encryption(self, n_values: int = 100) -> Dict:
        """
        Benchmark encryption latency and throughput.
        
        THESIS REFERENCE: Section 5.3.1 - Encryption Performance
        """
        print(f"\n[Benchmark] Encryption (n={n_values})...")
        
        # Generate test data
        if self.scheme == FHEScheme.CKKS:
            values = [float(i) for i in range(n_values)]
        else:  # BFV
            values = [int(i) for i in range(n_values)]
        
        # Warmup
        for _ in range(self.warmup_iterations):
            _ = self.fhe.encrypt_batch_optimized(values)
        
        # Measure
        latencies = []
        memory_usage = []
        
        for _ in range(self.measurement_iterations):
            # Track memory
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            
            start = time.time()
            encrypted = self.fhe.encrypt_batch_optimized(values)
            duration = time.time() - start
            
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            
            latencies.append(duration)
            memory_usage.append(mem_after - mem_before)
        
        # Calculate statistics
        latencies = np.array(latencies)
        
        result = {
            'operation': 'encryption',
            'scheme': self.scheme.value,
            'n_values': n_values,
            'total_time_mean': float(np.mean(latencies)),
            'total_time_std': float(np.std(latencies)),
            'avg_latency_ms': float(np.mean(latencies) / n_values * 1000),
            'throughput_ops_sec': float(n_values / np.mean(latencies)),
            'memory_delta_mb_mean': float(np.mean(memory_usage)),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        self._print_result(result)
        return result
    
    def benchmark_addition(self, n_operations: int = 100) -> Dict:
        """
        Benchmark homomorphic addition.
        
        THESIS REFERENCE: Section 5.3.2 - Computation Performance
        """
        print(f"\n[Benchmark] Addition (n={n_operations})...")
        
        # Prepare encrypted data
        if self.scheme == FHEScheme.CKKS:
            values_a = [float(i) for i in range(n_operations)]
            values_b = [float(i+1) for i in range(n_operations)]
        else:
            values_a = [int(i) for i in range(n_operations)]
            values_b = [int(i+1) for i in range(n_operations)]
        
        enc_a = self.fhe.encrypt_batch_optimized(values_a)
        enc_b = self.fhe.encrypt_batch_optimized(values_b)
        
        # Warmup
        for _ in range(self.warmup_iterations):
            _ = self.fhe.add_encrypted_batch_optimized(enc_a, enc_b)
        
        # Measure
        latencies = []
        for _ in range(self.measurement_iterations):
            start = time.time()
            _ = self.fhe.add_encrypted_batch_optimized(enc_a, enc_b)
            duration = time.time() - start
            latencies.append(duration)
        
        latencies = np.array(latencies)
        
        result = {
            'operation': 'addition',
            'scheme': self.scheme.value,
            'n_operations': n_operations,
            'total_time_mean': float(np.mean(latencies)),
            'total_time_std': float(np.std(latencies)),
            'avg_latency_ms': float(np.mean(latencies) / n_operations * 1000),
            'throughput_ops_sec': float(n_operations / np.mean(latencies)),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        self._print_result(result)
        return result
    
    def benchmark_multiplication(self, n_operations: int = 50) -> Dict:
        """
        Benchmark homomorphic multiplication.
        
        Note: Multiplication is more expensive than addition.
        
        THESIS REFERENCE: Section 5.3.2 - Computation Performance
        """
        print(f"\n[Benchmark] Multiplication (n={n_operations})...")
        
        # Prepare encrypted data (smaller n due to cost)
        if self.scheme == FHEScheme.CKKS:
            values_a = [float(i+1) for i in range(n_operations)]
            values_b = [float(2.0) for _ in range(n_operations)]
        else:
            values_a = [int(i+1) for i in range(n_operations)]
            values_b = [int(2) for _ in range(n_operations)]
        
        enc_a = self.fhe.encrypt_batch_optimized(values_a)
        enc_b = self.fhe.encrypt_batch_optimized(values_b)
        
        # Warmup
        for _ in range(self.warmup_iterations):
            try:
                _ = self.fhe.multiply_encrypted_batch(enc_a, enc_b)
            except:
                pass  # Some schemes may not support multiplication
        
        # Measure
        latencies = []
        for _ in range(self.measurement_iterations):
            start = time.time()
            try:
                _ = self.fhe.multiply_encrypted_batch(enc_a, enc_b)
                duration = time.time() - start
                latencies.append(duration)
            except Exception as e:
                print(f"  Warning: Multiplication failed - {e}")
                break
        
        if latencies:
            latencies = np.array(latencies)
            result = {
                'operation': 'multiplication',
                'scheme': self.scheme.value,
                'n_operations': n_operations,
                'total_time_mean': float(np.mean(latencies)),
                'total_time_std': float(np.std(latencies)),
                'avg_latency_ms': float(np.mean(latencies) / n_operations * 1000),
                'throughput_ops_sec': float(n_operations / np.mean(latencies)),
                'timestamp': datetime.now().isoformat()
            }
        else:
            result = {
                'operation': 'multiplication',
                'scheme': self.scheme.value,
                'error': 'Multiplication not supported or failed',
                'timestamp': datetime.now().isoformat()
            }
        
        self.results.append(result)
        self._print_result(result)
        return result
    
    def benchmark_decryption(self, n_values: int = 100) -> Dict:
        """
        Benchmark decryption latency and throughput.
        
        THESIS REFERENCE: Section 5.3.3 - Decryption Performance
        """
        print(f"\n[Benchmark] Decryption (n={n_values})...")
        
        # Prepare encrypted data
        if self.scheme == FHEScheme.CKKS:
            values = [float(i) for i in range(n_values)]
        else:
            values = [int(i) for i in range(n_values)]
        
        encrypted = self.fhe.encrypt_batch_optimized(values)
        
        # Warmup
        for _ in range(self.warmup_iterations):
            _ = self.fhe.decrypt_batch_optimized(encrypted)
        
        # Measure
        latencies = []
        for _ in range(self.measurement_iterations):
            start = time.time()
            _ = self.fhe.decrypt_batch_optimized(encrypted)
            duration = time.time() - start
            latencies.append(duration)
        
        latencies = np.array(latencies)
        
        result = {
            'operation': 'decryption',
            'scheme': self.scheme.value,
            'n_values': n_values,
            'total_time_mean': float(np.mean(latencies)),
            'total_time_std': float(np.std(latencies)),
            'avg_latency_ms': float(np.mean(latencies) / n_values * 1000),
            'throughput_ops_sec': float(n_values / np.mean(latencies)),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        self._print_result(result)
        return result
    
    def run_all_benchmarks(self, sizes: List[int] = [10, 100]) -> List[Dict]:
        """
        Run complete benchmark suite.
        
        Args:
            sizes: Batch sizes to test
            
        Returns:
            List of all benchmark results
        """
        print("="*80)
        print("COMPREHENSIVE PERFORMANCE BENCHMARK")
        print("="*80)
        
        for size in sizes:
            self.benchmark_encryption(n_values=size)
            self.benchmark_addition(n_operations=size)
            self.benchmark_multiplication(n_operations=min(size, 50))
            self.benchmark_decryption(n_values=size)
        
        return self.results
    
    def save_results(self, output_dir: str = 'evaluation/results/performance/'):
        """
        Save results to JSON and CSV for thesis.
        
        THESIS REFERENCE: Table 5.2 - Performance Results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scheme_name = self.scheme.value.lower()
        
        # Save JSON
        json_file = output_path / f"performance_{scheme_name}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved to: {json_file}")
        
        # Save CSV
        if self.results:
            csv_file = output_path / f"performance_{scheme_name}_{timestamp}.csv"
            keys = self.results[0].keys()
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.results)
            print(f"✅ Results saved to: {csv_file}")
    
    def _print_result(self, result: Dict):
        """Print formatted result."""
        print(f"  Operation: {result.get('operation', 'unknown')}")
        if 'avg_latency_ms' in result:
            print(f"  Avg Latency: {result['avg_latency_ms']:.3f} ms")
        if 'throughput_ops_sec' in result:
            print(f"  Throughput: {result['throughput_ops_sec']:.0f} ops/sec")
        if 'error' in result:
            print(f"  Error: {result['error']}")


# Example usage
if __name__ == "__main__":
    print("Performance Benchmarking - Thesis Evaluation\n")
    
    # Benchmark CKKS
    benchmark = PerformanceBenchmark(scheme=FHEScheme.CKKS, precision_bits=40)
    benchmark.run_all_benchmarks(sizes=[10, 100])
    benchmark.save_results()
    
    print("\n" + "="*80)
    print("Benchmark Complete - Results saved to evaluation/results/performance/")
    print("="*80)
