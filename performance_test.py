#!/usr/bin/env python3
"""
Performance testing script for aimassist
"""

import time
import threading
import statistics
from typing import List, Dict, Any
import json

from core import Core
from config import Config
from performance_monitor import PerformanceMonitor
from performance_config import get_performance_profile, get_available_profiles, apply_performance_profile


class PerformanceTester:
    """Performance testing for aimassist"""
    
    def __init__(self):
        self.config = Config()
        self.core = Core(self.config)
        self.monitor = PerformanceMonitor()
        self.test_results = {}
        
    def run_latency_test(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """Test input latency and responsiveness"""
        print(f"Running latency test for {duration_seconds} seconds...")
        
        self.monitor.start_monitoring()
        self.core.start()
        self.core.set_enabled(True)
        
        # simulate mouse movements
        test_start = time.monotonic()
        movement_count = 0
        
        while time.monotonic() - test_start < duration_seconds:
            self.core.on_move(100, 100)
            time.sleep(0.001)  # 1ms 
            movement_count += 1
            
            self.monitor.record_frame()
        
        self.core.stop()
        self.monitor.stop_monitoring()
        
        results = self.monitor.get_performance_summary()
        results['movements_per_second'] = movement_count / duration_seconds
        results['test_duration'] = duration_seconds
        
        return results
    
    def run_stress_test(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Test performance under stress conditions"""
        print(f"Running stress test for {duration_seconds} seconds...")
        
        self.monitor.start_monitoring()
        self.core.start()
        self.core.set_enabled(True)
        
        stress_threads = []
        stop_event = threading.Event()
        
        def stress_worker():
            while not stop_event.is_set():
                for i in range(100):
                    if stop_event.is_set():
                        break
                    self.core.on_move(i, i)
                    time.sleep(0.0001)  # 0.1ms
                
                self.core.on_click(100, 100, None, True)
                time.sleep(0.001)
                self.core.on_click(100, 100, None, False)
        
        for i in range(3):
            thread = threading.Thread(target=stress_worker, daemon=True)
            thread.start()
            stress_threads.append(thread)
        
        time.sleep(duration_seconds)
        stop_event.set()
        
        for thread in stress_threads:
            thread.join(timeout=1.0)
        
        self.core.stop()
        self.monitor.stop_monitoring()
        
        results = self.monitor.get_performance_summary()
        results['test_duration'] = duration_seconds
        results['stress_threads'] = len(stress_threads)
        
        return results
    
    def test_performance_profiles(self) -> Dict[str, Any]:
        """Test different performance profiles"""
        print("Testing different performance profiles...")
        
        profile_results = {}
        
        for profile_name in get_available_profiles():
            print(f"Testing profile: {profile_name}")
            
            profile = get_performance_profile(profile_name)
            apply_performance_profile(self.core, profile)
            
            results = self.run_latency_test(duration_seconds=5)
            profile_results[profile_name] = results
            
            self.monitor.reset_stats()
        
        return profile_results
    
    def benchmark_core_operations(self) -> Dict[str, Any]:
        """Benchmark individual core operations"""
        print("Benchmarking core operations...")
        
        self.core.start()
        self.core.set_enabled(True)
        
        movement_times = []
        for i in range(1000):
            start_time = time.perf_counter()
            self.core.on_move(i, i)
            end_time = time.perf_counter()
            movement_times.append((end_time - start_time) * 1000)  
        
        gamepad_times = []
        for i in range(100):
            start_time = time.perf_counter()
            self.core.update_gamepad_stick(i, i)
            end_time = time.perf_counter()
            gamepad_times.append((end_time - start_time) * 1000)  
        
        recoil_times = []
        for i in range(100):
            start_time = time.perf_counter()
            recoil_offset = max(i - 100, -1000)
            end_time = time.perf_counter()
            recoil_times.append((end_time - start_time) * 1000)  
        
        self.core.stop()
        
        return {
            'mouse_movement': {
                'avg_time_ms': statistics.mean(movement_times),
                'min_time_ms': min(movement_times),
                'max_time_ms': max(movement_times),
                'std_dev_ms': statistics.stdev(movement_times) if len(movement_times) > 1 else 0
            },
            'gamepad_update': {
                'avg_time_ms': statistics.mean(gamepad_times),
                'min_time_ms': min(gamepad_times),
                'max_time_ms': max(gamepad_times),
                'std_dev_ms': statistics.stdev(gamepad_times) if len(gamepad_times) > 1 else 0
            },
            'recoil_calculation': {
                'avg_time_ms': statistics.mean(recoil_times),
                'min_time_ms': min(recoil_times),
                'max_time_ms': max(recoil_times),
                'std_dev_ms': statistics.stdev(recoil_times) if len(recoil_times) > 1 else 0
            }
        }
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete performance benchmark"""
        print("Starting full performance benchmark...")
        
        benchmark_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': self._get_system_info(),
            'latency_test': self.run_latency_test(duration_seconds=10),
            'stress_test': self.run_stress_test(duration_seconds=20),
            'performance_profiles': self.test_performance_profiles(),
            'core_operations': self.benchmark_core_operations()
        }
        
        self.test_results = benchmark_results
        return benchmark_results
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import psutil
            import platform
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2)
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    def save_results(self, filename: str = 'benchmark_results.json'):
        """Save benchmark results to file"""
        if self.test_results:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"Results saved to {filename}")
    
    def print_summary(self):
        """Print benchmark summary"""
        if not self.test_results:
            print("No benchmark results available. Run a test first.")
            return
        
        print("\n" + "="*50)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*50)
        
        print(f"\nSystem: {self.test_results['system_info'].get('platform', 'Unknown')}")
        print(f"CPU Cores: {self.test_results['system_info'].get('cpu_count', 'Unknown')}")
        print(f"Memory: {self.test_results['system_info'].get('memory_total_gb', 'Unknown')} GB")
        
        latency = self.test_results['latency_test']
        print(f"\nLatency Test:")
        print(f"  FPS: {latency.get('fps', 0):.1f}")
        print(f"  Avg Frame Time: {latency.get('avg_frame_time_ms', 0):.2f} ms")
        print(f"  CPU Usage: {latency.get('cpu_usage_percent', 0):.1f}%")
        print(f"  Memory Usage: {latency.get('memory_usage_mb', 0):.1f} MB")
        
        core_ops = self.test_results['core_operations']
        print(f"\nCore Operations:")
        print(f"  Mouse Movement: {core_ops['mouse_movement']['avg_time_ms']:.3f} ms avg")
        print(f"  Gamepad Update: {core_ops['gamepad_update']['avg_time_ms']:.3f} ms avg")
        print(f"  Recoil Calc: {core_ops['recoil_calculation']['avg_time_ms']:.3f} ms avg")
        
        profiles = self.test_results['performance_profiles']
        print(f"\nPerformance Profiles:")
        for profile_name, profile_results in profiles.items():
            fps = profile_results.get('fps', 0)
            cpu = profile_results.get('cpu_usage_percent', 0)
            print(f"  {profile_name}: {fps:.1f} FPS, {cpu:.1f}% CPU")


def main():
    """Main function for running performance tests"""
    print("AimAssist Performance Testing")
    print("="*40)
    
    tester = PerformanceTester()
    
    try:
        results = tester.run_full_benchmark()
        
        tester.print_summary()
        
        tester.save_results()
        
        print("\nBenchmark completed successfully!")
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
