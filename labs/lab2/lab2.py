from machine import Pin, PWM, ADC, Timer, disable_irq, enable_irq
import time

class Lab2:
    def __init__(self, devices):
        #LED
        self.freq = 1
        self.duty = 512
        self.led = PWM(Pin(13),freq=self.freq,duty=self.duty)
        
        # Piezo
        self.piezo = PWM(Pin(15),freq=self.freq,duty=self.duty)

        # ALS
        self.als = ADC(0)

        # Switch
        self.switch = Pin(14, Pin.IN)
        self.switch.irq(handler=self.switch_cb,trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,hard=True)
    
        # Interrupt flags
        self.do_debounce = False
        self.read_als = False

        # Timer
        self.timer = Timer(-1)
        self.timer.init(period=1000, mode=Timer.PERIODIC,callback=self.timer_cb)
        
        # test LED
        self.test_led = Pin(2, Pin.OUT)
        self.test_led.off()

        return

    def timer_cb(self, timer):
        if self.read_als:
            self.duty = self.als.read()
            self.led.duty(self.duty)
        self.test_led.off()
        
        #if self.do_debounce:
        #    self.do_debounce = False
        #    self.debounce()
        return

    # Interrupt callback
    def switch_cb(self, pin):
        state = disable_irq()
        value = pin.value()
        if value == 1:
            self.read_als = True
        else:
            self.read_als = False
        self.do_debounce = True
        self.test_led.on()
        enable_irq(state)
        return

    # Debounce
    def debounce(self):
        cur_val = self.switch.value()
        dur_active = 0
        while dur_active < 10:
            if pin.value() == cur_val:
                dur_active = dur_active + 1
            else:
                cur_val = self.switch.value()
                dur_active = 0
            time.sleep_ms(1) # 1 millisecond
        if cur_val == 1:
            self.read_als = True
        else:
            self.read_als = False
        return
