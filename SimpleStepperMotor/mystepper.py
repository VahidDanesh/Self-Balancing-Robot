import machine
import math
import time

def constrain(value: float, min_val: float, max_val: float) -> float:
    """Constrain a value between min and max values."""
    return max(min_val, min(max_val, value))

def near_zero(value: float, tolerance: float = 0.0001) -> bool:
    """Check if a value is near zero within a tolerance."""
    return abs(value) < tolerance

class Stepper:
    """
    Advanced Stepper motor control class with acceleration/deceleration support.
    """
    
    def __init__(self, 
                 step_pin: machine.Pin | int,
                 dir_pin: machine.Pin | int,
                 en_pin: machine.Pin | int | None = None,
                 steps_per_rev: int = 200,
                 speed_sps: float = 100,
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
        self.steps_per_sec = speed_sps
        self.acceleration = acceleration
        
        # Position tracking
        self.current_pos = 0
        self.target_pos = 0
        
        # Speed and acceleration variables
        self.current_speed = 0.0
        self.step_interval = 0
        self.last_step_time = 0
        self._c0 = 1000000.0 / (math.sqrt(2.0 * self.acceleration))  # Initial step interval
        self._cmin = 1000000.0 / self.max_speed  # Minimum step interval
        self._cn = self._c0  # Current step interval
        self._n = 0  # Step counter
        
        # Direction and state
        self.direction = 1
        self.running = False
        self.enabled = True
        self.free_run_mode = 0
        self.free_run_speed = speed_sps
        
        # Timer management
        self._init_timer(timer_id)
        
        # Callbacks
        self.on_target_reached = None
        self.on_error = None
        
        # Enable motor if en_pin provided
        if self.en_pin:
            self.enable(True)

    def _init_timer(self, timer_id: int) -> None:
        """Initialize hardware timer with error handling."""
        try:
            self.timer = machine.Timer(timer_id)
            self.timer_is_running = False
            self.timer_id = timer_id
            # Initialize 
            self._start_timer()
        except Exception as e:
            if self.on_error:
                self.on_error(f"Timer initialization failed: {e}")
            raise RuntimeError(f"Timer initialization failed: {e}")

    def _start_timer(self) -> None:
        """Start the timer with high base frequency."""
        try:
            self.timer.deinit()
            self.timer.init(freq=self.steps_per_sec, callback=self._timer_callback)  
            self.timer_is_running = True
        except Exception as e:
            if self.on_error:
                self.on_error(f"Timer start failed: {e}")
            raise RuntimeError(f"Timer start failed: {e}")

    def _calc_step_interval(self, speed: float) -> int:
        """Calculate step interval in microseconds from speed in steps/second."""
        if speed == 0:
            return 0
        return int(1000000.0 / abs(speed))

    def _update_speed(self) -> None:
        """Update speed using step counting algorithm for smooth motion control."""
        if not self.running:
            return

        # Calculate distance to go
        steps_to_go = self.target_pos - self.current_pos
        
        # Calculate steps needed to stop
        steps_to_stop = int((self.current_speed * self.current_speed) / (2.0 * self.acceleration))
        
        # Check if we're at target and nearly stopped
        if steps_to_go == 0 and steps_to_stop <= 1:
            self.step_interval = 0
            self.current_speed = 0.0
            self._n = 0
            self.running = False
            if self.on_target_reached:
                self.on_target_reached()
            return

        # Handle free run mode
        if self.free_run_mode != 0:
            target_speed = self.free_run_speed if self.free_run_mode > 0 else -self.free_run_speed
            self.step_interval = self._calc_step_interval(target_speed)
            self.direction = self.free_run_mode
            if self._n == 0:
                self._cn = self._c0
            else:
                self._cn = self._cn - ((2.0 * self._cn) / ((4.0 * self._n) + 1))
                self._cn = max(self._cn, self._cmin)
        else:
            # Normal position control mode
            if steps_to_go > 0:
                if self._n > 0:
                    if (steps_to_stop >= steps_to_go) or self.direction < 0:
                        self._n = -steps_to_stop
                elif self._n < 0:
                    if (steps_to_stop < steps_to_go) and self.direction > 0:
                        self._n = -self._n
            elif steps_to_go < 0:
                if self._n > 0:
                    if (steps_to_stop >= -steps_to_go) or self.direction > 0:
                        self._n = -steps_to_stop
                elif self._n < 0:
                    if (steps_to_stop < -steps_to_go) and self.direction < 0:
                        self._n = -self._n

            if self._n == 0:
                self._cn = self._c0
                self.direction = 1 if steps_to_go > 0 else -1
            else:
                self._cn = self._cn - ((2.0 * self._cn) / ((4.0 * self._n) + 1))
                self._cn = max(self._cn, self._cmin)

        # Update step counter and timing
        self._n += 1
        self.step_interval = int(self._cn)
        self.current_speed = 1000000.0 / self._cn
        if self.direction < 0:
            self.current_speed = -self.current_speed

    def _timer_callback(self, t: machine.Timer) -> None:
        """Timer callback for stepping motor."""
        if not self.running or self.step_interval == 0:
            return

        current_time = time.ticks_us()
        if time.ticks_diff(current_time, self.last_step_time) >= self.step_interval:
            if self.enabled:
                self.dir_value_func(1 if self.direction > 0 else 0 ^ self.invert_dir)
                self.step_value_func(1)
                self.step_value_func(0)
            
            self.current_pos += self.direction
            self.last_step_time = current_time
            self._update_speed()

    def move_to(self, position: int) -> None:
        """Move to absolute position with acceleration."""
        self.free_run_mode = 0
        self.target_pos = position
        self.running = True
        self._n = 0  # Reset step counter
        self.last_step_time = time.ticks_us()
        self._update_speed()

    def move(self, steps: int) -> None:
        """Move relative number of steps with acceleration."""
        self.move_to(self.current_pos + steps)

    def free_run(self, direction: int, speed: float = None) -> None:
        """Run the stepper continuously in specified direction."""
        if direction not in [-1, 0, 1]:
            raise ValueError("Direction must be -1, 0, or 1")
        
        if direction == 0:
            self.stop()
            return
        
        # Set free run parameters
        self.free_run_mode = direction
        self.free_run_speed = speed if speed is not None else self.max_speed
        self.free_run_speed = min(self.free_run_speed, self.max_speed)
        
        # Reset acceleration parameters
        self._n = 0
        self._cn = self._c0
        self.direction = direction
        
        # Set initial speed to a small value to start movement
        self.current_speed = direction * (self.max_speed / 100)  # Start at 1% of max speed
        self.step_interval = self._calc_step_interval(abs(self.current_speed))
        
        # Enable running state
        self.running = True
        self.last_step_time = time.ticks_us()
        
        # Force an immediate speed update
        self._update_speed()

    def stop(self) -> None:
        """Stop motor with deceleration."""
        self.free_run_mode = 0
        self.target_pos = self.current_pos
        self._n = -int((self.current_speed * self.current_speed) / (2.0 * self.acceleration))
        self._update_speed()



    def move_to_deg(self, degrees: float) -> None:
        """Move to absolute position in degrees with acceleration."""
        self.move_to(int(degrees * self.steps_per_rev / 360)) # Convert degrees to steps
    
    def move_to_rad(self, radians: float) -> None:
        """Move to absolute position in radians with acceleration."""
        self.move_to(int(radians * self.steps_per_rev / (2.0 * math.pi)))
    

    def stop(self) -> None:
        """Stop motor with deceleration."""
        self.free_run_mode = 0
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


    def set_position(self, position: int) -> None:
        """Set current position in steps."""
        self.current_pos = position
    


    def set_max_speed(self, speed: float) -> None:
        """Set maximum speed in steps per second."""
        if speed < 0.0:
            speed = -speed
        if self.max_speed != speed:
            self.max_speed = speed
            self._cmin = 1000000.0 / self.max_speed
            if self.n>0:
                self.n = int((self.current_speed * self.current_speed) / (2.0 * self.acceleration))
                self.step_interval = self._calc_step_interval(self.current_speed)
                self._update_speed()
        

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

    def is_enabled(self) -> bool:
        """Check if the stepper motor is enabled."""
        return self.enabled

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
    

    def sps2rpm(self, speed_sps: float) -> float:
        """Convert speed in steps per second to RPM."""
        return speed_sps * 60 / self.steps_per_rev
    
    def rpm2sps(self, speed_rpm: float) -> float:
        """Convert speed in RPM to steps per second."""
        return speed_rpm * self.steps_per_rev / 60
    
    def rps2sps(self, speed_rps: float) -> float:
        """Convert speed in revolutions per second to steps per second."""
        return speed_rps * self.steps_per_rev
