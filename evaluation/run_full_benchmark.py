#!/usr/bin/env python3
"""
Full Performance Evaluation Pipeline

Orchestrates all benchmarks and generates complete results:
- CKKS/FHE performance
- Scaling analysis
- ZKP metrics
- End-to-end latency
- Resource utilization
- All visualizations
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.ckks_benchmarker import CKKSBenchmarker
from evaluation.scaling_benchmarker import ScalingBenchmarker
from evaluation.zkp_benchmarker import ZKPBenchmarker
from evaluation.end_to_end_benchmarker import EndToEndBenchmarker
from evaluation.resource_monitor import ResourceMonitor
from evaluation.plot_generator import PlotGenerator


class FullBenchmarkPipeline:
    """Complete performance evaluation pipeline."""
    
    def __init__(self, quick: bool = False):
        """
        Initialize pipeline.
        
        Args:
            quick: If True, run reduced iterations for quick testing
        """
        self.quick = quick
        self.monitor = ResourceMonitor()
        self.start_time = None
        self.results_summary = {}
        
        print("="*80)
        print("FULL PERFORMANCE EVALUATION PIPELINE")
        print("="*80)
        print(f"Mode: {'QUICK TEST' if quick else 'FULL EVALUATION'}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def run_ckks_benchmarks(self):
        """Run CKKS/FHE performance benchmarks."""
        print("\n" + "="*80)
        print("PHASE 1: CKKS/FHE PERFORMANCE BENCHMARKS")
        print("="*80)
        
        with self.monitor.measure("CKKS Benchmarking"):
            iterations = 3 if self.quick else 10
            benchmarker = CKKSBenchmarker(iterations=iterations)
            benchmarker.run_all_benchmarks()
            csv_file = benchmarker.save_results()
            self.results_summary['ckks_csv'] = csv_file
    
    def run_scaling_benchmarks(self):
        """Run scaling analysis benchmarks."""
        print("\n" + "="*80)
        print("PHASE 2: SCALING ANALYSIS BENCHMARKS")
        print("="*80)
        
        with self.monitor.measure("Scaling Benchmarking"):
            iterations = 2 if self.quick else 5
            benchmarker = ScalingBenchmarker(iterations=iterations)
            benchmarker.run_all_benchmarks()
            csv_file = benchmarker.save_results()
            self.results_summary['scaling_csv'] = csv_file
    
    def run_zkp_benchmarks(self):
        """Run ZKP performance benchmarks."""
        print("\n" + "="*80)
        print("PHASE 3: ZKP (GROTH16) BENCHMARKS")
        print("="*80)
        
        with self.monitor.measure("ZKP Benchmarking"):
            benchmarker = ZKPBenchmarker()
            benchmarker.run_all_benchmarks()
            csv_file = benchmarker.save_results()
            self.results_summary['zkp_csv'] = csv_file
    
    def run_end_to_end_benchmarks(self):
        """Run end-to-end pipeline benchmarks."""
        print("\n" + "="*80)
        print("PHASE 4: END-TO-END PIPELINE BENCHMARKS")
        print("="*80)
        
        with self.monitor.measure("End-to-End Benchmarking"):
            iterations = 2 if self.quick else 5
            benchmarker = EndToEndBenchmarker(iterations=iterations)
            benchmarker.run_all_benchmarks()
            csv_file = benchmarker.save_results()
            self.results_summary['e2e_csv'] = csv_file
    
    def generate_visualizations(self):
        """Generate all plots."""
        print("\n" + "="*80)
        print("PHASE 5: GENERATING VISUALIZATIONS")
        print("="*80)
        
        with self.monitor.measure("Plot Generation"):
            generator = PlotGenerator()
            generator.generate_all_plots()
    
    def save_resource_usage(self):
        """Save resource usage data."""
        print("\n" + "="*80)
        print("SAVING RESOURCE USAGE DATA")
        print("="*80)
        
        csv_file = self.monitor.save_results()
        self.results_summary['resource_csv'] = csv_file
    
    def print_final_summary(self):
        """Print final summary report."""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("="*80)
        print("  ALL PERFORMANCE METRICS GENERATED SUCCESSFULLY")
        print("  Ready for Chapter 8 inclusion.")
        print("="*80)
        print("="*80)
        
        print("\n📊 GENERATED OUTPUTS:")
        print("-" * 80)
        
        print("\n📁 CSV Data Files:")
        for key, value in self.results_summary.items():
            if value and 'csv' in key:
                print(f"  ✓ {value}")
        
        print("\n📁 Visualization Files:")
        plots_dir = Path("evaluation/results/plots")
        if plots_dir.exists():
            plots = list(plots_dir.glob("*.png"))
            print(f"  📍 Location: {plots_dir}")
            print(f"  📈 Total plots: {len(plots)}")
            for plot in sorted(plots):
                print(f"      - {plot.name}")
        
        print("\n⏱️  EXECUTION SUMMARY:")
        print("-" * 80)
        print(f"  Total Duration: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📌 NEXT STEPS:")
        print("-" * 80)
        print("  1. Review generated plots in evaluation/results/plots/")
        print("  2. Import CSV data into thesis tables")
        print("  3. Embed PNG plots in Chapter 8 (300 DPI ready)")
        
        print("\n" + "="*80)
        print("Evaluation pipeline complete! 🎉")
        print("="*80 + "\n")
    
    def run_full_pipeline(self):
        """Execute complete pipeline."""
        self.start_time = time.time()
        
        try:
            # Run all benchmarks
            self.run_ckks_benchmarks()
            self.run_scaling_benchmarks()
            self.run_zkp_benchmarks()
            self.run_end_to_end_benchmarks()
            
            # Generate visualizations
            self.generate_visualizations()
            
            # Save resource monitoring
            self.save_resource_usage()
            
            # Print summary
            self.print_final_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Pipeline interrupted by user")
            print("Partial results may be available in evaluation/results/")
            return False
            
        except Exception as e:
            print(f"\n\n❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            print("\nPartial results may be available in evaluation/results/")
            return False


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(
        description="Full Performance Evaluation Pipeline for Thesis"
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick test with reduced iterations'
    )
    
    args = parser.parse_args()
    
    pipeline = FullBenchmarkPipeline(quick=args.quick)
    success = pipeline.run_full_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
