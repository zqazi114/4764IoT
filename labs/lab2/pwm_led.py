from machine import Pin, PWM, Timer, ADC

def led_test():
    p13 = Pin(13, Pin.OUT)
    p13.on()
    return

def led_init():
    global led
    pin = 13
    freq = 1  #1-1k Hz
    duty = 512 #0 - 1023
    led = PWM(Pin(pin), freq=freq, duty=duty)
    return

def piezo_init():
    global piezo
    pin = 15
    freq = 1
    duty = 512
    piezo = PWM(Pin(pin), freq=freq, duty=duty)
    return

def als_init():
    global als
    als = ADC(0)
    return 

def init_all():
    led_init()
    #piezo_init()
    als_init()
    return

def deinit_all():
    global led
    global piezo
    global adc
    global timer
    led = Pin(13,Pin.OUT)
    led.off()
    piezo = Pin(15,Pin.OUT)
    piezo.off()
    timer.deinit()
    return

def init_timer():
    global timer
    timer = Timer(-1)
    timer.init(period=100, mode=Timer.PERIODIC,callback=timer_cb)
    return timer

def deinit_timer():
    global timer
    timer.deinit()
    return

def timer_cb(tim):
    global led
    global als
    val = als.read()
    led.duty(val)
    return

piezo = 0
led = 0
adc = 0
timer = 0
