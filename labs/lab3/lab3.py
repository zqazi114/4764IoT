from machine import Pin, PWM, ADC, Timer, disable_irq, enable_irq, I2C, RTC
import machine
import time
import ssd1306

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

DEBOUNCE_TIME = 100

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
        self.switch_prev = 0
        self.switch_pending = False

        self.oled_a = Pin(OLED_A, Pin.IN)
        self.oled_a_ts = time.ticks_ms()
        self.oled_a_prev = 0
        self.oled_a_pending = False

        self.oled_b = Pin(OLED_B, Pin.IN)
        self.oled_b_ts = time.ticks_ms()
        self.oled_b_prev = 0
        
        self.oled_c = Pin(OLED_C, Pin.IN)
        self.oled_c_ts = time.ticks_ms()
        self.oled_c_prev = 0
        
        self.button_timer = Timer(1)
        self.button_timer.init(period=10, mode=Timer.PERIODIC,callback=self.button_cb)
        #self.switch.irq(handler=self.switch_cb,trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,hard=True)
    
        # OLED
        self.i2c = I2C(scl=Pin(SCL), sda=Pin(SDA), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled_brightness = 0.5 

        # RTC
        self.mode = 0 # 0: Clock, 1: Set, 2: Alarm
        self.rtc = RTC()
        date = (2018, 9, 27, 1, 12, 48, 0, 0)
        self.rtc.datetime(date)
        self.current_time = self.rtc.datetime()
        self.current_digit = 0
        self.current_tiktok = 1
        self.clock_timer = Timer(2)
        self.clock_timer.init(period=1000, mode=Timer.PERIODIC, callback=self.clock_cb)

        # Interrupt table
        self.INT_als = False
        self.INT_switch = False
        self.INT_oled_a = False
        self.INT_oled_b = False
        self.INT_oled_c = False
        self.INT_rtc = False

        self.control_timer = Timer(3)
        self.control_timer.init(period=10, mode=Timer.PERIODIC, callback=self.control_cb)

        # Alarm
        self.alarm_timer = Timer(4)

        # IMU
        self.init_imu()
        self.imu_timer = Timer(5)
        self.imu_timer.init(period=15000, mode=Timer.ONE_SHOT, callback=self.imu_cb)
        self.imu_buf = bytearray(6)
        self.x_val = 0
        self.y_val = 0
        self.z_val = 0

        # test LED
        self.test_led = Pin(TEST_LED, Pin.OUT)
        self.test_led.off()
        self.test_led2 = Pin(TEST_LED2, Pin.OUT)
        self.test_led2.off()

        return

################ LAB 3 ######################
   
    def print_text(self,text):
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
        return

    def set_alarm(self, duration):
        self.alarm_timer.init(period=duration*1000, mode=Timer.ONE_SHOT, callback=self.alarm_cb)
        self.test_led2.on()
        return

    def alarm_cb(self, timer):
        self.mode = 2
        self.print_text("WAKE UP!!!")
        self.mode = 0
        return

    def adjust_brightness(self,brightness):
        b_arr = bytearray([0x80, 0x81])
        self.i2c.writeto(OLED_ADDR, b_arr)
        b_arr = bytearray([0x80, brightness])
        self.i2c.writeto(OLED_ADDR, b_arr)
        return
    
    def imu_cb(self, timer):
        #self.x_val = self.imu_x() 
        #self.y_val = self.imu_y() 
        #self.z_val = self.imu_z() 
        text = "{} {} {}".format(x)
        #self.mode = 3
        #self.oled.text(text, 0, 0)
        #self.oled.show()
        return

    def scroll_text(self, direction):
        a = 1
        return

    def init_imu(self):
        b = bytearray(1)
        b[0] = 0
        self.i2c.writeto_mem(IMU_ADDR, 0x2d, b)
        b[0] = 16
        self.i2c.writeto_mem(IMU_ADDR, 0x2d, b)
        b[0] = 8
        self.i2c.writeto_mem(IMU_ADDR, 0x2d, b)
        return

    def imu_x(self):
        self.imu_buf = self.i2c.readfrom_mem(IMU_ADDR, IMU_REG, 6)
        x = (int(self.imu_buf[1]) << 8) | self.imu_buf[0]
        if x > 32767:
            x = x - 65536
        return x

    def imu_y(self):
        self.imu_buf = self.i2c.readfrom_mem(IMU_ADDR, IMU_REG, 6)
        y = (int(self.imu_buf[3]) << 8) | self.imu_buf[2]
        if y > 32767:
            y = y - 65536
        return y

    def imu_z(self):
        self.imu_buf = self.i2c.readfrom_mem(IMU_ADDR, IMU_REG, 6)
        z = (int(self.imu_buf[5]) << 8) | self.imu_buf[4]
        if z > 32767:
            z = z - 65536
        return z

################ TIMERS ######################

    def als_cb(self, timer):
        #if self.INT_als:
            #self.duty = self.als.read()
            #self.led.duty(self.duty)
        brightness = self.als.read()
        brightness = (brightness*255)//1024
        self.adjust_brightness(brightness)
        return
    
    def clock_cb(self, timer):
        if self.mode == 0:
            self.oled.fill(0)
            self.oled.show()
            date = self.rtc.datetime()
            dateStr = "{}/{:02d}".format(date[1], date[2])
            timeStr = "{:02d}:{:02d}:{:02d}:{:02d}".format(date[3], date[4], date[5], date[6])
            self.oled.text(dateStr + " " + timeStr, 0, 20, 1)
            self.oled.show()
        elif self.mode == 1:
            self.oled.fill(1)
            self.oled.show()
            date = (2018, 9, 27, 1, 12, 48, 0, 0)
            #date = self.current_time
            dateStr = "{}/{:02d}".format(date[1], date[2])
            timeStr = "{:02d}:{:02d}:{:02d}:{:02d}".format(date[3], date[4], date[5], date[6])
            self.oled.text(dateStr + " " + timeStr, 0, 20, 0)
            self.oled.show()
            
            self.draw_cursor(self.current_digit)
        elif self.mode == 3:
            a = 1
        return
    
    def draw_cursor(self, digit):
        if self.current_tiktok == 1:
            self.current_tiktok = 0
        else:
            self.current_tiktok = 1
        for i in range(10):
            for j in range(10):
                x = digit*10 + i
                y = 20 + j
                self.oled.pixel(x,y,0)#self.current_tiktok)
        self.oled.show()
        return

    def control_cb(self, timer):
        if self.mode == 0:
            if self.INT_oled_a:# and self.INT_oled_b and ~self.INT_oled_c:
                self.mode = 1
                self.current_time = self.rtc.datetime()
            elif self.INT_oled_a and self.INT_oled_c:
                self.mode = 2
        elif self.mode == 1:
            if self.INT_oled_a:
                self.mode = 0
            elif self.INT_als:#self.INT_oled_b:
                self.current_digit = self.current_digit + 1
            elif self.INT_oled_c:
                self.current_digit = self.current_digit - 1
        elif self.mode == 2:
            if self.INT_oled_a:
                self.mode = 0

        return

################ BUTTONS ######################

    def button_cb(self, timer):
        if self.switch_pending:
            self.debounce(SWITCH)
        elif self.switch_prev != self.switch.value(): 
            self.switch_prev = self.switch.value()
            self.switch_pending = True
            self.switch_ts = time.ticks_ms()
            self.debounce(SWITCH)
        
        if self.oled_a_pending:
            self.debounce(OLED_A)
        elif self.oled_a_prev != self.oled_a.value(): 
            self.oled_a_prev = self.oled_a.value()
            self.oled_a_pending = True
            self.debounce(OLED_A)
        return

    def debounce(self, switch):
        if switch == SWITCH:
            if time.ticks_diff(time.ticks_ms(),self.switch_ts) > DEBOUNCE_TIME:
                self.switch_pending = False
                if self.switch_prev == self.switch.value():
                    if self.switch.value() == 0:
                        #self.INT_als = True
                        self.test_led.on()
                    else:
                        #self.INT_als = False
                        self.test_led.off()
        elif switch == OLED_A:
            if time.ticks_diff(time.ticks_ms(),self.oled_a_ts) > DEBOUNCE_TIME:
                self.oled_a_pending = False
                if self.oled_a_prev == self.oled_a.value():
                    if self.oled_a.value() == 0:
                        self.INT_oled_a = True
                        #self.test_led2.on()
                    else:
                        self.INT_oled_a = False
                        #self.test_led2.off()
        elif switch == OLED_B:
            if time.ticks_diff(time.ticks_ms(),self.oled_b_ts) > DEBOUNCE_TIME:
                self.oled_b_ts = time.ticks_ms()
                if self.oled_b_prev == self.oled_b.value():
                    if self.oled_b.value() == 0:
                        self.INT_oled_b = True
                        self.test_led.on()
                    else:
                        self.INT_oled_b = False
                        self.test_led.off()
                else:
                    self.oled_b_prev = self.oled_b.value()
        elif switch == OLED_C:
            if time.ticks_diff(time.ticks_ms(),self.oled_c_ts) > 50:
                self.oled_c_ts = time.ticks_ms()
                if self.oled_c_prev == self.oled_c.value():
                    if self.oled_c.value() == 0:
                        self.INT_oled_c = True
                        self.test_led.on()
                    else:
                        self.INT_oled_c = False
                        self.test_led.off()
                else:
                    self.oled_c_prev = self.oled_c.value()
        return

################ INTERRUPTS ######################


#########################################
