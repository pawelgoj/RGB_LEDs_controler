import machine
import _thread
from visual_effects import VisualEffects
from button import Button
from functions import change_specific_color
from functions import prepare_pins
from functions import button_change_color_fn
from functions import load_saved_colors_form_file
from button import ButtonChangeColor


button_change_color_pin: machine.Pin = machine.Pin(16, machine.Pin.IN,
                                               machine.Pin.PULL_DOWN)

state_of_button_change_color: ButtonChangeColor = ButtonChangeColor('b')

button_on_off_pressed: bool = False

start_button_oscillation_time: int|None = 0


def button_on_off_thread() -> None:
    
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
            

potentiometer: machine.ADC = machine.ADC(26)
list_led_b, list_led_g, list_led_r = prepare_pins([15, 12, 9], [14, 11, 8], [13, 10, 7])

colors, first_run = load_saved_colors_form_file()

state_of_button_change_color.state = 'b' if first_run else 'loaded'

#thread with handling buttons events 
_thread.start_new_thread(button_on_off_thread, ())

temp_colors = [colors['b'], colors['g'], colors['r']]
visual_effects = VisualEffects(list_led_b, list_led_g, list_led_r, temp_colors)


if first_run:
    change_specific_color(list_led_b, 0)
    change_specific_color(list_led_g, 0)
    change_specific_color(list_led_r, 0)
    state_of_button_change_color.state = 'b'
else: 
    change_specific_color(list_led_b, 0)
    change_specific_color(list_led_g, 0)
    change_specific_color(list_led_r, 0)
    state_of_button_change_color.state = 'loaded'

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