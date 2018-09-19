from machine import Pin, PWM, Timer

def pwm_on_pin(freq, duty, pin):
    pwm = PWM(Pin(pin))
    pwm.freq(freq)
    pwm.duty(duty)
    return pwm

def led_init():
    pin = 13
    freq = 1  #1-1k Hz
    duty = 512 #0 - 1023
    global led
    led = pwm_on_pin(freq, duty, pin)
    return

def piezo_init():
    pin = 15
    freq = 1
    duty = 512
    global piezo
    piezo = pwm_on_pin(freq, duty, pin)
    return

def als_init():
    global als
    als = ADC(0)
    tim = Timer(-1)
    tim.init(period=1000, mode=Timer.PERIODIC, callback=read_als)
    return als

def read_als():
    global als
    als.read()
    return

def init_all():
    led_init()
    piezo_init()
    als_init()
    return

def deinit_all():
    led.deinit()
    piezo.deinit()
    als.deinit()
    return

led
piezo
als
