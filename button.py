import machine
import utime

class Button:
    _oscillation_time: int = 15
    _time_recent_action: int
    _pressed = False
    
    def __init__(self, machine_pin_with_button: machine.Pin):
        
        self.machine_pin_with_button = machine_pin_with_button
        self._time_recent_action = utime.ticks_ms()
        
    @property
    def pressed(self):

        if utime.ticks_diff(utime.ticks_ms(), self._time_recent_action) > self._oscillation_time:
            self._pressed = False if self.machine_pin_with_button.value() == 0 else True
            self._time_recent_action = utime.ticks_ms()
            
        return self._pressed
    
class ButtonChangeColor:
    state: str
    
    def __init__(self, state: str):
        self.state = state 