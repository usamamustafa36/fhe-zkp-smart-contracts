import tenseal as ts
import numpy as np
from typing import List, Union, Tuple, Optional, Dict
import time
from joblib import Parallel, delayed
from tqdm import tqdm
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

class FHEScheme(Enum):
    """Supported FHE schemes."""
    CKKS = "CKKS"  # For floating-point arithmetic
    BFV = "BFV"    # For integer arithmetic

class AdvancedFHE:
    """
    Advanced Fully Homomorphic Encryption engine with multiple schemes
    and optimized precision handling.
    """
    
    # ------------------------------------------------------------------
    # Recommended parameter sets (see security_model.md Section 1.3).
    #
    # SECURE (default) — N = 8192, log q ≈ 200 → λ ≈ 128-bit security.
    #   Suitable for thesis evaluation and production-style experiments.
    #
    # BENCHMARK — N = 4096, log q ≈ 100 → λ ≈ 80-bit security.
    #   Smaller parameters used only for fast micro-benchmarks where
    #   timing, not security level, is the measurement target.
    #   Explicitly NOT intended for deployment.
    # ------------------------------------------------------------------
    SECURE_PARAMS = {
        "poly_modulus_degree": 8192,
        "coeff_mod_bit_sizes": [60, 40, 40, 60],  # log q ≈ 200, λ ≈ 128
        "global_scale": 2 ** 40,
    }
    BENCHMARK_PARAMS = {
        "poly_modulus_degree": 4096,
        "coeff_mod_bit_sizes": [40, 20, 40],       # log q ≈ 100, λ ≈ 80
        "global_scale": 2 ** 20,
    }

    def __init__(self,
                 scheme: FHEScheme = FHEScheme.CKKS,
                 poly_modulus_degree: int = 8192,
                 coeff_mod_bit_sizes: List[int] = None,
                 plain_modulus: int = None,
                 global_scale: int = None,
                 max_workers: int = 4,
                 precision_bits: int = 40):
        """
        Initialize advanced FHE engine.
        
        Args:
            scheme: FHE scheme to use
            poly_modulus_degree: Polynomial modulus degree
            coeff_mod_bit_sizes: Coefficient modulus bit sizes (for CKKS)
            plain_modulus: Plain modulus (for BFV/BGV)
            global_scale: Global scale for CKKS
            max_workers: Maximum number of parallel workers
            precision_bits: Precision bits for CKKS (higher = more precision)
        """
        self.scheme = scheme
        self.max_workers = max_workers
        self.precision_bits = precision_bits
        
        # Set default parameters based on scheme.
        # Default CKKS parameters → N=8192, [60,40,40,60] → ≥128-bit security.
        if scheme == FHEScheme.CKKS:
            if coeff_mod_bit_sizes is None:
                coeff_mod_bit_sizes = [60, 40, 40, 60]
            if global_scale is None:
                global_scale = 2 ** 40
        elif scheme == FHEScheme.BFV:
            if plain_modulus is None:
                plain_modulus = 786433  # 2^18 + 1
        
        self.context = self._create_context(
            scheme, poly_modulus_degree, coeff_mod_bit_sizes, 
            plain_modulus, global_scale
        )
        
        print(f"Advanced FHE with {scheme.value} scheme enabled")
        print(f"Precision: {precision_bits} bits")
    
    def _create_context(self, scheme: FHEScheme, poly_modulus_degree: int, 
                       coeff_mod_bit_sizes: List[int], plain_modulus: int, 
                       global_scale: int) -> ts.Context:
        """Create optimized FHE context based on scheme."""
        if scheme == FHEScheme.CKKS:
            context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=poly_modulus_degree,
                coeff_mod_bit_sizes=coeff_mod_bit_sizes
            )
            context.global_scale = global_scale
            context.generate_galois_keys()
            context.generate_relin_keys()  # Required for ciphertext-ciphertext multiplication
        elif scheme == FHEScheme.BFV:
            context = ts.context(
                ts.SCHEME_TYPE.BFV,
                poly_modulus_degree=poly_modulus_degree,
                plain_modulus=plain_modulus
            )
        else:
            raise ValueError(f"Unsupported scheme: {scheme}")
        
        return context
    
    def encrypt_batch_optimized(self, values: List[Union[float, int]], 
                               batch_size: int = 100) -> List[Union[ts.CKKSTensor, ts.BFVTensor]]:
        """
        Optimized batch encryption with scheme-specific handling.
        
        Args:
            values: List of values to encrypt
            batch_size: Size of each batch for processing
            
        Returns:
            List of encrypted tensors
        """
        if not values:
            return []
        
        # Validate input types based on scheme
        if self.scheme == FHEScheme.CKKS:
            if not all(isinstance(v, (int, float)) for v in values):
                raise ValueError("CKKS scheme requires numeric values")
        else:  # BFV/BGV
            if not all(isinstance(v, int) for v in values):
                raise ValueError(f"{self.scheme.value} scheme requires integer values")
        
        encrypted_batch = []

        print(f"Encrypting {len(values)} values using {self.scheme.value} scheme...")

        for i in tqdm(range(0, len(values), batch_size), desc=f"{self.scheme.value} Encryption"):
            batch_values = values[i:i + batch_size]

            # Submit futures in order and collect results in the same order.
            # as_completed() is intentionally avoided here: it returns futures in
            # completion order (non-deterministic), which would shuffle enc[i] away
            # from value[i]. Using future.result() on the ordered list preserves
            # the 1-to-1 correspondence between plaintext inputs and ciphertexts.
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._encrypt_single_optimized, val) for val in batch_values]
                batch_results = [f.result() for f in futures]

            encrypted_batch.extend(batch_results)
        
        return encrypted_batch
    
    def _encrypt_single_optimized(self, value: Union[float, int]) -> Union[ts.CKKSTensor, ts.BFVTensor]:
        """Encrypt a single value with optimization."""
        if self.scheme == FHEScheme.CKKS:
            # For CKKS, we can use vector encryption for better efficiency
            return ts.ckks_vector(self.context, [float(value)])
        elif self.scheme == FHEScheme.BFV:
            return ts.bfv_vector(self.context, [int(value)])

    
    def add_encrypted_batch_optimized(self, 
                                    enc_a_list: List[Union[ts.CKKSTensor, ts.BFVTensor]], 
                                    enc_b_list: List[Union[ts.CKKSTensor, ts.BFVTensor]],
                                    batch_size: int = 50) -> List[Union[ts.CKKSTensor, ts.BFVTensor]]:
        """
        Optimized batch addition with scheme-specific handling.
        
        Args:
            enc_a_list: List of first encrypted tensors
            enc_b_list: List of second encrypted tensors
            batch_size: Size of each batch for processing
            
        Returns:
            List of encrypted sum tensors
        """
        if len(enc_a_list) != len(enc_b_list):
            raise ValueError("Lists must have the same length")
        
        results = []

        print(f"Adding {len(enc_a_list)} encrypted pairs using {self.scheme.value} scheme...")

        for i in tqdm(range(0, len(enc_a_list), batch_size), desc=f"{self.scheme.value} Addition"):
            batch_a = enc_a_list[i:i + batch_size]
            batch_b = enc_b_list[i:i + batch_size]

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._add_encrypted_pair_optimized, a, b)
                           for a, b in zip(batch_a, batch_b)]
                batch_results = [f.result() for f in futures]

            results.extend(batch_results)
        
        return results
    
    def _add_encrypted_pair_optimized(self, 
                                    enc_a: Union[ts.CKKSTensor, ts.BFVTensor], 
                                    enc_b: Union[ts.CKKSTensor, ts.BFVTensor]) -> Union[ts.CKKSTensor, ts.BFVTensor]:
        """Add two encrypted values with optimization."""
        result = enc_a + enc_b
        return result
    
    def decrypt_batch_optimized(self, 
                               encrypted_list: List[Union[ts.CKKSTensor, ts.BFVTensor]], 
                               batch_size: int = 100) -> List[Union[float, int]]:
        """
        Optimized batch decryption with scheme-specific handling.
        
        Args:
            encrypted_list: List of encrypted tensors to decrypt
            batch_size: Size of each batch for processing
            
        Returns:
            List of decrypted values
        """
        if not encrypted_list:
            return []
        
        decrypted_batch = []

        print(f"Decrypting {len(encrypted_list)} values using {self.scheme.value} scheme...")

        for i in tqdm(range(0, len(encrypted_list), batch_size), desc=f"{self.scheme.value} Decryption"):
            batch_encrypted = encrypted_list[i:i + batch_size]

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._decrypt_single_optimized, enc_val)
                           for enc_val in batch_encrypted]
                batch_results = [f.result() for f in futures]

            decrypted_batch.extend(batch_results)
        
        return decrypted_batch
    
    def _decrypt_single_optimized(self, 
                                 encrypted_val: Union[ts.CKKSTensor, ts.BFVTensor]) -> Union[float, int]:
        """Decrypt a single value with optimization."""
        decrypted = encrypted_val.decrypt()[0]
        
        # Return appropriate type based on scheme
        if self.scheme == FHEScheme.CKKS:
            return float(decrypted)
        else:
            return int(decrypted)
    
    def multiply_encrypted_batch(self, 
                                enc_a_list: List[Union[ts.CKKSTensor, ts.BFVTensor]], 
                                enc_b_list: List[Union[ts.CKKSTensor, ts.BFVTensor]],
                                batch_size: int = 25) -> List[Union[ts.CKKSTensor, ts.BFVTensor]]:
        """
        Batch multiplication of encrypted values.
        Note: Multiplication increases noise significantly.
        
        Args:
            enc_a_list: List of first encrypted tensors
            enc_b_list: List of second encrypted tensors
            batch_size: Size of each batch for processing
            
        Returns:
            List of encrypted product tensors
        """
        if len(enc_a_list) != len(enc_b_list):
            raise ValueError("Lists must have the same length")
        
        results = []

        print(f"Multiplying {len(enc_a_list)} encrypted pairs using {self.scheme.value} scheme...")
        print("Warning: Multiplication increases noise significantly!")

        for i in tqdm(range(0, len(enc_a_list), batch_size), desc=f"{self.scheme.value} Multiplication"):
            batch_a = enc_a_list[i:i + batch_size]
            batch_b = enc_b_list[i:i + batch_size]

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._multiply_encrypted_pair, a, b)
                           for a, b in zip(batch_a, batch_b)]
                batch_results = [f.result() for f in futures]

            results.extend(batch_results)
        
        return results
    
    def _multiply_encrypted_pair(self, 
                                enc_a: Union[ts.CKKSTensor, ts.BFVTensor], 
                                enc_b: Union[ts.CKKSTensor, ts.BFVTensor]) -> Union[ts.CKKSTensor, ts.BFVTensor]:
        """Multiply two encrypted values."""
        result = enc_a * enc_b
        return result
    
    def benchmark_schemes(self, num_values: int = 1000) -> Dict:
        """
        Benchmark performance across different FHE schemes.
        
        Args:
            num_values: Number of values to test
            
        Returns:
            Dictionary with benchmark results
        """
        print(f"\n=== Multi-Scheme Benchmark ({num_values} values) ===")
        
        schemes_to_test = [FHEScheme.CKKS, FHEScheme.BFV]
        results = {}
        
        for scheme in schemes_to_test:
            print(f"\n--- Testing {scheme.value} scheme ---")
            
            # Create engine for this scheme
            engine = AdvancedFHE(
                scheme=scheme,
                max_workers=self.max_workers
            )
            
            # Generate appropriate test data
            if scheme == FHEScheme.CKKS:
                test_values = np.random.random(num_values).tolist()
            else:
                test_values = np.random.randint(1, 1000, num_values).tolist()
            
            scheme_results = {}
            
            # Encryption benchmark
            start_time = time.time()
            encrypted = engine.encrypt_batch_optimized(test_values)
            scheme_results['encryption_time'] = time.time() - start_time
            
            # Addition benchmark
            start_time = time.time()
            sums = engine.add_encrypted_batch_optimized(
                encrypted[:len(encrypted)//2], 
                encrypted[len(encrypted)//2:]
            )
            scheme_results['addition_time'] = time.time() - start_time
            
            # Decryption benchmark
            start_time = time.time()
            decrypted = engine.decrypt_batch_optimized(sums)
            scheme_results['decryption_time'] = time.time() - start_time
            
            # Calculate throughput
            scheme_results['encryption_throughput'] = num_values / scheme_results['encryption_time']
            scheme_results['addition_throughput'] = num_values / scheme_results['addition_time']
            scheme_results['decryption_throughput'] = num_values / scheme_results['decryption_time']
            
            results[scheme.value] = scheme_results
            
            print(f"  Encryption: {scheme_results['encryption_time']:.4f}s ({scheme_results['encryption_throughput']:.0f} ops/sec)")
            print(f"  Addition: {scheme_results['addition_time']:.4f}s ({scheme_results['addition_throughput']:.0f} ops/sec)")
            print(f"  Decryption: {scheme_results['decryption_time']:.4f}s ({scheme_results['decryption_throughput']:.0f} ops/sec)")
        
        return results
    
    def get_scheme_info(self) -> Dict:
        """Get information about the current FHE scheme."""
        info = {
            'scheme': self.scheme.value,
            'poly_modulus_degree': self.context.poly_modulus_degree(),
            'max_workers': self.max_workers
        }
        
        if self.scheme == FHEScheme.CKKS:
            info.update({
                'global_scale': self.context.global_scale(),
                'precision_bits': self.precision_bits
            })
        else:
            info.update({
                'plain_modulus': self.context.plain_modulus()
            })
        
        return info 