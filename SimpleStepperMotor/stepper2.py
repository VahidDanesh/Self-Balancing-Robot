from typing import Optional, Union, Callable
import machine
import math
import time

class Stepper:
    """
    Advanced Stepper motor control class with acceleration/deceleration support.
    
    Args:
        step_pin (Union[machine.Pin, int]): The step pin number or Pin object
        dir_pin (Union[machine.Pin, int]): The direction pin number or Pin object
        en_pin (Optional[Union[machine.Pin, int]]): Enable pin (optional)
        steps_per_rev (int): Steps per revolution (default: 200)
        max_speed_sps (float): Maximum speed in steps per second
        acceleration (float): Acceleration in steps per second squared
        invert_dir (bool): Invert direction logic
        timer_id (int): Hardware timer ID (must be unique per stepper)
        en_active_low (bool): Enable pin active low logic
    """
    
    def __init__(self, 
                 step_pin: Union[machine.Pin, int],
                 dir_pin: Union[machine.Pin, int],
                 en_pin: Optional[Union[machine.Pin, int]] = None,
                 steps_per_rev: int = 200,
                 max_speed_sps: float = 1000,
                 acceleration: float = 1000,
                 invert_dir: bool = False,
                 timer_id: int = -1,
                 en_active_low: bool = True):
        
        # Initialize pins
        if not isinstance(step_pin, machine.Pin):
            step_pin = machine.Pin(step_pin, machine.Pin.OUT)
        if not isinstance(dir_pin, machine.Pin):
            dir_pin = machine.Pin(dir_pin, machine.Pin.OUT)
        if (en_pin is not None) and (not isinstance(en_pin, machine.Pin)):
            en_pin = machine.Pin(en_pin, machine.Pin.OUT)

        self.step_value_func = step_pin.value
        self.dir_value_func = dir_pin.value
        self.en_pin = en_pin
        self.invert_dir = invert_dir
        self.en_active_low = en_active_low

        # Motor parameters
        self.steps_per_rev = steps_per_rev
        self.max_speed = max_speed_sps
        self.acceleration = acceleration  # steps/second^2
        
        # Position tracking
        self.current_pos = 0
        self.target_pos = 0
        
        # Speed and acceleration variables
        self.current_speed = 0.0  # steps/second
        self.step_interval = 0  # microseconds
        self.last_step_time = 0
        self.min_step_interval = self._calc_step_interval(max_speed_sps)
        
        # Direction and state
        self.direction = 1
        self.running = False
        self.enabled = True
        
        # Timer management
        self._init_timer(timer_id)
        
        # Callbacks
        self.on_target_reached: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    def _init_timer(self, timer_id: int) -> None:
        """Initialize hardware timer with error handling."""
        try:
            self.timer = machine.Timer(timer_id)
            self.timer_is_running = False
            self.timer_id = timer_id
        except Exception as e:
            if self.on_error:
                self.on_error(f"Timer initialization failed: {e}")
            raise RuntimeError(f"Timer initialization failed: {e}")

    def _calc_step_interval(self, speed: float) -> int:
        """Calculate step interval in microseconds from speed in steps/second."""
        if speed == 0:
            return 0
        return int(1000000 / abs(speed))

    def _update_speed(self) -> None:
        """Update current speed based on acceleration and target position."""
        if not self.running:
            return

        current_time = time.ticks_us()
        time_since_last_step = time.ticks_diff(current_time, self.last_step_time)
        
        # Calculate required speed to reach target
        steps_to_go = abs(self.target_pos - self.current_pos)
        if steps_to_go == 0:
            target_speed = 0
        else:
            # Calculate direction
            self.direction = 1 if self.target_pos > self.current_pos else -1
            
            # Calculate stopping distance at current speed
            stopping_steps = (self.current_speed * self.current_speed) / (2.0 * self.acceleration)
            
            if steps_to_go <= stopping_steps:
                # Need to start decelerating
                target_speed = math.sqrt(2.0 * self.acceleration * steps_to_go)
            else:
                # Can accelerate or maintain speed
                target_speed = self.max_speed

        # Apply acceleration limits
        if self.current_speed < target_speed:
            # Accelerating
            new_speed = self.current_speed + self.acceleration * time_since_last_step / 1000000.0
            self.current_speed = min(new_speed, target_speed, self.max_speed)
        elif self.current_speed > target_speed:
            # Decelerating
            new_speed = self.current_speed - self.acceleration * time_since_last_step / 1000000.0
            self.current_speed = max(new_speed, target_speed, 0)

        # Update step interval
        if self.current_speed > 0:
            self.step_interval = self._calc_step_interval(self.current_speed)
        else:
            self.step_interval = 0
            self.running = False
            if self.on_target_reached:
                self.on_target_reached()

    def _timer_callback(self, t: machine.Timer) -> None:
        """Timer callback for stepping motor."""
        current_time = time.ticks_us()
        
        if not self.running or self.step_interval == 0:
            return

        if time.ticks_diff(current_time, self.last_step_time) >= self.step_interval:
            # Make a step
            if self.enabled:
                self.dir_value_func(1 if self.direction > 0 else 0 ^ self.invert_dir)
                self.step_value_func(1)
                self.step_value_func(0)
            
            self.current_pos += self.direction
            self.last_step_time = current_time
            
            # Update speed for next step
            self._update_speed()

    def move_to(self, position: int) -> None:
        """Move to absolute position with acceleration."""
        self.target_pos = position
        self.running = True
        if not self.timer_is_running:
            self._start_timer()

    def move_to_deg(self, degrees: float) -> None:
        """Move to absolute position in degrees with acceleration."""
        self.move_to(int(degrees * self.steps_per_rev / 360)) # Convert degrees to steps
    
    def move_to_rad(self, radians: float) -> None:
        """Move to absolute position in radians with acceleration."""
        self.move_to(int(radians * self.steps_per_rev / (2.0 * math.pi)))
    


    def move(self, steps: int) -> None:
        """Move relative number of steps with acceleration."""
        self.move_to(self.current_pos + steps)

    def stop(self) -> None:
        """Stop motor with deceleration."""
        self.target_pos = self.current_pos
        if self.timer_is_running:
            self.timer.deinit()
            self.timer_is_running = False
        self.running = False
        self.current_speed = 0

    def emergency_stop(self) -> None:
        """Immediately stop motor without deceleration."""
        self.stop()
        self.enable(False)
        if self.on_error:
            self.on_error("Emergency stop triggered")

    def _start_timer(self) -> None:
        """Start the timer with current parameters."""
        try:
            self.timer.deinit()
            # Use a high frequency base timer and handle timing in the callback
            self.timer.init(freq=10000, callback=self._timer_callback)
            self.timer_is_running = True
        except Exception as e:
            if self.on_error:
                self.on_error(f"Timer start failed: {e}")
            raise RuntimeError(f"Timer start failed: {e}")

    def set_max_speed(self, speed: float) -> None:
        """Set maximum speed in steps per second."""
        if speed < 0:
            raise ValueError("Speed cannot be negative")
        self.max_speed = speed
        self.min_step_interval = self._calc_step_interval(speed)

    def set_acceleration(self, acceleration: float) -> None:
        """Set acceleration in steps per second squared."""
        if acceleration <= 0:
            raise ValueError("Acceleration must be positive")
        self.acceleration = acceleration

    def enable(self, state: bool) -> None:
        """Enable or disable the stepper motor."""
        if self.en_pin:
            self.en_pin.value(not state if self.en_active_low else state)
        self.enabled = state
        if not state:
            self.dir_value_func(0)

    def is_running(self) -> bool:
        """Return True if motor is currently moving."""
        return self.running

    def get_position(self) -> int:
        """Get current position in steps."""
        return self.current_pos

    def get_speed(self) -> float:
        """Get current speed in steps per second."""
        return self.current_speed
    
    def get_max_speed(self) -> float:
        """Get maximum speed in steps per second."""
        return self.max_speed
    
    def get_acceleration(self) -> float:
        """Get acceleration in steps per second squared."""
        return self.acceleration
    
    def get_position_deg(self) -> float:
        """Get current position in degrees."""
        return self.current_pos * 360 / self.steps_per_rev
    
    def get_position_rad(self) -> float:
        """Get current position in radians."""
        return self.current_pos * 2 * math.pi / self.steps_per_rev
    
    