from machine import Pin

def button_callback(p):

    return

def button_init():
    p14 = Pin(14, Pin.IN)
    p14.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_callback)
    return
