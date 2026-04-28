#!/usr/bin/env python3
"""
Scaling Experiments for Thesis Analysis

THESIS REFERENCE: Chapter 5, Section 5.4 - Scalability Analysis

Conducts controlled scaling experiments to evaluate how performance changes
with input size. This is critical for understanding:
- Asymptotic complexity (O(n), O(n²), etc.)
- Practical scaling limits
- Resource requirements at different scales

EXPERIMENTAL DESIGN:
===================
- Fixed parameters across all runs (reproducibility)
- Range: n = 10, 100, 1000  (orders of magnitude)
- Multiple iterations per size (statistical validity)
- Consistent test data generation
- CSV/JSON output for thesis plots

METRICS ANALYZED:
================
- Time complexity: How latency scales with n
- Space complexity: How memory scales with n
- Throughput degradation: ops/sec vs n
- Efficiency metrics: Batch speedup factor

THESIS PLOTS:
============
- Figure 5.1: Latency vs Input Size
- Figure 5.2: Throughput vs Input Size
- Figure 5.3: Memory Usage vs Input Size
- Table 5.3: Scaling Factors
"""

import time
import json
import csv
import numpy as np
import psutil
from pathlib import Path
from typing import Dict, List
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto.fhe_engine import AdvancedFHE, FHEScheme


class ScalingExperiment:
    """
    Controlled scaling experiments for thesis evaluation.
    
    THESIS REFERENCE: Chapter 5, Section 5.4
    """
    
    def __init__(
        self,
        scheme: FHEScheme = FHEScheme.CKKS,
        sizes: List[int] = [10, 100, 1000],
        iterations_per_size: int = 5
    ):
        """
        Initialize scaling experiment.
        
        Args:
            scheme: FHE scheme to test
            sizes: Input sizes to test (orders of magnitude)
            iterations_per_size: Measurements per size (for averaging)
        """
        self.scheme = scheme
        self.sizes = sizes
        self.iterations = iterations_per_size
        self.fhe = AdvancedFHE(scheme=scheme, precision_bits=40)
        self.results = []
        
        print(f"Scaling Experiment Configuration:")
        print(f"  Scheme: {scheme.value}")
        print(f"  Sizes: {sizes}")
        print(f"  Iterations per size: {iterations_per_size}")
    
    def run_encryption_scaling(self) -> List[Dict]:
        """
        Measure encryption scaling with input size.
        
        Tests hypothesis: Encryption time = O(n)
        
        THESIS REFERENCE: Section 5.4.1 - Encryption Scaling
        """
        print("\n" + "="*80)
        print("ENCRYPTION SCALING EXPERIMENT")
        print("="*80)
        
        results = []
        
        for n in self.sizes:
            print(f"\n[n={n}] Encryption scaling...")
            
            # Generate test data
            if self.scheme == FHEScheme.CKKS:
                values = [float(i) for i in range(n)]
            else:
                values = [int(i) for i in range(n)]
            
            latencies = []
            memory_deltas = []
            
            for iteration in range(self.iterations):
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                
                start = time.time()
                encrypted = self.fhe.encrypt_batch_optimized(values)
                latency = time.time() - start
                
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                
                latencies.append(latency)
                memory_deltas.append(mem_after - mem_before)
                
                print(f"  Iteration {iteration+1}/{self.iterations}: "
                      f"{latency:.3f}s, {latencies[-1]/n*1000:.3f}ms/op")
            
            # Calculate statistics
            result = {
                'operation': 'encryption',
                'scheme': self.scheme.value,
                'n': n,
                'latency_mean_sec': float(np.mean(latencies)),
                'latency_std_sec': float(np.std(latencies)),
                'latency_per_op_ms': float(np.mean(latencies) / n * 1000),
                'throughput_ops_sec': float(n / np.mean(latencies)),
                'memory_delta_mb': float(np.mean(memory_deltas)),
                'timestamp': datetime.now().isoformat()
            }
            
            results.append(result)
            self.results.append(result)
            
            print(f"  Mean: {result['latency_mean_sec']:.3f}s "
                  f"({result['latency_per_op_ms']:.3f}ms/op)")
            print(f"  Throughput: {result['throughput_ops_sec']:.0f} ops/sec")
        
        # Analyze scaling factor
        self._analyze_scaling_factor(results, 'encryption')
        
        return results
    
    def run_computation_scaling(self) -> List[Dict]:
        """
        Measure homomorphic addition scaling with input size.
        
        Tests hypothesis: Addition time = O(n)
        
        THESIS REFERENCE: Section 5.4.2 - Computation Scaling
        """
        print("\n" + "="*80)
        print("HOMOMORPHIC ADDITION SCALING EXPERIMENT")
        print("="*80)
        
        results = []
        
        for n in self.sizes:
            print(f"\n[n={n}] Addition scaling...")
            
            # Prepare encrypted data
            if self.scheme == FHEScheme.CKKS:
                values_a = [float(i) for i in range(n)]
                values_b = [float(i+1) for i in range(n)]
            else:
                values_a = [int(i) for i in range(n)]
                values_b = [int(i+1) for i in range(n)]
            
            # Pre-encrypt (not counted in timing)
            enc_a = self.fhe.encrypt_batch_optimized(values_a)
            enc_b = self.fhe.encrypt_batch_optimized(values_b)
            
            latencies = []
            
            for iteration in range(self.iterations):
                start = time.time()
                _ = self.fhe.add_encrypted_batch_optimized(enc_a, enc_b)
                latency = time.time() - start
                latencies.append(latency)
                
                print(f"  Iteration {iteration+1}/{self.iterations}: "
                      f"{latency:.3f}s, {latency/n*1000:.3f}ms/op")
            
            result = {
                'operation': 'addition',
                'scheme': self.scheme.value,
                'n': n,
                'latency_mean_sec': float(np.mean(latencies)),
                'latency_std_sec': float(np.std(latencies)),
                'latency_per_op_ms': float(np.mean(latencies) / n * 1000),
                'throughput_ops_sec': float(n / np.mean(latencies)),
                'timestamp': datetime.now().isoformat()
            }
            
            results.append(result)
            self.results.append(result)
            
            print(f"  Mean: {result['latency_mean_sec']:.3f}s "
                  f"({result['latency_per_op_ms']:.3f}ms/op)")
        
        self._analyze_scaling_factor(results, 'addition')
        
        return results
    
    def run_all_experiments(self) -> List[Dict]:
        """
        Run complete scaling experiment suite.
        
        Returns:
            All experimental results
        """
        print("\n" + "="*80)
        print(f"COMPREHENSIVE SCALING ANALYSIS - {self.scheme.value}")
        print("="*80)
        
        self.run_encryption_scaling()
        self.run_computation_scaling()
        
        print("\n" + "="*80)
        print("SCALING EXPERIMENTS COMPLETE")
        print("="*80)
        
        return self.results
    
    def _analyze_scaling_factor(self, results: List[Dict], operation: str):
        """
        Analyze scaling factor between consecutive sizes.
        
        If time doubles when n increases 10x → O(n/5) sublinear
        If time increases 10x when n increases 10x → O(n) linear
        If time increases 100x when n increases 10x → O(n²) quadratic
        """
        print(f"\n  Scaling Analysis for {operation}:")
        
        for i in range(1, len(results)):
            n1, t1 = results[i-1]['n'], results[i-1]['latency_mean_sec']
            n2, t2 = results[i]['n'], results[i]['latency_mean_sec']
            
            n_factor = n2 / n1
            time_factor = t2 / t1
            
            # Estimate complexity exponent: t2/t1 ≈ (n2/n1)^k → k = log(t2/t1) / log(n2/n1)
            if t1 > 0 and n_factor > 1:
                complexity_exponent = np.log(time_factor) / np.log(n_factor)
                
                print(f"  n: {n1} → {n2} (×{n_factor:.1f})")
                print(f"  time: {t1:.3f}s → {t2:.3f}s (×{time_factor:.2f})")
                print(f"  Estimated complexity: O(n^{complexity_exponent:.2f})")
    
    def save_results(self, output_dir: str = 'evaluation/results/scaling/'):
        """
        Save scaling results for thesis plots.
        
        Output formats:
        - CSV: For creating plots in Excel/Python
        - JSON: Complete data with metadata
        
        THESIS REFERENCE: Figure 5.1, Figure 5.2, Table 5.3
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scheme_name = self.scheme.value.lower()
        
        # Save JSON
        json_file = output_path / f"scaling_{scheme_name}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'experiment': 'scaling_analysis',
                'scheme': self.scheme.value,
                'sizes_tested': self.sizes,
                'iterations_per_size': self.iterations,
                'results': self.results,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print(f"\n✅ Results saved to: {json_file}")
        
        # Save CSV
        if self.results:
            csv_file = output_path / f"scaling_{scheme_name}_{timestamp}.csv"
            keys = self.results[0].keys()
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.results)
            print(f"✅ Results saved to: {csv_file}")


def generate_scaling_plots_data():
    """
    Generate data formatted for thesis plots.
    
    Creates plot-ready data structure for:
    - Matplotlib/Seaborn plotting scripts
    - Excel charts
    - LaTeX/TikZ figures
    """
    # This would be called by figures/performance_plots.py
    pass


# Example usage
if __name__ == "__main__":
    print("Scaling Experiments - Thesis Evaluation\n")
    
    # Run scaling experiment
    experiment = ScalingExperiment(
        scheme=FHEScheme.CKKS,
        sizes=[10, 100, 1000],
        iterations_per_size=3
    )
    
    experiment.run_all_experiments()
    experiment.save_results()
    
    print("\n" + "="*80)
    print("For thesis: Use results to generate Figure 5.1 and Figure 5.2")
    print("Command: python figures/performance_plots.py")
    print("="*80)
