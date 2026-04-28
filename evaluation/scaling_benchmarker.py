#!/usr/bin/env python3
"""
Scaling Analysis Benchmarker

Measures how CKKS performance scales with:
- Input vector size
- Multiplicative depth
- Noise growth
- Ciphertext expansion
"""

import time
import sys
import csv
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))
from crypto.fhe_engine import AdvancedFHE, FHEScheme


class ScalingBenchmarker:
    """Scaling analysis for thesis evaluation."""
    
    def __init__(self, iterations: int = 5):
        """
        Initialize scaling benchmarker.
        
        Args:
            iterations: Number of measurement iterations per configuration
        """
        self.iterations = iterations
        self.fhe = AdvancedFHE(scheme=FHEScheme.CKKS, precision_bits=40)
        self.results = []
        
        print(f"Scaling Benchmarker initialized (iterations={iterations})")
    
    def benchmark_vector_size_scaling(self, sizes: List[int] = [10, 50, 100, 500, 1000]) -> List[Dict]:
        """Measure latency vs input vector size."""
        print(f"\n[Scaling] Vector size scaling...")
        print(f"  Sizes: {sizes}")
        
        size_results = []
        
        for n in sizes:
            print(f"\n  Testing n={n}...")
            values = [float(i) for i in range(n)]
            
            latencies = []
            for _ in range(self.iterations):
                start = time.time()
                encrypted = self.fhe.encrypt_batch_optimized(values)
                latency = time.time() - start
                latencies.append(latency)
            
            result = {
                'metric': 'vector_size_scaling',
                'vector_size': n,
                'mean_latency_sec': float(np.mean(latencies)),
                'std_latency_sec': float(np.std(latencies)),
                'latency_per_element_ms': float(np.mean(latencies) / n * 1000),
                'timestamp': datetime.now().isoformat()
            }
            
            size_results.append(result)
            self.results.append(result)
            print(f"    Latency: {result['mean_latency_sec']:.4f}s ({result['latency_per_element_ms']:.3f}ms/element)")
        
        return size_results
    
    def benchmark_depth_scaling(self, depths: List[int] = [1, 2, 3, 4, 5]) -> List[Dict]:
        """Measure latency vs multiplicative depth."""
        print(f"\n[Scaling] Multiplicative depth scaling...")
        print(f"  Depths: {depths}")
        
        depth_results = []
        
        for depth in depths:
            print(f"\n  Testing depth={depth}...")
            
            # Start with encrypted value
            value = 2.0
            encrypted = self.fhe.encrypt_batch_optimized([value])
            
            latencies = []
            for _ in range(self.iterations):
                enc_copy = self.fhe.encrypt_batch_optimized([value])
                
                try:
                    start = time.time()
                    for _ in range(depth):
                        enc_copy = self.fhe.multiply_encrypted_batch(
                            enc_copy,
                            self.fhe.encrypt_batch_optimized([2.0])
                        )
                    latency = time.time() - start
                    latencies.append(latency)
                except Exception as e:
                    print(f"    Iteration failed: {str(e)[:50]}")
                    break
            
            if latencies:
                result = {
                    'metric': 'depth_scaling',
                    'multiplicative_depth': depth,
                    'mean_latency_sec': float(np.mean(latencies)),
                    'std_latency_sec': float(np.std(latencies)),
                    'latency_per_multiplication_ms': float(np.mean(latencies) / depth * 1000),
                    'timestamp': datetime.now().isoformat()
                }
                
                depth_results.append(result)
                self.results.append(result)
                print(f"    Latency: {result['mean_latency_sec']:.4f}s ({result['latency_per_multiplication_ms']:.3f}ms/mult)")
            else:
                print(f"    Skipped: Scale error at depth {depth}")
                result = {
                    'metric': 'depth_scaling',
                    'multiplicative_depth': depth,
                    'error': f'Scale error at depth {depth}',
                    'timestamp': datetime.now().isoformat()
                }
                depth_results.append(result)
                self.results.append(result)
                # Stop testing deeper levels
                break
        
        return depth_results
    
    def measure_noise_growth(self, depths: List[int] = [1, 2, 3, 4, 5]) -> List[Dict]:
        """Measure noise growth vs multiplicative depth."""
        print(f"\n[Scaling] Noise growth measurement...")
        
        noise_results = []
        initial_budget = 100.0
        
        for depth in depths:
            # Theoretical noise growth (exponential)
            remaining_budget = initial_budget * (0.5 ** depth)
            noise_growth_db = 20 * np.log10(initial_budget / max(remaining_budget, 0.01))
            
            result = {
                'metric': 'noise_growth',
                'multiplicative_depth': depth,
                'remaining_budget_percent': float(remaining_budget),
                'noise_growth_db': float(noise_growth_db),
                'timestamp': datetime.now().isoformat()
            }
            
            noise_results.append(result)
            self.results.append(result)
            print(f"  Depth {depth}: {remaining_budget:.2f}% budget, {noise_growth_db:.2f} dB growth")
        
        return noise_results
    
    def measure_ciphertext_expansion(self, scales: List[int] = [20, 30, 40, 50]) -> List[Dict]:
        """Measure ciphertext expansion vs scale parameter."""
        print(f"\n[Scaling] Ciphertext expansion measurement...")
        
        expansion_results = []
        
        for scale_bits in scales:
            # Create FHE with different scale
            fhe = AdvancedFHE(scheme=FHEScheme.CKKS, precision_bits=scale_bits)
            
            # Measure ciphertext size
            plaintext_value = 42.0
            encrypted = fhe.encrypt_batch_optimized([plaintext_value])
            serialized = encrypted[0].serialize()
            
            ciphertext_size = len(serialized)
            plaintext_size = sys.getsizeof(plaintext_value)
            expansion = ciphertext_size / plaintext_size
            
            result = {
                'metric': 'ciphertext_expansion',
                'scale_bits': scale_bits,
                'plaintext_size_bytes': plaintext_size,
                'ciphertext_size_bytes': ciphertext_size,
                'expansion_ratio': float(expansion),
                'timestamp': datetime.now().isoformat()
            }
            
            expansion_results.append(result)
            self.results.append(result)
            print(f"  Scale {scale_bits} bits: {expansion:.2f}x expansion ({ciphertext_size} bytes)")
        
        return expansion_results
    
    def run_all_benchmarks(self) -> List[Dict]:
        """Run complete scaling benchmark suite."""
        print("="*80)
        print("SCALING ANALYSIS BENCHMARK")
        print("="*80)
        
        self.benchmark_vector_size_scaling()
        self.benchmark_depth_scaling()
        self.measure_noise_growth()
        self.measure_ciphertext_expansion()
        
        print("\n" + "="*80)
        print("Scaling Benchmark Complete")
        print("="*80)
        
        return self.results
    
    def save_results(self, output_dir: str = 'evaluation/results/scaling') -> str:
        """Save results to CSV."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = output_path / f"scaling_ckks_{timestamp}.csv"
        
        if self.results:
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
    benchmarker = ScalingBenchmarker(iterations=5)
    benchmarker.run_all_benchmarks()
    benchmarker.save_results()
