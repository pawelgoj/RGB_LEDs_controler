import machine
import _thread
import os
import utime
from visual_effects import VisualEffects
from button import Button
from functions import change_specific_color
from button import ButtonChangeColor


button_change_color_pin: machine.Pin = machine.Pin(16, machine.Pin.IN,
                                               machine.Pin.PULL_DOWN)

state_of_button_change_color: ButtonChangeColor = ButtonChangeColor('b')


button_on_off_pressed: bool = False

start_button_oscillation_time: int|None = 0


        
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

def button_on_off_thread() -> None:
    
    import utime 
    """The thread for handling button events
    """
    
    global state_of_button_change_color
    button_change_color = Button(button_change_color_pin)
    

    time = None
    after_saved = False
    last_button_state = 'b'
    
    while True:
        state_of_button_change_color , time, after_saved, last_button_state =\
            button_change_color_fn(state_of_button_change_color, 
                                   time, after_saved, button_change_color, last_button_state)
            

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

state_of_button_change_color.state = 'b' if first_run else 'loaded'

#thread with handling buttons events 
_thread.start_new_thread(button_on_off_thread, ())

temp_colors = [colors['b'], colors['g'], colors['r']]
visual_effects = VisualEffects(list_led_b, list_led_g, list_led_r, temp_colors)

#main loop
while True:
    result: int = (0 if potentiometer.read_u16() < 300 else potentiometer.read_u16())
    
    if state_of_button_change_color.state == 'b':
        temp_colors[0] = result
        change_specific_color(list_led_b, result)
        
    elif state_of_button_change_color.state == 'g':
        temp_colors[1] = result
        change_specific_color(list_led_g, result)
        
    elif state_of_button_change_color.state == 'r':
        temp_colors[2] = result
        change_specific_color(list_led_r, result)
        
    elif state_of_button_change_color.state == 'save':
        first_run = False
        colors['b'] = temp_colors[0]
        colors['g'] = temp_colors[1]
        colors['r'] = temp_colors[2]
        
        with open('data.txt', 'w') as file:
            string_to_file = f"{colors['b']} {colors['g']} {colors['r']}"
            file.write(string_to_file)

    elif state_of_button_change_color.state == 'loaded':
        change_specific_color(list_led_b, colors['b'])
        change_specific_color(list_led_g, colors['g'])
        change_specific_color(list_led_r, colors['r'])
        
    elif state_of_button_change_color.state == 'visual_effects':
        visual_effects.temp_colors = temp_colors
        visual_effects.current_effect = 'breath_effect'
        visual_effects.effect_loop(potentiometer, state_of_button_change_color, list_led_b, list_led_g, 
                                   list_led_r, temp_colors)
    
    elif not first_run:
        change_specific_color(list_led_b, 0)
        change_specific_color(list_led_g, 0)
        change_specific_color(list_led_r, 0)
        state_of_button_change_color.state = 'loaded'
        
    elif first_run:
        change_specific_color(list_led_b, 0)
        change_specific_color(list_led_g, 0)
        change_specific_color(list_led_r, 0)