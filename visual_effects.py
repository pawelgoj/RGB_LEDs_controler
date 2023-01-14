import utime
import machine
from functions import change_specific_color
from button import ButtonChangeColor


class VisualEffects: 
    time: int|None = None
    interval: int = 1000
    time_interval: int = 1000
    current_effect: str = 'breath_effect'
    constant: int = 65535
    
    def __init__(self, list_led_b: list[machine.PWM], 
                 list_led_g: list[machine.PWM], 
                 list_led_r: list[machine.PWM], temp_colors: list[int]) -> None: 
        
        self.list_led_b = list_led_b
        self.list_led_g = list_led_g
        self.list_led_r = list_led_r
        self.temp_colors = temp_colors
        
    def breath_effect(self, list_led_b: list, list_led_g: list, list_led_r: list, temp_colors: list) -> None:
 
        if self.time == None:
            self.time = utime.ticks_ms()
        elif utime.ticks_diff(utime.ticks_ms(), self.time) < self.time_interval:
            change_specific_color(list_led_b, 0)
            change_specific_color(list_led_g, 0)
            change_specific_color(list_led_r, 0)
        elif  (t := utime.ticks_diff(utime.ticks_ms(), self.time)) < 2 * self.time_interval: 
            change_specific_color(list_led_b, int(temp_colors[0] * ((t - self.time_interval) /self.time_interval)))
            change_specific_color(list_led_g, int(temp_colors[1] * ((t - self.time_interval) /self.time_interval)))
            change_specific_color(list_led_r, int(temp_colors[2] * ((t - self.time_interval) /self.time_interval)))
        elif  utime.ticks_diff(utime.ticks_ms(), self.time) < 3 * self.time_interval:
            change_specific_color(list_led_b, temp_colors[0])
            change_specific_color(list_led_g, temp_colors[1])
            change_specific_color(list_led_r, temp_colors[2])
        elif  (t := utime.ticks_diff(utime.ticks_ms(), self.time)) < 4 * self.time_interval:
            change_specific_color(list_led_b, int(temp_colors[0] 
                                                  * (self.time_interval - (t - 3 * self.time_interval)) /self.time_interval))
            change_specific_color(list_led_g, int(temp_colors[1] 
                                                  * (self.time_interval - (t - 3 * self.time_interval)) /self.time_interval))
            change_specific_color(list_led_r, int(temp_colors[2] 
                                                  * (self.time_interval - (t - 3 * self.time_interval)) /self.time_interval))
        else:
            self.time = None
            
    def color_change(self, list_led_b: list, list_led_g: list, list_led_r: list) -> None:
        if self.time == None:
            self.time = utime.ticks_ms()
        elif utime.ticks_diff(utime.ticks_ms(), self.time) < self.time_interval:
            change_specific_color(list_led_b, 0)
            change_specific_color(list_led_g, 0)
            change_specific_color(list_led_r, self.constant)
        elif  (t := utime.ticks_diff(utime.ticks_ms(), self.time)) < 2 * self.time_interval: 
            change_specific_color(list_led_b, 0)
            change_specific_color(list_led_g, int(self.constant * ((t - self.time_interval) /self.time_interval)))
            change_specific_color(list_led_r, int(self.constant * (self.time_interval - (t -  self.time_interval)) /self.time_interval))
        elif  utime.ticks_diff(utime.ticks_ms(), self.time) < 3 * self.time_interval:
            change_specific_color(list_led_b, 0)
            change_specific_color(list_led_g, self.constant)
            change_specific_color(list_led_r, 0)
        elif  (t := utime.ticks_diff(utime.ticks_ms(), self.time)) < 4 * self.time_interval:
            change_specific_color(list_led_b, int(self.constant * ((t - 3 * self.time_interval) /self.time_interval)))
            change_specific_color(list_led_g, int(self.constant 
                                                  * (self.time_interval - (t - 3 * self.time_interval)) /self.time_interval))
            change_specific_color(list_led_r, 0)
            
        elif  (t := utime.ticks_diff(utime.ticks_ms(), self.time)) < 5 * self.time_interval:
            change_specific_color(list_led_b, self.constant)
            change_specific_color(list_led_g, 0)
            change_specific_color(list_led_r, 0)
        elif  (t := utime.ticks_diff(utime.ticks_ms(), self.time)) < 6 * self.time_interval:
            change_specific_color(list_led_b, int(self.constant 
                                                  * (self.time_interval - (t - 5 * self.time_interval)) /self.time_interval))
            change_specific_color(list_led_g, 0)
            change_specific_color(list_led_r, int(self.constant * ((t - 5 * self.time_interval) /self.time_interval)))
        else:
            self.time = None
    
    def effect_loop(self, potentiometer: machine.ADC, state_of_button_change_color: ButtonChangeColor, list_led_b: list, list_led_g: list, list_led_r: list, temp_colors: list) -> None: 
        
        
        while True:
            
            if state_of_button_change_color.state in ('save', 'loaded'):
                break
            elif state_of_button_change_color.state is 'change':
                self.time = None
                state_of_button_change_color.state = 'visual_effects'
                self.current_effect = 'breath_effect' if self.current_effect is 'color_change' else 'color_change'
                
            if self.current_effect == 'breath_effect': 
                self.time_interval = int((((potentiometer.read_u16() / self.constant) * self.interval) /2)) + 100
                self.breath_effect(list_led_b, list_led_g, list_led_r, temp_colors)
            elif self.current_effect == 'color_change':
                self.time_interval = int((((potentiometer.read_u16() / self.constant) * self.interval) /2)) + 100
                self.color_change(list_led_b, list_led_g, list_led_r)
            else: 
                print("No implement effect!!!!!")