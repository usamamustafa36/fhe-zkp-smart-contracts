#!/usr/bin/env python3
"""
End-to-End Pipeline Latency Benchmarker

Measures full workflow latency:
1. ZKP proof generation
2. FHE encryption
3. On-chain verification (estimated)
4. Homomorphic computation
5. Decryption
"""

import time
import sys
import csv
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))
from crypto.fhe_engine import AdvancedFHE, FHEScheme


class EndToEndBenchmarker:
    """End-to-end pipeline latency measurement."""
    
    def __init__(self, iterations: int = 5):
        """
        Initialize end-to-end benchmarker.
        
        Args:
            iterations: Number of full pipeline runs
        """
        self.iterations = iterations
        self.fhe = AdvancedFHE(scheme=FHEScheme.CKKS, precision_bits=40)
        self.zkp_dir = Path("zkp_prod")
        self.artifacts_dir = self.zkp_dir / "artifacts"
        self.results = []
        
        print(f"End-to-End Benchmarker initialized (iterations={iterations})")
    
    def run_full_pipeline(self) -> Dict:
        """Run complete pipeline and measure each stage."""
        print(f"\n[E2E] Running full pipeline...")
        
        stage_times = {
            'zkp_proof_generation': 0,
            'fhe_encryption': 0,
            'verification_estimated': 0.003,  # Estimated 3ms on-chain
            'homomorphic_computation': 0,
            'fhe_decryption': 0
        }
        
        # Stage 1: ZKP Proof Generation
        print("  Stage 1: ZKP proof generation...")
        zkp_start = time.time()
        
        try:
            # Create sample input
            sample_input = {
                "value": 50,
                "salt": 12345,
                "min_value": 0,
                "max_value": 100
            }
            
            input_file = self.artifacts_dir / "e2e_input.json"
            with open(input_file, 'w') as f:
                json.dump(sample_input, f)
            
            # Generate witness
            witness_gen_script = self.zkp_dir / "python" / "witness_sanitizer.py"
            subprocess.run(
                [sys.executable, str(witness_gen_script), str(input_file)],
                capture_output=True,
                timeout=60,
                check=False
            )
            
            # Generate proof
            zkey_file = self.artifacts_dir / "range_commit_0001.zkey"
            witness_file = self.artifacts_dir / "witness.wtns"
            proof_file = self.artifacts_dir / "e2e_proof.json"
            public_file = self.artifacts_dir / "e2e_public.json"
            
            if zkey_file.exists() and witness_file.exists():
                subprocess.run(
                    [
                        "snarkjs", "groth16", "prove",
                        str(zkey_file),
                        str(witness_file),
                        str(proof_file),
                        str(public_file)
                    ],
                    capture_output=True,
                    timeout=60,
                    check=False
                )
            
            stage_times['zkp_proof_generation'] = time.time() - zkp_start
            print(f"    ZKP: {stage_times['zkp_proof_generation']:.4f}s")
        except Exception as e:
            print(f"    ZKP: Failed - {e}")
        
        # Stage 2: FHE Encryption
        print("  Stage 2: FHE encryption...")
        enc_start = time.time()
        
        values = [float(sample_input['value'])]
        encrypted = self.fhe.encrypt_batch_optimized(values)
        
        stage_times['fhe_encryption'] = time.time() - enc_start
        print(f"    Encryption: {stage_times['fhe_encryption']:.4f}s")
        
        # Stage 3: On-chain verification (estimated)
        print(f"  Stage 3: On-chain verification (estimated)...")
        print(f"    Verification: {stage_times['verification_estimated']:.4f}s (estimated)")
        
        # Stage 4: Homomorphic Computation
        print("  Stage 4: Homomorphic computation...")
        comp_start = time.time()
        
        # Perform homomorphic operation (add 100)
        encrypted_hundred = self.fhe.encrypt_batch_optimized([100.0])
        result_encrypted = self.fhe.add_encrypted_batch_optimized(encrypted, encrypted_hundred)
        
        stage_times['homomorphic_computation'] = time.time() - comp_start
        print(f"    Computation: {stage_times['homomorphic_computation']:.4f}s")
        
        # Stage 5: FHE Decryption
        print("  Stage 5: FHE decryption...")
        dec_start = time.time()
        
        result_decrypted = self.fhe.decrypt_batch_optimized(result_encrypted)
        
        stage_times['fhe_decryption'] = time.time() - dec_start
        print(f"    Decryption: {stage_times['fhe_decryption']:.4f}s")
        
        # Calculate total
        total_time = sum(stage_times.values())
        
        result = {
            'metric': 'end_to_end_pipeline',
            'total_time_sec': float(total_time),
            **{f'{k}_sec': float(v) for k, v in stage_times.items()},
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n  Total pipeline: {total_time:.4f}s")
        
        return result
    
    def run_all_benchmarks(self) -> List[Dict]:
        """Run complete end-to-end benchmark suite."""
        print("="*80)
        print("END-TO-END PIPELINE LATENCY BENCHMARK")
        print("="*80)
        
        for i in range(self.iterations):
            print(f"\n=== Iteration {i+1}/{self.iterations} ===")
            result = self.run_full_pipeline()
            self.results.append(result)
        
        # Calculate averages
        if self.results:
            import numpy as np
            
            # Get all numeric fields
            numeric_fields = [k for k in self.results[0].keys() 
                            if k.endswith('_sec') and k != 'timestamp']
            
            avg_result = {'metric': 'end_to_end_average'}
            for field in numeric_fields:
                values = [r[field] for r in self.results if field in r]
                avg_result[f'{field}_mean'] = float(np.mean(values))
                avg_result[f'{field}_std'] = float(np.std(values))
            
            avg_result['timestamp'] = datetime.now().isoformat()
            self.results.append(avg_result)
            
            print("\n" + "="*80)
            print("AVERAGE LATENCIES:")
            for field in numeric_fields:
                print(f"  {field}: {avg_result[f'{field}_mean']:.4f}s ± {avg_result[f'{field}_std']:.4f}s")
        
        print("\n" + "="*80)
        print("End-to-End Benchmark Complete")
        print("="*80)
        
        return self.results
    
    def save_results(self, output_dir: str = 'evaluation/results/end_to_end') -> str:
        """Save results to CSV."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = output_path / f"end_to_end_latency_{timestamp}.csv"
        
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
    benchmarker = EndToEndBenchmarker(iterations=5)
    benchmarker.run_all_benchmarks()
    benchmarker.save_results()
