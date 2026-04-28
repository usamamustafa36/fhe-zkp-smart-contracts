#!/usr/bin/env python3
"""
Comparative Analysis Framework

THESIS REFERENCE: Chapter 7, Section 7.1 - Comparative Analysis

Compares this framework against alternative approaches:
- Plain smart contracts
- ZKP-only systems  
- FHE-only systems
- This framework (FHE + ZKP)
"""

import json
import pandas as pd
from pathlib import Path

COMPARISON_TABLE = {
    'Plain Smart Contracts': {
        'privacy': 'None - all data public',
        'verifiability': 'Full - on-chain verification',
        'computation_overhead': '1x (baseline)',
        'storage_overhead': '1x (baseline)',
        'trust_assumptions': 'Blockchain only',
        'use_cases': 'Public computations'
    },
    'ZKP-only Systems': {
        'privacy': 'High - zero-knowledge proofs',
        'verifiability': 'Full - proof verification',
        'computation_overhead': '100-1000x (proof generation)',
        'storage_overhead': 'Low - compact proofs',
        'trust_assumptions': 'Cryptographic assumptions',
        'use_cases': 'Private verification'
    },
    'FHE-only Systems': {
        'privacy': 'Full - encrypted computation',
        'verifiability': 'Limited - trust decryptor',
        'computation_overhead': '1000-10000x',
        'storage_overhead': '500-1000x',
        'trust_assumptions': 'Key holder trust',
        'use_cases': 'Private computation'
    },
    'This Framework (FHE + ZKP)': {
        'privacy': 'High - FHE encryption',
        'verifiability': 'Medium - abstracted ZKP',
        'computation_overhead': '1000-10000x (FHE dominant)',
        'storage_overhead': '500-1000x (ciphertexts)',
        'trust_assumptions': 'Key holder + ZKP oracle',
        'use_cases': 'Privacy-first with validation'
    }
}


def generate_comparison_table():
    """Generate comparison table for thesis."""
    df = pd.DataFrame(COMPARISON_TABLE).T
    print("\nComparative Analysis - Privacy-Preserving Approaches\n")
    print(df.to_string())
    
    # Save CSV
    output_dir = Path('evaluation/results/performance/')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_dir / 'comparative_analysis.csv')
    print(f"\n✅ Saved to: {output_dir}/comparative_analysis.csv")
    
    return df


if __name__ == "__main__":
    generate_comparison_table()
