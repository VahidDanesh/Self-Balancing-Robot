import machine
import math
import time

class Stepper:
  def __init__(self, step_pin, dir_pin, en_pin=None, steps_per_rev=200, speed_sps=10, invert_dir=False, timer_id=-1, en_active_low=True, accel_time=1.0):
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

      self.timer = machine.Timer(timer_id)
      self.timer_is_running = False
      self.free_run_mode = 0
      self.enabled = True

      self.target_pos = 0
      self.pos = 0
      self.steps_per_sec = speed_sps
      self.steps_per_rev = steps_per_rev
      self.accel_time = accel_time  # Time to reach full speed

      self.start_time = None
      self.current_speed = 0

      self.track_target()

  def cubic_time_scaling(self, t, T):
      # Cubic time scaling function
      s = 3 * (t / T) ** 2 - 2 * (t / T) ** 3
      v = 6 * (t / T) * (1 - t / T) / T
      a = 6 * (1 - 2 * t / T) / (T ** 2)
      return s, v, a

  def speed(self, sps):
      self.steps_per_sec = sps
      if self.timer_is_running:
          self.track_target()

  def speed_rps(self, rps):
      self.speed(rps * self.steps_per_rev)

  def target(self, t):
      self.target_pos = t

  def target_deg(self, deg):
      self.target(self.steps_per_rev * deg / 360.0)

  def target_rad(self, rad):
      self.target(self.steps_per_rev * rad / (2.0 * math.pi))

  def get_pos(self):
      return self.pos
  
  def get_speed(self):
      return self.current_speed

  def get_pos_deg(self):
      return self.get_pos() * 360.0 / self.steps_per_rev

  def get_pos_rad(self):
      return self.get_pos() * (2.0 * math.pi) / self.steps_per_rev

  def overwrite_pos(self, p):
      self.pos = 0

  def overwrite_pos_deg(self, deg):
      self.overwrite_pos(deg * self.steps_per_rev / 360.0)

  def overwrite_pos_rad(self, rad):
      self.overwrite_pos(rad * self.steps_per_rev / (2.0 * math.pi))

  def step(self, d):
      if d > 0:
          if self.enabled:
              self.dir_value_func(1 ^ self.invert_dir)
              self.step_value_func(1)
              self.step_value_func(0)
          self.pos += 1
      elif d < 0:
          if self.enabled:
              self.dir_value_func(0 ^ self.invert_dir)
              self.step_value_func(1)
              self.step_value_func(0)
          self.pos -= 1

  def _timer_callback(self, t):
      current_time = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0
      if current_time < self.accel_time:
          s, v, a = self.cubic_time_scaling(current_time, self.accel_time)
          self.current_speed = self.steps_per_sec * v
      else:
          self.current_speed = self.steps_per_sec

      if self.free_run_mode > 0:
          self.step(1)
      elif self.free_run_mode < 0:
          self.step(-1)
      elif self.target_pos > self.pos:
          self.step(1)
      elif self.target_pos < self.pos:
          self.step(-1)

      # Update the timer frequency based on the current speed
      if self.current_speed > 0:
          self.timer.init(freq=self.current_speed, callback=self._timer_callback)

  def free_run(self, d):
      self.free_run_mode = d
      if self.timer_is_running:
          self.timer.deinit()
      if d != 0:
          self.start_time = time.ticks_ms()
          self.timer.init(freq=self.steps_per_sec, callback=self._timer_callback)
          self.timer_is_running = True
      else:
          self.dir_value_func(0)

  def track_target(self):
      self.free_run_mode = 0
      if self.timer_is_running:
          self.timer.deinit()
      self.start_time = time.ticks_ms()
      self.timer.init(freq=self.steps_per_sec, callback=self._timer_callback)
      self.timer_is_running = True

  def stop(self):
      self.free_run_mode = 0
      if self.timer_is_running:
          self.timer.deinit()
      self.timer_is_running = False
      self.dir_value_func(0)

  def enable(self, e):
      if self.en_pin:
          # Adjust the enable logic based on whether the enable pin is active low
          self.en_pin.value(not e if self.en_active_low else e)
      self.enabled = e
      if not e:
          self.dir_value_func(0)

  def is_enabled(self):
      return self.enabled