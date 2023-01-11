import machine


def change_specific_color(list_of_pins: list[machine.PWM], result: int) -> None:
    for item in list_of_pins:
        item.duty_u16(result)
        