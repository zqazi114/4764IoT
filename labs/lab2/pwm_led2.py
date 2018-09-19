from machine import Pin, PWM, Timer

def pwm_on_pin(freq, duty, pin):
    pwm = PWM(Pin(pin))
    pwm.freq(freq)
    pwm.duty(duty)
    return

def pwm_led():
    pin = 13
    freq = 1  #1-1k Hz
    duty = 512 #0 - 1023
    pwm_on_pin(freq, duty, pin)
    return

def pwm_piezo():
    pin = 15
    freq = 1
    duty = 512
    pwm_on_pin(freq, duty, pin)
    return

def als_init():
    als = ADC(0)
    tim = Timer(-1)
    tim.init(period=1000, mode=Timer.PERIODIC, callback=read_als(als))
    return als

def read_als(als):
    als.read()
    return
