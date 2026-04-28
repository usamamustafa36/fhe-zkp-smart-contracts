#!/usr/bin/env python3
"""
Master's Thesis - Complete Evaluation Demo
===========================================

This script runs ALL thesis evaluation modules in sequence:
1. ZKP Validator Demo
2. Correctness Validation
3. Cost Analysis
4. Comparative Framework
5. Performance Benchmarks (if TenSEAL available)
6. Scaling Experiments (if TenSEAL available)

USAGE:
    python3 thesis-demo.py

OUTPUT:
    - Console demonstrations
    - JSON/CSV files in evaluation/results/
    - Complete thesis evaluation data

THESIS REFERENCE: Chapter 5 & 6 - Evaluation and Demonstration
"""

import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title):
    """Print formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_step(step_num, total_steps, description):
    """Print step progress."""
    print(f"\n[{step_num}/{total_steps}] {description}")
    print("-" * 60)


def run_module(module_path, description):
    """Run a Python module and capture output."""
    print(f"\n▶️  Running: {module_path}")
    result = subprocess.run(
        [sys.executable, module_path],
        capture_output=False,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ {description} - COMPLETE")
    else:
        print(f"⚠️  {description} - FAILED (but continuing...)")
    return result.returncode == 0


def check_tenseal():
    """Check if TenSEAL is available."""
    try:
        import tenseal
        return True
    except ImportError:
        return False


def main():
    """Run complete thesis evaluation."""
    
    # Start time
    start_time = datetime.now()
    
    print_header("🎓 MASTER'S THESIS - COMPLETE EVALUATION DEMO")
    print("Project: Privacy-Preserving Smart Contract Framework")
    print("Author: Master's Thesis Student")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check TenSEAL availability
    has_tenseal = check_tenseal()
    if has_tenseal:
        print("\n✅ TenSEAL detected - Will run FULL evaluation (with real FHE)")
        total_steps = 6
    else:
        print("\n⚠️  TenSEAL not found - Will run PARTIAL evaluation (estimates only)")
        print("   To get real FHE data: pip install tenseal==0.3.14")
        total_steps = 4
    
    results = []
    
    # =========================================================================
    # STEP 1: ZKP Validator Demo
    # =========================================================================
    print_step(1, total_steps, "ZKP Input Validator Demo")
    success = run_module("crypto/zkp_validator.py", "ZKP Validator")
    results.append(("ZKP Validator", success))
    
    # =========================================================================
    # STEP 2: Correctness Validation
    # =========================================================================
    print_step(2, total_steps, "FHE Correctness Validation")
    success = run_module("crypto/correctness.py", "Correctness Module")
    results.append(("Correctness", success))
    
    # =========================================================================
    # STEP 3: Cost Analysis
    # =========================================================================
    print_step(3, total_steps, "Ciphertext & Blockchain Cost Analysis")
    success = run_module("evaluation/cost_analysis.py", "Cost Analysis")
    results.append(("Cost Analysis", success))
    
    # =========================================================================
    # STEP 4: Comparative Framework
    # =========================================================================
    print_step(4, total_steps, "Comparative Framework Analysis")
    success = run_module("evaluation/comparative.py", "Comparative Analysis")
    results.append(("Comparative Analysis", success))
    
    # =========================================================================
    # STEP 5: Performance Benchmarks (requires TenSEAL)
    # =========================================================================
    if has_tenseal:
        print_step(5, total_steps, "Performance Benchmarks (5-10 minutes)")
        print("⏱️  This will take several minutes - measuring real FHE performance...")
        success = run_module("evaluation/performance.py", "Performance Benchmarks")
        results.append(("Performance", success))
    
    # =========================================================================
    # STEP 6: Scaling Experiments (requires TenSEAL)
    # =========================================================================
    if has_tenseal:
        print_step(6, total_steps, "Scaling Experiments (10-15 minutes)")
        print("⏱️  This will take several minutes - analyzing scalability...")
        success = run_module("evaluation/scaling.py", "Scaling Experiments")
        results.append(("Scaling", success))
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("📊 EVALUATION SUMMARY")
    
    print("Results:")
    for module, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}  {module}")
    
    print(f"\nTotal Time: {duration}")
    print(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show generated files
    print("\n📁 Generated Files:")
    perf_dir = Path("evaluation/results/performance")
    scaling_dir = Path("evaluation/results/scaling")
    
    if perf_dir.exists():
        files = list(perf_dir.glob("*.json")) + list(perf_dir.glob("*.csv"))
        for f in files:
            print(f"  ✅ {f}")
    
    if scaling_dir.exists():
        files = list(scaling_dir.glob("*.json")) + list(scaling_dir.glob("*.csv"))
        for f in files:
            print(f"  ✅ {f}")
    
    # Final instructions
    print_header("🎓 NEXT STEPS FOR THESIS")
    
    print("1. Import generated CSV/JSON files into thesis")
    print("2. Use data for:")
    print("   - Table 5.2: Performance Results")
    print("   - Table 5.3: Cost Analysis")
    print("   - Figure 5.1-5.2: Scaling Plots")
    print("   - Table 7.1: Comparative Analysis")
    print("\n3. Reference documentation:")
    print("   - crypto/threat_model.md → Chapter 3")
    print("   - docs/limitations.md → Chapter 7")
    print("   - docs/environment.md → Appendix A")
    
    if not has_tenseal:
        print("\n⚠️  NOTE: Install TenSEAL for complete evaluation:")
        print("   pip install tenseal==0.3.14")
        print("   then run: python3 thesis-demo.py")
    
    print("\n" + "="*80)
    print("✅ THESIS EVALUATION COMPLETE!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
