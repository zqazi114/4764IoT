from machine import Pin, PWM, ADC, Timer, disable_irq, enable_irq, I2C, RTC
import machine
import time
import ssd1306
from global_s import Globals

import micropython
micropython.alloc_emergency_exception_buf(100)

# Pin definitions
LED = 14
SWITCH = 12
OLED_A = 13
OLED_B = 15
TEST_LED = 0
PIEZO = 0
OLED_C = 16
TEST_LED2 = 2
SDA = 4
SCL = 5

# Address
OLED_ADDR = 0x3f
IMU_ADDR = 0x53
IMU_REG = 0x32

DEBOUNCE_TIME = 1000
DIGITS = (0, 3, 6, 9, 12, 15)

class Lab3:
    def __init__(self):
        #LED
        self.freq = 1
        self.duty = 512
        self.led = PWM(Pin(LED),freq=self.freq,duty=self.duty)
        
        # Piezo
        #self.piezo = PWM(Pin(PIEZO),freq=self.freq,duty=self.duty)

        # ALS
        self.als = ADC(0)
        self.als_timer = Timer(0)
        self.als_timer.init(period=5000, mode=Timer.PERIODIC,callback=self.als_cb)

        # Buttons
        self.switch = Pin(SWITCH, Pin.IN)
        self.switch_ts = time.ticks_ms()
        self.switch_pending = False

        self.oled_a = Pin(OLED_A, Pin.IN)
        self.oled_a_ts = time.ticks_ms()
        self.oled_a_pending = False

        self.oled_b = Pin(OLED_B, Pin.IN)
        self.oled_b_ts = time.ticks_ms()
        self.oled_b_pending = False
        
        self.oled_c = Pin(OLED_C, Pin.IN)
        self.oled_c_ts = time.ticks_ms()
        self.oled_c_pending = False
        
        self.button_timer = Timer(1)
        self.button_timer.init(period=10, mode=Timer.PERIODIC,callback=self.button_cb2)
    
        # OLED
        self.i2c = I2C(scl=Pin(SCL), sda=Pin(SDA), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled_brightness = 0.5 
        self.oled_direction = 0
        self.ticks = 0

        # RTC
        self.mode = 0 # 0: Clock, 1: Set, 2: Alarm
        self.rtc = RTC()
        date = [2018, 9, 27, 1, 12, 48, 0, 0]
        self.rtc.datetime(date)
        self.current_time = self.rtc.datetime()
        self.current_digit = 0
        self.clock_timer = Timer(2)
        self.clock_timer.init(period=1000, mode=Timer.PERIODIC, callback=self.clock_cb)

        # Interrupt table
        self.INT_als = False
        self.INT_rtc = False

        self.control_timer = Timer(3)
        self.control_timer.init(period=10, mode=Timer.PERIODIC, callback=self.control_cb)

        # Alarm
        self.alarm_timer = Timer(4)
        self.alarm_duration = 0

        # Globals
        self.globals = Globals()
        
        # test LED
        self.test_led = Pin(TEST_LED, Pin.OUT)
        self.test_led.off()
        
        return

################ LAB 3 ######################
   
    def print_text(self,text):
        m = self.mode
        self.mode = 5
        self.oled.fill(0)
        self.oled.show()
        for i in range(len(text)):
            t = text[:i+1]
            self.oled.text(t, 0, 0)
            self.oled.show()
            time.sleep_ms(500)
        self.oled.invert(True)
        self.oled.show()
        time.sleep_ms(1000)
        self.oled.invert(False)
        self.oled.show()
        time.sleep_ms(1000)
        self.oled.show()
        self.mode = m
        return

    def set_alarm(self):
        self.alarm_timer.init(period=1000, mode=Timer.PERIODIC, callback=self.alarm_cb)
        return

    def alarm_cb(self, timer):
        self.alarm_duration = self.alarm_duration - 1
        if self.alarm_duration <= 0:
            #self.mode = 3
            self.alarm_timer.deinit()
            self.print_text("WAKE UP!!!")
        return

    def format_alarm(self):
        s = self.alarm_duration % 60
        m = (self.alarm_duration // 60) % 60
        h = (self.alarm_duration // 3600) % 60
        alarmStr = "{:02d}:{:02d}:{:02d}".format(h, m, s)
        return alarmStr

    def adjust_brightness(self,brightness):
        b_arr = bytearray([0x80, 0x81])
        self.i2c.writeto(0x3c, b_arr)
        b_arr = bytearray([0x80, brightness])
        self.i2c.writeto(0x3c, b_arr)
        self.test_led.on()
        return
    
    def scroll_text(self, direction):
        self.oled_direction = direction
        self.ticks = 0
        self.mode = 4
        return

################ TIMERS ######################

    def als_cb(self, timer):
        brightness = self.als.read()
        if brightness <= 512:
            brightness = 10
        else:
            brightness = 1000
        brightness = (brightness*255)//1024
        self.adjust_brightness(brightness)
        return
    
    def clock_cb(self, timer):
        # Normal
        if self.mode == 0:
            self.oled.fill(0)
            self.oled.show()
            date = self.rtc.datetime()
            dateStr = "{}/{:02d}".format(date[1], date[2])
            timeStr = "{:02d}:{:02d}:{:02d}:{:02d}".format(date[3], date[4], date[5], date[6])
            self.oled.text(dateStr + " " + timeStr, 0, 20, 1)
            self.oled.show()
        # Edit
        elif self.mode == 1:
            self.oled.fill(1)
            self.oled.show()
            date = self.current_time
            dateStr = "{}/{:02d}".format(date[1], date[2])
            timeStr = "{:02d}:{:02d}:{:02d}:{:02d}".format(date[3], date[4], date[5], date[6])
            self.oled.text(dateStr + " " + timeStr, 0, 20, 0)
            self.oled.show()
            
            self.draw_cursor()
        elif self.mode == 2:
            text = "Alarm"
            self.oled.fill(0)
            self.oled.show()
            self.oled.text(text, 0, 0, 1)
            self.oled.show()
            alarmStr = self.format_alarm()
            self.oled.text(alarmStr, 0, 20, 1)
            self.oled.show()
        elif self.mode == 3:
            text = "Alarm"
            self.oled.fill(0)
            self.oled.show()
            self.oled.text(text, 0, 0, 1)
            self.oled.show()
            alarmStr = self.format_alarm()
            self.oled.text(alarmStr, 0, 20, 1)
            self.oled.show()
        # IMU scroll
        elif self.mode == 4:
            self.ticks = self.ticks + 1
            self.oled.fill(0)
            self.oled.show()
            column = self.globals.column
            row = self.globals.row
            if self.oled_direction == 0:
                row = row + self.ticks*2
                if row >= 35:
                    row = -5
                    self.ticks = 0
            elif self.oled_direction == 1:
                row = row - self.ticks*2
                if row <= -5:
                    row = 30
                    self.ticks = 0
            #elif self.oled_direction == 2:
            #    column = column + self.ticks*2
            #    if column >= 100:
            #        column = -50
            #        self.ticks = 0
            #elif self.oled_direction == 3:
            #    column = column - self.ticks*2
            #    if column <= -5:
            #        column = 105
            #        self.ticks = 0
            dirStr = "Direction: {0}".format(self.oled_direction)
            self.oled.text(dirStr, column, row, 1)
            self.oled.show()
            self.globals.row = row
            self.globals.column = column
        return
    
    def draw_cursor(self):
        d = DIGITS[self.current_digit]
        for i in range(8):
            for j in range(8):
                x = d*8 + i
                y = 20 + j
                self.oled.pixel(x,y,0)
        self.oled.show()
        return

    def increment_digit(self):
        #date = (2018, 9, 27, 1, 12, 48, 0, 0)
        d = self.current_digit + 1
        t = self.current_time
        self.current_time = [t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7]]
        self.current_time[d] = t[d] + 1
        return

################ BUTTONS ######################

    def button_cb2(self, timer):
        t = time.ticks_ms()
        if self.switch.value() == 1 and (t - self.switch_ts) > DEBOUNCE_TIME:
            self.switch_pending = True
            self.switch_ts = time.ticks_ms()
            self.mode = (self.mode + 1) % 5
            if self.mode == 1:
                self.current_time = self.rtc.datetime()
            elif self.mode == 2:
                self.rtc.datetime(self.current_time)
            elif self.mode == 3:
                self.set_alarm()
    
        if self.oled_a.value() == 0 and (t - self.oled_a_ts) > DEBOUNCE_TIME:
            self.oled_a_pending = True
            self.oled_a_ts = time.ticks_ms()

        if self.oled_c.value() == 0 and (t - self.oled_c_ts) > DEBOUNCE_TIME:
            self.oled_c_pending = True
            self.oled_c_ts = time.ticks_ms()

        return

    def control_cb(self, timer):
        if self.mode == 1:
            if self.oled_a_pending:
                self.oled_a_pending = False
                self.current_digit = self.current_digit + 1
            elif self.oled_c_pending:
                self.oled_c_pending = False
                #self.current_digit = self.current_digit - 1
                self.increment_digit()
        elif self.mode == 2:
            if self.oled_c_pending:
                self.oled_c_pending = False
                self.alarm_duration = self.alarm_duration + 1
        return

################ INTERRUPTS ##################


#########################################
