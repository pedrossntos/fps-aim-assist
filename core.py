from config import Config
import threading
import time
from pynput import mouse
import vgamepad as vg
from collections import deque
import math


class Core:
    
    def __init__(self, config: Config, gui_callback=None):
        self.config = config
        self.gui_callback = gui_callback
        
        self.MAX = 32767
        self.MIN = -32768
        self.CENTER = 0
        
        self.mouse_lock = threading.Lock()
        self.gamepad_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        self.deadzone_squared = self.config.deadzone ** 2
        self.recoil_strength = self.config.recoil_strength
        self.max_recoil_offset = self.config.max_recoil_offset
        
        self.movement_history = deque(maxlen=3)
        
        self.last_sent_x = self.CENTER
        self.last_sent_y = self.CENTER
        self.last_x = 0
        self.last_y = 0
        self.last_move_time = time.time()
        
        self.monotonic_time = time.monotonic
        
        self.running = True
        self.enabled = False
        self.recoil_enabled = config.recoil_enabled
        self.recoil_active = False
        self.recoil_offset_y = 0
        self.is_moving = False
        
        self.stats_pending = {
            'total_movements': 0,
            'total_clicks': 0,
            'recoil_activations': 0
        }
        self.stats = {
            'total_movements': 0,
            'total_clicks': 0,
            'recoil_activations': 0,
            'start_time': time.time()
        }
        
        self.gamepad = None
        self.mouse_controller = mouse.Controller()
        self._initialize_gamepad()
        
        self.mouse_listener = None
        self.keyboard_listener = None
        
        self._last_update_time = 0
        self._update_threshold = 0.001  # 1ms minimum between updates
        
    def _initialize_gamepad(self):
        try:
            self.gamepad = vg.VX360Gamepad()
            return True
        except Exception as e:
            if self.gui_callback:
                self.gui_callback("error", f"error starting gamepad: {e}")
            return False
    
    def clamp(self, val: float, min_val: int, max_val: int) -> int:
        return max(min_val, min(max_val, math.floor(val)))
    
    def update_gamepad_stick(self, stick_x: int, stick_y: int):
        if not self.gamepad:
            return
        
        if (stick_x == self.last_sent_x and stick_y == self.last_sent_y):
            return
            
        stick_x = self.clamp(stick_x, self.MIN, self.MAX)
        stick_y = self.clamp(stick_y, self.MIN, self.MAX)
        
        with self.gamepad_lock:
            self.gamepad.right_joystick(x_value=stick_x, y_value=stick_y)
            self.gamepad.update()
        
        self.last_sent_x = stick_x
        self.last_sent_y = stick_y
    
    def on_move(self, x: int, y: int):
        if not self.enabled or not self.gamepad:
            return
        
        current_time = self.monotonic_time()
        if current_time - self._last_update_time < self._update_threshold:
            return
        self._last_update_time = current_time
        
        with self.mouse_lock:
            dx = x - self.last_x
            dy = y - self.last_y
            self.last_x = x
            self.last_y = y
            self.last_move_time = current_time
            
            if dx * dx + dy * dy < self.deadzone_squared:
                return
            
            self.stats_pending['total_movements'] += 1
            self.is_moving = True
            
            sens = self.config.sens
            raw_x = dx * sens
            raw_y = -dy * sens
            
            if self.recoil_active and self.recoil_enabled:
                raw_y += self.recoil_offset_y
            
            stick_x = self.CENTER if abs(raw_x) <= self.config.deadzone else self.clamp(raw_x, self.MIN, self.MAX)
            stick_y = self.CENTER if abs(raw_y) <= self.config.deadzone else self.clamp(raw_y, self.MIN, self.MAX)
            
            self.update_gamepad_stick(stick_x, stick_y)
    
    def on_click(self, x: int, y: int, button, pressed: bool):
        if button == mouse.Button.left and self.recoil_enabled and self.enabled:
            if pressed:
                self.stats_pending['total_clicks'] += 1
            self.recoil_active = pressed
            if pressed:
                self.stats_pending['recoil_activations'] += 1
    
    def _update_stats(self):
        """Batch update stats to reduce lock contention"""
        if any(self.stats_pending.values()):
            with self.stats_lock:
                for key, value in self.stats_pending.items():
                    self.stats[key] += value
                    self.stats_pending[key] = 0
    
    def reset_stick_loop(self):
        sleep_time = 0.005  
        
        while self.running:
            time.sleep(sleep_time)
            
            self._update_stats()
            
            if not self.enabled:
                with self.mouse_lock:
                    if self.last_sent_x != self.CENTER or self.last_sent_y != self.CENTER:
                        if self.gamepad:
                            with self.gamepad_lock:
                                self.gamepad.right_joystick(x_value=self.CENTER, y_value=self.CENTER)
                                self.gamepad.update()
                        self.last_sent_x = self.CENTER
                        self.last_sent_y = self.CENTER
                        self.is_moving = False
                continue
            
            with self.mouse_lock:
                time_since_move = self.monotonic_time() - self.last_move_time
                
                if time_since_move > self.config.reset_delay and self.is_moving:
                    if self.gamepad:
                        with self.gamepad_lock:
                            self.gamepad.right_joystick(x_value=self.CENTER, y_value=self.CENTER)
                            self.gamepad.update()
                    self.last_sent_x = self.CENTER
                    self.last_sent_y = self.CENTER
                    self.is_moving = False
    
    def recoil_loop(self):
        recoil_rate = self.config.recoil_rate
        recoil_recovery_rate = self.config.recoil_recovery_rate
        recoil_strength = self.recoil_strength
        max_recoil_offset = self.max_recoil_offset
        
        while self.running:
            if self.recoil_active and self.enabled and self.recoil_enabled:
                with self.mouse_lock:
                    target_offset = max(
                        self.recoil_offset_y - recoil_strength,
                        -max_recoil_offset
                    )
                    self.recoil_offset_y = int(self.recoil_offset_y + (target_offset - self.recoil_offset_y) * 0.6)
                time.sleep(recoil_rate)
            else:
                with self.mouse_lock:
                    if abs(self.recoil_offset_y) > 1000:
                        recovery_speed = 0.4
                    else:
                        recovery_speed = 0.6
                    
                    self.recoil_offset_y = int(self.recoil_offset_y + (0 - self.recoil_offset_y) * recovery_speed)
                    
                    if abs(self.recoil_offset_y) < 10:
                        self.recoil_offset_y = 0
                time.sleep(recoil_recovery_rate)
    
    def start(self):
        if not self.gamepad:
            return False
            
        try:
            self.last_x, self.last_y = self.mouse_controller.position
            self.last_move_time = self.monotonic_time()
        except:
            return False
        
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.mouse_listener.start()
        
        reset_thread = threading.Thread(target=self.reset_stick_loop, daemon=True, name="ResetThread")
        recoil_thread = threading.Thread(target=self.recoil_loop, daemon=True, name="RecoilThread")
        
        reset_thread.start()
        recoil_thread.start()
        
        return True
    
    def stop(self):
        self.running = False
        self.enabled = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        if self.gamepad:
            with self.gamepad_lock:
                self.gamepad.right_joystick(x_value=self.CENTER, y_value=self.CENTER)
                self.gamepad.update()
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled and self.gamepad:
            with self.mouse_lock:
                with self.gamepad_lock:
                    self.gamepad.right_joystick(x_value=self.CENTER, y_value=self.CENTER)
                    self.gamepad.update()
                self.last_sent_x = self.CENTER
                self.last_sent_y = self.CENTER
                self.recoil_offset_y = 0
                self.recoil_active = False
                self.is_moving = False
