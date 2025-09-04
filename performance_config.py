from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PerformanceProfile:
    """Performance profile configuration"""
    name: str
    description: str
    
    reset_loop_sleep_ms: float
    recoil_loop_sleep_ms: float
    
    mouse_update_threshold_ms: float
    gamepad_update_threshold_ms: float
    
    stats_batch_size: int
    stats_update_interval_ms: float
    
    max_movement_history: int
    max_stats_samples: int
    
    enable_smoothing: bool
    enable_prediction: bool
    use_integer_math: bool


PERFORMANCE_PROFILES = {
    'ultra_low_latency': PerformanceProfile(
        name="Ultra Low Latency",
        description="Maximum responsiveness, higher CPU usage",
        reset_loop_sleep_ms=0.001,  # 1ms
        recoil_loop_sleep_ms=0.004,  # 4ms
        mouse_update_threshold_ms=0.001,  # 1ms
        gamepad_update_threshold_ms=0.001,  # 1ms
        stats_batch_size=1,
        stats_update_interval_ms=1.0,
        max_movement_history=5,
        max_stats_samples=50,
        enable_smoothing=True,
        enable_prediction=True,
        use_integer_math=False
    ),
    
    'balanced': PerformanceProfile(
        name="Balanced",
        description="Good balance of performance and resource usage",
        reset_loop_sleep_ms=0.005,  # 5ms
        recoil_loop_sleep_ms=0.008,  # 8ms
        mouse_update_threshold_ms=0.002,  # 2ms
        gamepad_update_threshold_ms=0.002,  # 2ms
        stats_batch_size=5,
        stats_update_interval_ms=5.0,
        max_movement_history=3,
        max_stats_samples=100,
        enable_smoothing=True,
        enable_prediction=False,
        use_integer_math=True
    ),
    
    'power_saver': PerformanceProfile(
        name="Power Saver",
        description="Lower CPU usage, slightly higher latency",
        reset_loop_sleep_ms=0.010,  # 10ms
        recoil_loop_sleep_ms=0.016,  # 16ms
        mouse_update_threshold_ms=0.005,  # 5ms
        gamepad_update_threshold_ms=0.005,  # 5ms
        stats_batch_size=10,
        stats_update_interval_ms=10.0,
        max_movement_history=2,
        max_stats_samples=200,
        enable_smoothing=False,
        enable_prediction=False,
        use_integer_math=True
    )
}


def get_performance_profile(profile_name: str = 'balanced') -> PerformanceProfile:
    """Get a performance profile by name"""
    return PERFORMANCE_PROFILES.get(profile_name, PERFORMANCE_PROFILES['balanced'])


def get_available_profiles() -> Dict[str, str]:
    """Get available performance profile names and descriptions"""
    return {name: profile.description for name, profile in PERFORMANCE_PROFILES.items()}


def apply_performance_profile(core_instance, profile: PerformanceProfile):
    """Apply performance profile settings to a core instance"""
    if not hasattr(core_instance, '_performance_profile'):
        core_instance._performance_profile = profile
    
    core_instance._update_threshold = profile.mouse_update_threshold_ms / 1000.0
    
    if hasattr(core_instance, 'movement_history'):
        core_instance.movement_history = core_instance.movement_history.__class__(
            maxlen=profile.max_movement_history
        )
    
    if hasattr(core_instance, 'stats_pending'):
        core_instance._stats_batch_size = profile.stats_batch_size
        core_instance._stats_update_interval = profile.stats_update_interval_ms / 1000.0


def optimize_for_gaming():
    """Get optimal settings for gaming scenarios"""
    return get_performance_profile('ultra_low_latency')


def optimize_for_battery():
    """Get optimal settings for battery life"""
    return get_performance_profile('power_saver')


def get_system_recommendation():
    """Get performance profile recommendation based on system capabilities"""
    import psutil
    
    try:
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        if cpu_count >= 8 and memory_gb >= 16:
            return 'ultra_low_latency'
        elif cpu_count >= 4 and memory_gb >= 8:
            return 'balanced'
        else:
            return 'power_saver'
    except:
        return 'balanced'
