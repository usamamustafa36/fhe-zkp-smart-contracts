#!/usr/bin/env python3
"""
ZKP (Groth16) Performance Benchmarker

Measures Zero-Knowledge Proof metrics:
- Circuit constraint count
- Proof generation time
- Proof size
- Verification time
- Gas estimation
"""

import time
import sys
import json
import csv
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))


class ZKPBenchmarker:
    """ZKP performance benchmarking using existing Circom/SnarkJS pipeline."""
    
    def __init__(self):
        """Initialize ZKP benchmarker."""
        self.zkp_dir = Path("zkp_prod")
        self.artifacts_dir = self.zkp_dir / "artifacts"
        self.circuit_name = "range_commit"
        self.results = []
        
        print("ZKP Benchmarker initialized")
    
    def verify_artifacts_exist(self) -> bool:
        """Verify required ZKP artifacts exist."""
        required_files = [
            self.artifacts_dir / f"{self.circuit_name}.r1cs",
            self.artifacts_dir / f"{self.circuit_name}_0001.zkey",
            self.artifacts_dir / f"{self.circuit_name}_js" / f"{self.circuit_name}.wasm",
            self.artifacts_dir / "verification_key.json"
        ]
        
        missing = []
        for file in required_files:
            if not file.exists():
                missing.append(str(file))
        
        if missing:
            print("\n❌ Missing ZKP artifacts:")
            for f in missing:
                print(f"  - {f}")
            print("\nPlease run: ./zkp_prod/scripts/build.sh")
            return False
        
        print("✅ All ZKP artifacts found")
        return True
    
    def measure_circuit_constraints(self) -> Dict:
        """Measure circuit constraint count."""
        print(f"\n[ZKP] Measuring circuit constraints...")
        
        r1cs_file = self.artifacts_dir / f"{self.circuit_name}.r1cs"
        
        try:
            result = subprocess.run(
                ["snarkjs", "r1cs", "info", str(r1cs_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            
            # Parse output for constraint count
            constraints = 0
            for line in output.split('\n'):
                if 'Constraints:' in line or 'constraints:' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        constraints = int(parts[1].strip())
                        break
            
            metric = {
                'metric': 'circuit_constraints',
                'constraint_count': constraints,
                'circuit_name': self.circuit_name,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(metric)
            print(f"  Constraints: {constraints}")
            return metric
            
        except Exception as e:
            print(f"  Warning: Could not measure constraints - {e}")
            return {'metric': 'circuit_constraints', 'error': str(e)}
    
    def measure_proof_generation(self, iterations: int = 5) -> Dict:
        """Measure proof generation time."""
        print(f"\n[ZKP] Measuring proof generation time (iterations={iterations})...")
        
        # Use Python witness generator
        witness_gen_script = self.zkp_dir / "python" / "witness_sanitizer.py"
        zkey_file = self.artifacts_dir / f"{self.circuit_name}_0001.zkey"
        
        # Create sample input
        sample_input = {
            "value": 50,
            "salt": 12345,
            "min_value": 0,
            "max_value": 100
        }
        
        input_file = self.artifacts_dir / "test_input.json"
        with open(input_file, 'w') as f:
            json.dump(sample_input, f)
        
        latencies = []
        proof_sizes = []
        
        for i in range(iterations):
            try:
                # Generate witness (Python)
                witness_start = time.time()
                witness_result = subprocess.run(
                    [sys.executable, str(witness_gen_script), str(input_file)],
                    capture_output=True,
                    timeout=60
                )
                witness_time = time.time() - witness_start
                
                # Generate proof (SnarkJS)
                witness_file = self.artifacts_dir / "witness.wtns"
                proof_file = self.artifacts_dir / "proof.json"
                public_file = self.artifacts_dir / "public.json"
                
                proof_start = time.time()
                proof_result = subprocess.run(
                    [
                        "snarkjs", "groth16", "prove",
                        str(zkey_file),
                        str(witness_file),
                        str(proof_file),
                        str(public_file)
                    ],
                    capture_output=True,
                    timeout=60
                )
                proof_time = time.time() - proof_start
                
                total_time = witness_time + proof_time
                latencies.append(total_time)
                
                # Measure proof size
                if proof_file.exists():
                    proof_size = proof_file.stat().st_size
                    proof_sizes.append(proof_size)
                
                print(f"  Iteration {i+1}/{iterations}: {total_time:.4f}s")
                
            except subprocess.TimeoutExpired:
                print(f"  Iteration {i+1}/{iterations}: Timeout")
            except Exception as e:
                print(f"  Iteration {i+1}/{iterations}: Error - {e}")
        
        if latencies:
            import numpy as np
            result = {
                'metric': 'proof_generation',
                'mean_time_sec': float(np.mean(latencies)),
                'std_time_sec': float(np.std(latencies)),
                'min_time_sec': float(np.min(latencies)),
                'max_time_sec': float(np.max(latencies)),
                'mean_proof_size_bytes': float(np.mean(proof_sizes)) if proof_sizes else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"  Mean: {result['mean_time_sec']:.4f}s")
            return result
        else:
            return {'metric': 'proof_generation', 'error': 'No successful iterations'}
    
    def measure_proof_size(self) -> Dict:
        """Measure proof size."""
        print(f"\n[ZKP] Measuring proof size...")
        
        proof_file = self.artifacts_dir / "proof.json"
        
        if proof_file.exists():
            proof_size = proof_file.stat().st_size
            
            # Parse proof to get component sizes
            with open(proof_file, 'r') as f:
                proof_data = json.load(f)
            
            result = {
                'metric': 'proof_size',
                'total_size_bytes': proof_size,
                'proof_file': str(proof_file),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"  Proof size: {proof_size} bytes ({proof_size/1024:.2f} KB)")
            return result
        else:
            print("  Warning: No proof file found")
            return {'metric': 'proof_size', 'error': 'Proof file not found'}
    
    def measure_verification_time(self, iterations: int = 10) -> Dict:
        """Measure verification time."""
        print(f"\n[ZKP] Measuring verification time (iterations={iterations})...")
        
        proof_file = self.artifacts_dir / "proof.json"
        public_file = self.artifacts_dir / "public.json"
        vkey_file = self.artifacts_dir / "verification_key.json"
        
        if not all([proof_file.exists(), public_file.exists(), vkey_file.exists()]):
            print("  Warning: Missing verification files")
            return {'metric': 'verification', 'error': 'Missing files'}
        
        latencies = []
        
        for i in range(iterations):
            try:
                start = time.time()
                result = subprocess.run(
                    [
                        "snarkjs", "groth16", "verify",
                        str(vkey_file),
                        str(public_file),
                        str(proof_file)
                    ],
                    capture_output=True,
                    timeout=30
                )
                latency = time.time() - start
                latencies.append(latency)
                
            except Exception as e:
                print(f"  Iteration {i+1}/{iterations}: Error - {e}")
        
        if latencies:
            import numpy as np
            result = {
                'metric': 'verification',
                'mean_time_sec': float(np.mean(latencies)),
                'std_time_sec': float(np.std(latencies)),
                'mean_time_ms': float(np.mean(latencies) * 1000),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"  Mean: {result['mean_time_ms']:.2f}ms")
            return result
        else:
            return {'metric': 'verification', 'error': 'No successful iterations'}
    
    def estimate_gas_cost(self) -> Dict:
        """Estimate on-chain verification gas cost."""
        print(f"\n[ZKP] Estimating on-chain gas cost...")
        
        # Typical Groth16 verification gas cost
        # Based on standard Groth16 verifier contracts
        estimated_gas = 250000  # Approximate
        
        result = {
            'metric': 'gas_estimation',
            'estimated_gas': estimated_gas,
            'note': 'Estimated for Groth16 on-chain verification',
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"  Estimated gas: ~{estimated_gas:,}")
        return result
    
    def run_all_benchmarks(self) -> List[Dict]:
        """Run complete ZKP benchmark suite."""
        print("="*80)
        print("ZKP (GROTH16) PERFORMANCE BENCHMARK")
        print("="*80)
        
        if not self.verify_artifacts_exist():
            print("\n❌ Cannot run ZKP benchmarks without artifacts")
            return []
        
        self.measure_circuit_constraints()
        self.measure_proof_generation(iterations=5)
        self.measure_proof_size()
        self.measure_verification_time(iterations=10)
        self.estimate_gas_cost()
        
        print("\n" + "="*80)
        print("ZKP Benchmark Complete")
        print("="*80)
        
        return self.results
    
    def save_results(self, output_dir: str = 'evaluation/results/zkp') -> str:
        """Save results to CSV."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = output_path / f"zkp_metrics_{timestamp}.csv"
        
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
    benchmarker = ZKPBenchmarker()
    benchmarker.run_all_benchmarks()
    benchmarker.save_results()
