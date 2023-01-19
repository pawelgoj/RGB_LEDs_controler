import machine
import utime
import os
from button import ButtonChangeColor
from button import Button


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
        
        
def button_change_color_fn(state_of_button_change_color: ButtonChangeColor, 
                        time: int|None, after_saved: bool, button_change_color: Button, last_button_state: str) \
                        -> tuple[ButtonChangeColor, int|None, bool, str]:
    """Function specifying the state of the color change button

    Args:
        state_of_button_change_color (str): colors 'r', 'g', 'b' or 'save', 'loaded'
        time (int): time.ticks_ms()
        after_saved (bool): Was the previous state_of_button_change_color 'save'? True/False
        button_change_color (Button): Button object
        last_button_state: (str): 
    Returns:
        tuple(state_of_button_change_color, iteration, after_saved, last_button_state)
    """
    pressed = button_change_color.pressed
    
    if (pressed is True) and (time is None):
        time = utime.ticks_ms()
        time_diff = -1
    elif (pressed is False) and (time is not None):
        time_diff = utime.ticks_diff(utime.ticks_ms(), time)
        time = None
    else:
        time_diff = -1
    
    if after_saved:
        after_saved = False
        state_of_button_change_color.state = 'loaded'
        
    elif time_diff < 1500 and time_diff >= 0: 

        if state_of_button_change_color.state == 'b':
            state_of_button_change_color.state = 'g'
        elif state_of_button_change_color.state == 'g':
            state_of_button_change_color.state = 'r'
        elif state_of_button_change_color.state == 'r':
            state_of_button_change_color.state = 'b'
        elif state_of_button_change_color.state == 'loaded':
            state_of_button_change_color.state = 'b'
        elif state_of_button_change_color.state == 'visual_effects':
            state_of_button_change_color.state = 'change'
            
    elif (time_diff < 4000) and (time_diff >= 1500):
        last_button_state = state_of_button_change_color.state
        state_of_button_change_color.state = 'save'
        after_saved = True
        
    elif time_diff >= 4000:
        state_of_button_change_color.state = 'visual_effects'
        
    return state_of_button_change_color, time, after_saved, last_button_state