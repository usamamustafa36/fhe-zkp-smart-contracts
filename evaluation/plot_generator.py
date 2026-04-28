#!/usr/bin/env python3
"""
Plot Generator for Performance Evaluation

Generates all thesis-ready plots (300 DPI PNG):
- CKKS performance plots (4)
- Scaling analysis plots (3)
- ZKP metrics plots (3)
- End-to-end latency plots (1)
- Resource usage plots (2)
"""

import sys
import csv
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Set matplotlib to use a non-interactive backend
plt.switch_backend('Agg')


class PlotGenerator:
    """Generate thesis-ready performance plots."""
    
    def __init__(self, results_dir: str = 'evaluation/results', 
                 output_dir: str = 'evaluation/results/plots'):
        """
        Initialize plot generator.
        
        Args:
            results_dir: Directory containing CSV results
            output_dir: Directory to save plots
        """
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot style configuration
        plt.style.use('seaborn-v0_8-darkgrid')
        self.dpi = 300
        self.figsize = (10, 6)
        
        print(f"Plot Generator initialized")
        print(f"  Input: {self.results_dir}")
        print(f"  Output: {self.output_dir}")
    
    def load_csv(self, csv_file: Path) -> List[Dict]:
        """Load CSV file into list of dictionaries."""
        data = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    def find_latest_csv(self, subdir: str, pattern: str) -> Optional[Path]:
        """Find most recent CSV file matching pattern."""
        search_dir = self.results_dir / subdir
        if not search_dir.exists():
            return None
        
        files = list(search_dir.glob(f"{pattern}*.csv"))
        if not files:
            return None
        
        # Sort by modification time, get latest
        latest = max(files, key=lambda p: p.stat().st_mtime)
        return latest
    
    # ========================================================================
    # CKKS PERFORMANCE PLOTS
    # ========================================================================
    
    def plot_ckks_operation_latency(self, data: List[Dict]):
        """Bar chart: operation latencies."""
        print("\n[Plot] CKKS operation latency...")
        
        # Extract data
        operations = []
        latencies = []
        
        for row in data:
            if row.get('operation') in ['encryption', 'decryption', 'addition', 'multiplication']:
                # Try to get mean_time_sec, fallback to time_per_value_ms conversion
                latency = None
                if 'mean_time_sec' in row and row['mean_time_sec']:
                    latency = float(row['mean_time_sec']) * 1000  # Convert to ms
                elif 'time_per_value_ms' in row and row['time_per_value_ms']:
                    latency = float(row['time_per_value_ms'])
                
                # Only include if we have a valid latency
                if latency is not None:
                    operations.append(row['operation'].capitalize())
                    latencies.append(latency)
        
        if not operations:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=self.figsize)
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        bars = ax.bar(operations, latencies, color=colors[:len(operations)])
        
        ax.set_ylabel('Latency (ms)', fontsize=12)
        ax.set_title('CKKS Operation Latency Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        output_file = self.output_dir / 'ckks_operation_latency.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    def plot_noise_budget_vs_depth(self, data: List[Dict]):
        """Line chart: noise budget vs depth."""
        print("\n[Plot] Noise budget vs depth...")
        
        depths = []
        budgets = []
        
        for row in data:
            if row.get('metric') == 'noise_budget':
                depths.append(int(row['multiplicative_depth']))
                budgets.append(float(row['remaining_budget_percent']))
        
        if not depths:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(depths, budgets, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        
        ax.set_xlabel('Multiplicative Depth', fontsize=12)
        ax.set_ylabel('Remaining Noise Budget (%)', fontsize=12)
        ax.set_title('Noise Budget Degradation vs Multiplicative Depth', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'noise_budget_vs_depth.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    def plot_approximation_error_vs_depth(self, data: List[Dict]):
        """Line chart: approximation error vs depth."""
        print("\n[Plot] Approximation error vs depth...")
        
        depths = []
        abs_errors = []
        rel_errors = []
        
        for row in data:
            if row.get('metric') == 'approximation_error' and 'absolute_error' in row and 'relative_error' in row:
                depths.append(int(row['multiplicative_depth']))
                abs_errors.append(float(row['absolute_error']))
                rel_errors.append(float(row['relative_error']))
        
        if not depths:
            print("  No data available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Absolute error
        ax1.plot(depths, abs_errors, marker='o', linewidth=2, markersize=8, color='#A23B72')
        ax1.set_xlabel('Multiplicative Depth', fontsize=12)
        ax1.set_ylabel('Absolute Error', fontsize=12)
        ax1.set_title('Absolute Approximation Error', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        # Relative error
        ax2.plot(depths, rel_errors, marker='s', linewidth=2, markersize=8, color='#F18F01')
        ax2.set_xlabel('Multiplicative Depth', fontsize=12)
        ax2.set_ylabel('Relative Error', fontsize=12)
        ax2.set_title('Relative Approximation Error', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
        
        plt.tight_layout()
        output_file = self.output_dir / 'approximation_error_vs_depth.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    def plot_ciphertext_size_comparison(self, data: List[Dict]):
        """Bar chart: ciphertext vs plaintext size."""
        print("\n[Plot] Ciphertext size comparison...")
        
        for row in data:
            if row.get('metric') == 'ciphertext_size':
                plaintext_kb = float(row['plaintext_size_bytes']) / 1024
                ciphertext_kb = float(row['ciphertext_size_bytes']) / 1024
                
                fig, ax = plt.subplots(figsize=(8, 6))
                categories = ['Plaintext', 'Ciphertext']
                sizes = [plaintext_kb, ciphertext_kb]
                colors = ['#2E86AB', '#C73E1D']
                
                bars = ax.bar(categories, sizes, color=colors)
                ax.set_ylabel('Size (KB)', fontsize=12)
                ax.set_title('Ciphertext vs Plaintext Size', fontsize=14, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f} KB',
                           ha='center', va='bottom', fontsize=10)
                
                plt.tight_layout()
                output_file = self.output_dir / 'ciphertext_size_comparison.png'
                plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                print(f"  Saved: {output_file}")
                break
    
    # ========================================================================
    # SCALING ANALYSIS PLOTS
    # ========================================================================
    
    def plot_latency_vs_vector_size(self, data: List[Dict]):
        """Line chart: latency vs vector size."""
        print("\n[Plot] Latency vs vector size...")
        
        sizes = []
        latencies = []
        
        for row in data:
            if row.get('metric') == 'vector_size_scaling':
                sizes.append(int(row['vector_size']))
                latencies.append(float(row['mean_latency_sec']))
        
        if not sizes:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(sizes, latencies, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        
        ax.set_xlabel('Vector Size', fontsize=12)
        ax.set_ylabel('Latency (seconds)', fontsize=12)
        ax.set_title('Encryption Latency vs Input Vector Size', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        plt.tight_layout()
        output_file = self.output_dir / 'latency_vs_vector_size.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    def plot_latency_vs_depth(self, data: List[Dict]):
        """Line chart: latency vs multiplicative depth."""
        print("\n[Plot] Latency vs multiplicative depth...")
        
        depths = []
        latencies = []
        
        for row in data:
            if (row.get('metric') == 'depth_scaling' and 
                'mean_latency_sec' in row and 
                row['mean_latency_sec'] and 
                row['mean_latency_sec'] != ''):
                depths.append(int(row['multiplicative_depth']))
                latencies.append(float(row['mean_latency_sec']))
        
        if not depths:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(depths, latencies, marker='s', linewidth=2, markersize=8, color='#A23B72')
        
        ax.set_xlabel('Multiplicative Depth', fontsize=12)
        ax.set_ylabel('Latency (seconds)', fontsize=12)
        ax.set_title('Computation Latency vs Multiplicative Depth', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'latency_vs_depth.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    def plot_noise_growth_vs_depth(self, data: List[Dict]):
        """Line chart: noise growth vs depth."""
        print("\n[Plot] Noise growth vs depth...")
        
        depths = []
        noise_db = []
        
        for row in data:
            if row.get('metric') == 'noise_growth':
                depths.append(int(row['multiplicative_depth']))
                noise_db.append(float(row['noise_growth_db']))
        
        if not depths:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(depths, noise_db, marker='d', linewidth=2, markersize=8, color='#F18F01')
        
        ax.set_xlabel('Multiplicative Depth', fontsize=12)
        ax.set_ylabel('Noise Growth (dB)', fontsize=12)
        ax.set_title('Noise Growth vs Multiplicative Depth', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'noise_growth_vs_depth.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    # ========================================================================
    # ZKP METRICS PLOTS
    # ========================================================================
    
    def plot_zkp_prover_vs_verifier_time(self, data: List[Dict]):
        """Bar chart: prover vs verifier time."""
        print("\n[Plot] ZKP prover vs verifier time...")
        
        prover_time = 0
        verifier_time = 0
        
        for row in data:
            if row.get('metric') == 'proof_generation' and 'mean_time_sec' in row:
                prover_time = float(row['mean_time_sec']) * 1000  # Convert to ms
            elif row.get('metric') == 'verification' and 'mean_time_ms' in row:
                verifier_time = float(row['mean_time_ms'])
        
        if prover_time == 0 and verifier_time == 0:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        categories = ['Prover', 'Verifier']
        times = [prover_time, verifier_time]
        colors = ['#C73E1D', '#2E86AB']
        
        bars = ax.bar(categories, times, color=colors)
        ax.set_ylabel('Time (ms)', fontsize=12)
        ax.set_title('ZKP Prover vs Verifier Time', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f} ms',
                   ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        output_file = self.output_dir / 'zkp_prover_vs_verifier_time.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    def plot_zkp_proof_size(self, data: List[Dict]):
        """Bar chart: proof size."""
        print("\n[Plot] ZKP proof size...")
        
        for row in data:
            if row.get('metric') == 'proof_size' and 'total_size_bytes' in row:
                proof_kb = float(row['total_size_bytes']) / 1024
                
                fig, ax = plt.subplots(figsize=(6, 6))
                bars = ax.bar(['Proof Size'], [proof_kb], color='#A23B72', width=0.5)
                
                ax.set_ylabel('Size (KB)', fontsize=12)
                ax.set_title('ZKP Proof Size', fontsize=14, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                
                # Add value label
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f} KB',
                           ha='center', va='bottom', fontsize=10)
                
                plt.tight_layout()
                output_file = self.output_dir / 'zkp_proof_size.png'
                plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                print(f"  Saved: {output_file}")
                break
    
    def plot_zkp_vs_fhe_cost(self, zkp_data: List[Dict], fhe_data: List[Dict]):
        """Bar chart: computational cost comparison."""
        print("\n[Plot] ZKP vs FHE cost comparison...")
        
        zkp_time = 0
        fhe_time = 0
        
        # Get ZKP prover time
        for row in zkp_data:
            if row.get('metric') == 'proof_generation' and 'mean_time_sec' in row:
                zkp_time = float(row['mean_time_sec']) * 1000
                break
        
        # Get FHE encryption time
        for row in fhe_data:
            if row.get('operation') == 'encryption' and 'mean_time_sec' in row:
                fhe_time = float(row['mean_time_sec']) * 1000
                break
        
        if zkp_time == 0 and fhe_time == 0:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        categories = ['ZKP Proof Gen', 'FHE Encryption']
        times = [zkp_time, fhe_time]
        colors = ['#C73E1D', '#2E86AB']
        
        bars = ax.bar(categories, times, color=colors)
        ax.set_ylabel('Time (ms)', fontsize=12)
        ax.set_title('ZKP vs FHE Computational Cost', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f} ms',
                   ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        output_file = self.output_dir / 'zkp_vs_fhe_cost.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    # ========================================================================
    # END-TO-END PLOTS
    # ========================================================================
    
    def plot_end_to_end_latency_breakdown(self, data: List[Dict]):
        """Stacked bar chart: end-to-end latency breakdown."""
        print("\n[Plot] End-to-end latency breakdown...")
        
        # Find average row
        avg_row = None
        for row in data:
            if row.get('metric') == 'end_to_end_average':
                avg_row = row
                break
        
        if not avg_row:
            print("  No average data available")
            return
        
        # Extract stage times
        stages = []
        times = []
        
        stage_keys = [
            ('zkp_proof_generation_sec_mean', 'ZKP Proof Gen'),
            ('fhe_encryption_sec_mean', 'FHE Encryption'),
            ('verification_estimated_sec_mean', 'Verification'),
            ('homomorphic_computation_sec_mean', 'Computation'),
            ('fhe_decryption_sec_mean', 'FHE Decryption')
        ]
        
        for key, label in stage_keys:
            if key in avg_row and avg_row[key]:
                stages.append(label)
                times.append(float(avg_row[key]) * 1000)  # Convert to ms
        
        if not stages:
            print("  No stage data available")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#C73E1D', '#2E86AB', '#A23B72', '#F18F01', '#06A77D']
        
        bars = ax.bar(range(len(stages)), times, color=colors[:len(stages)])
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages, rotation=15, ha='right')
        ax.set_ylabel('Latency (ms)', fontsize=12)
        ax.set_title('End-to-End Pipeline Latency Breakdown', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_file = self.output_dir / 'end_to_end_latency_breakdown.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    # ========================================================================
    # RESOURCE USAGE PLOTS
    # ========================================================================
    
    def plot_peak_ram_per_component(self, data: List[Dict]):
        """Bar chart: peak RAM per component."""
        print("\n[Plot] Peak RAM per component...")
        
        components = []
        peak_ram = []
        
        for row in data:
            if 'component' in row and 'peak_memory_mb' in row:
                components.append(row['component'])
                peak_ram.append(float(row['peak_memory_mb']))
        
        if not components:
            print("  No data available")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(components)), peak_ram, color='#06A77D')
        ax.set_xticks(range(len(components)))
        ax.set_xticklabels(components, rotation=45, ha='right')
        ax.set_ylabel('Peak RAM (MB)', fontsize=12)
        ax.set_title('Peak RAM Usage per Component', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        output_file = self.output_dir / 'peak_ram_per_component.png'
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {output_file}")
    
    # ========================================================================
    # MAIN GENERATION
    # ========================================================================
    
    def generate_all_plots(self):
        """Generate all plots from available data."""
        print("="*80)
        print("GENERATING ALL PERFORMANCE PLOTS")
        print("="*80)
        
        # Load CKKS data
        ckks_csv = self.find_latest_csv('performance', 'performance_ckks')
        if ckks_csv:
            print(f"\nLoading CKKS data from: {ckks_csv}")
            ckks_data = self.load_csv(ckks_csv)
            self.plot_ckks_operation_latency(ckks_data)
            self.plot_noise_budget_vs_depth(ckks_data)
            self.plot_approximation_error_vs_depth(ckks_data)
            self.plot_ciphertext_size_comparison(ckks_data)
        
        # Load Scaling data
        scaling_csv = self.find_latest_csv('scaling', 'scaling_ckks')
        if scaling_csv:
            print(f"\nLoading Scaling data from: {scaling_csv}")
            scaling_data = self.load_csv(scaling_csv)
            self.plot_latency_vs_vector_size(scaling_data)
            self.plot_latency_vs_depth(scaling_data)
            self.plot_noise_growth_vs_depth(scaling_data)
        
        # Load ZKP data
        zkp_csv = self.find_latest_csv('zkp', 'zkp_metrics')
        if zkp_csv:
            print(f"\nLoading ZKP data from: {zkp_csv}")
            zkp_data = self.load_csv(zkp_csv)
            self.plot_zkp_prover_vs_verifier_time(zkp_data)
            self.plot_zkp_proof_size(zkp_data)
            
            # ZKP vs FHE comparison
            if ckks_csv:
                self.plot_zkp_vs_fhe_cost(zkp_data, ckks_data)
        
        # Load End-to-End data
        e2e_csv = self.find_latest_csv('end_to_end', 'end_to_end_latency')
        if e2e_csv:
            print(f"\nLoading End-to-End data from: {e2e_csv}")
            e2e_data = self.load_csv(e2e_csv)
            self.plot_end_to_end_latency_breakdown(e2e_data)
        
        # Load Resource data
        resource_csv = self.find_latest_csv('resources', 'resource_usage')
        if resource_csv:
            print(f"\nLoading Resource data from: {resource_csv}")
            resource_data = self.load_csv(resource_csv)
            self.plot_peak_ram_per_component(resource_data)
        
        print("\n" + "="*80)
        print("ALL PLOTS GENERATED SUCCESSFULLY")
        print(f"Output directory: {self.output_dir}")
        print("="*80)


if __name__ == "__main__":
    generator = PlotGenerator()
    generator.generate_all_plots()
