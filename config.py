from dataclasses import dataclass


@dataclass
class Config:
    sens: float = 8000.0
    deadzone: int = 3
    reset_delay: float = 0.01
    recoil_strength: int = 600
    recoil_rate: float = 0.004
    recoil_recovery_rate: float = 0.004
    recoil_enabled: bool = True
    use_integer_math: bool = False
    enable_smoothing: bool = True
    max_recoil_offset: int = 6000
    direct_response_mode: bool = True