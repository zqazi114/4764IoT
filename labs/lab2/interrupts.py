from machine import Pin, Timer, disable_irq, enable_irq
import pwm_led

def setup_switch():
    global timer
    global switch
    global test_led
    test_led = Pin(2,Pin.OUT)
    test_led.on()
    pwm_led.init_all()
    switch = Pin(14, Pin.IN)
    switch.irq(handler=switch_cb,trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, hard=True)
    timer = pwm_led.init_timer()
    return

def switch_cb(pin):
    state = disable_irq()
    global test_led
    global switch
    global timer
    if switch.value() == 1:
        test_led.off()
        pwm_led.read_als()
        #timer = pwm_led.init_timer()
    else:
        test_led.on()
        #pwm_led.deinit_timer()
    enable_irq(state)
    return

test_led = 0
switch = 0
timer = 0
