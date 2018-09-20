from machine import Pin,PWM

def blink_LED_PWM():
    pwm0 = PWM(Pin(0), freq=1, duty=512)
    #pwm2 = PWM(Pin(2), freq=1, duty=512)
    return
