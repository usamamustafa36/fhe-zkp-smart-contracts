#!/usr/bin/env python3
"""
Resource Utilization Monitor

Tracks system resource usage during benchmarks:
- Peak RAM usage (MB)
- CPU utilization (%)
- Execution time
- Memory profiling
"""

import time
import psutil
import tracemalloc
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable
from contextlib import contextmanager


class ResourceMonitor:
    """Monitor CPU and memory usage during benchmark execution."""
    
    def __init__(self):
        """Initialize resource monitor."""
        self.results = []
        self.process = psutil.Process()
    
    @contextmanager
    def measure(self, component_name: str):
        """
        Context manager to measure resource usage.
        
        Args:
            component_name: Name of component being measured
            
        Usage:
            with monitor.measure("CKKS Encryption"):
                # code to measure
                pass
        """
        print(f"\n[Resource Monitor] Measuring: {component_name}")
        
        # Start tracemalloc
        tracemalloc.start()
        
        # Record initial state
        mem_before = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent_before = self.process.cpu_percent()
        start_time = time.time()
        
        # Peak tracking
        peak_memory = mem_before
        
        try:
            yield
        finally:
            # Record final state
            end_time = time.time()
            mem_after = self.process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = self.process.cpu_percent()
            
            # Get tracemalloc stats
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            peak_mb = peak / 1024 / 1024
            
            result = {
                'component': component_name,
                'execution_time_sec': float(end_time - start_time),
                'memory_before_mb': float(mem_before),
                'memory_after_mb': float(mem_after),
                'memory_delta_mb': float(mem_after - mem_before),
                'peak_memory_mb': float(peak_mb),
                'cpu_percent': float(cpu_percent),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            print(f"  Duration: {result['execution_time_sec']:.2f}s")
            print(f"  Memory Delta: {result['memory_delta_mb']:.2f} MB")
            print(f"  Peak Memory: {result['peak_memory_mb']:.2f} MB")
            print(f"  CPU: {result['cpu_percent']:.1f}%")
    
    def measure_function(self, component_name: str, func: Callable, *args, **kwargs) -> Dict:
        """
        Measure resource usage of a function call.
        
        Args:
            component_name: Name of component
            func: Function to measure
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Result from function
        """
        with self.measure(component_name):
            result = func(*args, **kwargs)
        
        return result
    
    def get_system_info(self) -> Dict:
        """Get system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'total_memory_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'available_memory_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, output_dir: str = 'evaluation/results/resources') -> str:
        """Save resource usage results to CSV."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = output_path / f"resource_usage_{timestamp}.csv"
        
        if self.results:
            keys = self.results[0].keys()
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.results)
            
            print(f"\n✅ Resource usage saved: {csv_file}")
            return str(csv_file)
        
        return ""


if __name__ == "__main__":
    # Example usage
    monitor = ResourceMonitor()
    
    with monitor.measure("Test Operation"):
        # Simulate work
        data = [i**2 for i in range(1000000)]
        time.sleep(1)
    
    print("\nSystem Info:", monitor.get_system_info())
    monitor.save_results()
