from machine import Pin
import time

def blink_LED():
    p2 = Pin(2, Pin.OUT)
    p0 = Pin(0, Pin.OUT)
    for i in range(100):
        time.sleep(1)
        p0.on()
        p2.on()
        time.sleep(1)
        p2.off()
        time.sleep(1)
        p0.off()
    return

def blink_blue_LED():
    p0 = Pin(0, Pin.OUT)
    for i in range(100):
        p0.on()
        time.sleep(2)
        p0.off()
        time.sleep(2)
    return

def dot(pin):
    delay = 0.5
    time.sleep(delay)
    pin.on()
    time.sleep(delay)
    pin.off()

def dash(pin):
    delay = 0.5
    time.sleep(delay)
    pin.on()
    time.sleep(delay)
    time.sleep(delay)
    pin.off()

def SOS_LED():
    p0 = Pin(0, Pin.OUT)
    # . . . - - - . . .
    for i in range(10):
        dot(p0)
        dot(p0)
        dot(p0)
        dash(p0)
        dash(p0)
        dash(p0)
        dot(p0)
        dot(p0)
        dot(p0)

blink_LED()
#blink_blue_LED()
#SOS_LED()
