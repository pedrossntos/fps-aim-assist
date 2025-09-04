import time
import threading
import psutil
import os
from collections import deque
from typing import Dict, Any, Optional


class PerformanceMonitor:
    """Performance monitoring for the aimassist application"""
    
    def __init__(self, max_samples: int = 100):
        self.max_samples = max_samples
        self.running = False
        
        self.cpu_usage = deque(maxlen=max_samples)
        self.memory_usage = deque(maxlen=max_samples)
        self.frame_times = deque(maxlen=max_samples)
        self.input_latency = deque(maxlen=max_samples)
        
        self.thread_stats = {}
        
        self.last_frame_time = time.monotonic()
        self.frame_count = 0
        
        self.process = psutil.Process(os.getpid())
        
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start the performance monitoring"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop the performance monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
    def record_frame(self):
        """Record a frame for FPS calculation"""
        current_time = time.monotonic()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        self.frame_count += 1
        
    def record_input_latency(self, latency_ms: float):
        """Record input latency in milliseconds"""
        self.input_latency.append(latency_ms)
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.cpu_usage.append(cpu_percent)
                
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.memory_usage.append(memory_mb)
                
                self._update_thread_stats()
                
                time.sleep(0.5)  # 500ms
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(1.0)
                
    def _update_thread_stats(self):
        """Update thread statistics"""
        try:
            threads = self.process.threads()
            for thread in threads:
                thread_id = thread.id
                if thread_id not in self.thread_stats:
                    self.thread_stats[thread_id] = {
                        'cpu_percent': 0,
                        'user_time': 0,
                        'system_time': 0
                    }
                
                try:
                    thread_process = psutil.Process()
                    thread_process.cpu_percent()
                    time.sleep(0.1)
                    cpu_percent = thread_process.cpu_percent()
                    self.thread_stats[thread_id]['cpu_percent'] = cpu_percent
                except:
                    pass
                    
        except Exception as e:
            pass
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of current performance metrics"""
        if not self.cpu_usage:
            return {}
            
        avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage)
        avg_memory = sum(self.memory_usage) / len(self.memory_usage)
        
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            fps = 0
            
        avg_latency = 0
        if self.input_latency:
            avg_latency = sum(self.input_latency) / len(self.input_latency)
            
        return {
            'cpu_usage_percent': round(avg_cpu, 2),
            'memory_usage_mb': round(avg_memory, 2),
            'fps': round(fps, 1),
            'avg_frame_time_ms': round(avg_frame_time * 1000, 2) if 'avg_frame_time' in locals() else 0,
            'avg_input_latency_ms': round(avg_latency, 2),
            'frame_count': self.frame_count,
            'thread_count': len(self.thread_stats)
        }
        
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics"""
        summary = self.get_performance_summary()
        
        summary.update({
            'recent_cpu': list(self.cpu_usage)[-10:],
            'recent_memory': list(self.memory_usage)[-10:],
            'recent_frame_times': list(self.frame_times)[-10:],
            'recent_latency': list(self.input_latency)[-10:]
        })
        
        return summary
        
    def reset_stats(self):
        """Reset all performance statistics"""
        self.cpu_usage.clear()
        self.memory_usage.clear()
        self.frame_times.clear()
        self.input_latency.clear()
        self.frame_count = 0
        self.thread_stats.clear()
        
    def export_stats(self, filename: str):
        """Export performance statistics to a file"""
        try:
            stats = self.get_detailed_stats()
            with open(filename, 'w') as f:
                import json
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"Failed to export stats: {e}")


performance_monitor = PerformanceMonitor()


def start_performance_monitoring():
    """Start global performance monitoring"""
    performance_monitor.start_monitoring()


def stop_performance_monitoring():
    """Stop global performance monitoring"""
    performance_monitor.stop_monitoring()


def get_performance_summary():
    """Get global performance summary"""
    return performance_monitor.get_performance_summary()
