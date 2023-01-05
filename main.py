import machine
import utime
import _thread
import os

global button_change_color
button_change_color: machine.Pin = machine.Pin(16, machine.Pin.IN,
                                               machine.Pin.PULL_DOWN)


global state_of_button_change_color
state_of_button_change_color: str = 'b'

global button_on_off_pressed
button_on_off_pressed: bool = False 


class VisualEffects: 
    time: int|None = None
    time_interval: int = 1000
    
    def __init__(self, list_led_b: list[machine.PWM], 
                 list_led_g: list[machine.PWM], 
                 list_led_r: list[machine.PWM], temp_colors: list[int]) -> None: 
        
        self.list_led_b = list_led_b
        self.list_led_g = list_led_g
        self.list_led_r = list_led_r
        self.temp_colors = temp_colors
        
    def breath_effect(self) -> None:

        time = utime.ticks_ms() 
        if time == None:
            self.time = utime.ticks_ms()
        elif utime.ticks_diff(self.time_interval, time) > 0:
            change_specific_color(list_led_b, 0)
            change_specific_color(list_led_g, 0)
            change_specific_color(list_led_r, 0)
        elif  t := utime.ticks_diff(2 * self.time_interval, time) > 0: 
            change_specific_color(list_led_b, (temp_colors[0] / t))
            change_specific_color(list_led_g, (temp_colors[1] / t))
            change_specific_color(list_led_r, (temp_colors[2] / t))
        elif  utime.ticks_diff(3 * self.time_interval, time) > 0:
            change_specific_color(list_led_b, temp_colors[0])
            change_specific_color(list_led_g, temp_colors[1])
            change_specific_color(list_led_r, temp_colors[2])
        elif  t := utime.ticks_diff(4 * self.time_interval, time) > 0:
            change_specific_color(list_led_b, (temp_colors[0] / self.time_interval) * t)
            change_specific_color(list_led_b, (temp_colors[1] / self.time_interval) * t)
            change_specific_color(list_led_b, (temp_colors[2] / self.time_interval) * t)
        elif  utime.ticks_diff(5 * self.time_interval, time) <= 0:
            self.time = utime.ticks_ms()
    
    def effect_loop(self) -> None: 
        

        
def load_saved_colors_form_file() -> tuple[dict, bool]:
    """Loads saved colors from file data.txt, if file does not exist returns: 
        colors = {'b': 0, 'g': 0, 'r': 0} and first_run = True. 

    Returns:
        tuple[dict, bool]: ({'b': 0, 'g': 0, 'r': 0}, first_run)
    """
    
    colors = {'b': 0, 'g': 0, 'r': 0}
    first_run = True
    
    for item in os.listdir():
        if 'data.txt' == f'{item}':
            with open('data.txt', 'r') as file:
                string_data = file.read()
                splitted = string_data.split(' ')
                
                colors['b'] = int(splitted[0])
                colors['g'] = int(splitted[1])
                colors['r'] = int(splitted[2])
                
                del string_data
                first_run = False
    
    return colors, first_run


def button_change_color_fn(recent: int|None, state_of_button_change_color: str, 
                        time: int, after_saved: bool) \
                        -> tuple[int|None, str, int, bool]:
    """Function specifying the state of the color change button

    Args:
        recent (int): the binary state of the button (pressed down: 1, release: 0) during 
        an earlier iteration 
        state_of_button_change_color (str): colors 'r', 'g', 'b' or 'save', 'loaded'
        time (int): time.ticks_ms()
        after_saved (bool): Was the previous state_of_button_change_color 'save'? True/False

    Returns:
        tuple(recent, state_of_button_change_color, iteration, after_saved)
    """
    
    if button_change_color.value() == 0:
        time = utime.ticks_ms()
        
    if (button_change_color.value() == 0 and after_saved):
        after_saved = False
        state_of_button_change_color = 'loaded'
        
    elif (button_change_color.value() == 0 and recent != button_change_color.value()
        and utime.ticks_diff(3000, time) > 0): 
        if state_of_button_change_color == 'b':
            state_of_button_change_color = 'g'
        elif state_of_button_change_color == 'g':
            state_of_button_change_color = 'r'
        elif state_of_button_change_color == 'r':
            state_of_button_change_color = 'b'
        elif state_of_button_change_color == 'save':
            state_of_button_change_color = 'loaded'
        elif state_of_button_change_color == 'loaded' or state_of_button_change_color == 'visual_effects':
            state_of_button_change_color = 'b'
            
    elif utime.ticks_diff(3000, time) <= 0 and utime.ticks_diff(5000, time) > 0 \
        and button_change_color.value() == 0 \
        and recent != button_change_color.value():
        state_of_button_change_color = 'save'
        after_saved = True
        
    elif utime.ticks_diff(5000, time) <= 0:
        state_of_button_change_color = 'visual_effects'
    
    recent = button_change_color.value() 
    
    return recent, state_of_button_change_color, time, after_saved

def button_on_off_thread() -> None:
    """The thread for handling button events
    """
    
    global state_of_button_change_color
    
    recent_rgb =  0
    time = utime.ticks_ms()
    after_saved = False
    
    while True:
        recent_rgb, state_of_button_change_color , time, after_saved =\
            button_change_color_fn(recent_rgb, state_of_button_change_color, 
                                   time, after_saved)
        

    
def change_specific_color(list_of_pins: list[machine.PWM], result: int) -> None:
    for item in list_of_pins:
        item.duty_u16(result)

def prepare_pins(red_led_pins: list[int], green_led_pins: list[int], 
                 blue_led_pins: list[int]) -> tuple[list[machine.PWM], 
                                                    list[machine.PWM], 
                                                    list[machine.PWM]]:
    """Function return the tuple of lists of machine.PWM for pins for leds

    Args:
        red_led_pins (list[int]): list of pins connected to red leds 
        green_led_pins (list[int]): list of pins connected to green leds
        blue_led_pins (list[int]): list of pins connected to blue leds

    Raises:
        Exception: If length of list of pins connected to leds are not the same.

    Returns:
        tuple[list[machine.PWM], list[machine.PWM], list[machine.PWM]]: _description_
    """
    
    if len(blue_led_pins) == len(green_led_pins) == len(red_led_pins):
        list_led_b = [machine.PWM(machine.Pin(item))
                    for item in blue_led_pins]
        
        list_led_g = [machine.PWM(machine.Pin(item))
                    for item in green_led_pins]
        
        list_led_r = [machine.PWM(machine.Pin(item))
                for item in red_led_pins]
        
        for i in range(len(list_led_r)):
            list_led_g[i].freq(1000)
            list_led_b[i].freq(1000)
            list_led_r[i].freq(1000)
    else: 
        raise Exception("Length of red_led_pins, blue_led_pins and" +
                        "green_led_pins must be the same!")
        
    return list_led_b, list_led_g, list_led_r



potentiometer: machine.ADC = machine.ADC(26)
list_led_b, list_led_g, list_led_r = prepare_pins([15, 12, 9], [14, 11, 8], [13, 10, 7])

colors, first_run = load_saved_colors_form_file()

state_of_button_change_color = 'b' if first_run else 'loaded'

#thread with handling buttons events 
_thread.start_new_thread(button_on_off_thread, ())

temp_colors = [colors['b'], colors['g'], colors['r']]
visual_effects = VisualEffects(list_led_b, list_led_g, list_led_r, temp_colors)

while True:
    result: int = (0 if potentiometer.read_u16() < 300 else potentiometer.read_u16())
    
    if state_of_button_change_color == 'b':
        temp_colors[0] = result
        change_specific_color(list_led_b, result)
        
    elif state_of_button_change_color == 'g':
        temp_colors[1] = result
        change_specific_color(list_led_g, result)
        
    elif state_of_button_change_color == 'r':
        temp_colors[2] = result
        change_specific_color(list_led_r, result)
        
    elif state_of_button_change_color == 'save':
        first_run = False
        colors['b'] = temp_colors[0]
        colors['g'] = temp_colors[1]
        colors['r'] = temp_colors[2]
        
        with open('data.txt', 'w') as file:
            string_to_file = f"{colors['b']} {colors['g']} {colors['r']}"
            file.write(string_to_file)

    elif state_of_button_change_color == 'loaded':
        change_specific_color(list_led_b, colors['b'])
        change_specific_color(list_led_g, colors['g'])
        change_specific_color(list_led_r, colors['r'])
        
    elif state_of_button_change_color == 'visual_effects':
        visual_effects.temp_colors = temp_colors
        visual_effects.breath_effect()
    
    elif not first_run:
        change_specific_color(list_led_b, 0)
        change_specific_color(list_led_g, 0)
        change_specific_color(list_led_r, 0)
        state_of_button_change_color = 'loaded'
        
    elif first_run:
        change_specific_color(list_led_b, 0)
        change_specific_color(list_led_g, 0)
        change_specific_color(list_led_r, 0)