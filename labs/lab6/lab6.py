from machine import Pin, I2C, Timer, RTC
import ssd1306
import time

from google import GoogleAPI
from iotnetwork import Network
from weather import OpenWeather
from tstwitter import Twitter

import urequests as requests

class Lab6:

    # Server
    IP = '34.224.78.191'
    PORT = 80
    HTTP = 'http://'
    PATH = '/esp8266/'
    ACCELSTART = 'accelstart&'
    ACCELDATA = 'acceldata&'
    ACCELSTOP = 'accelstop&'

    # Pin Definition
    TEST_LED = 0
    TEST_LED2 = 2
    LED = 14
    BUTTON = 12
    BUTTON2 = 15 
    SCL = 5
    SDA = 4
    OLED_A = 13 
    OLED_C = 16 

    # I2C Addresses
    OLED_ADDR = 0x3f
    IMU_ADDR = 0x53
    IMU_REG = 0x32

    # MISC
    DEBOUNCE_TIME = 1000
    DIGITS = (0, 3, 6, 9, 12, 15)
    COLUMBIA = ["C", "O", "L", "U", "M", "B", "I", "A"]
    MAXREADINGS = 100
    IMU_INT = 100
    SLEEP = 1000

    def __init__(self,loc="home"):
        # Test LED
        self.test_led = Pin(Lab6.TEST_LED, Pin.OUT)
        self.test_led.off()
        
        # Class Vars
        self.network = Network(loc)
        self.google = GoogleAPI()
        self.weather = OpenWeather()
        self.twitter = Twitter()

        # Timers
        #self.location_timer = Timer(-1)
        #self.location_timer.init(period=5000, mode=Timer.PERIODIC, callback=self.location_cb)
        
        # LED
        self.led = Pin(Lab6.LED, Pin.OUT)

        # OLED
        self.i2c = I2C(scl=Pin(Lab6.SCL), sda=Pin(Lab6.SDA), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled_brightness = 0.5 
        self.oled_direction = 0
        self.ticks = 0
        
        # Buttons
        self.button = Pin(Lab6.BUTTON, Pin.IN)
        self.button_ts = time.ticks_ms()

        self.oled_a = Pin(Lab6.OLED_A, Pin.IN)
        self.oled_a_ts = time.ticks_ms()

        self.button2 = Pin(Lab6.BUTTON2, Pin.IN)
        self.button2_ts = time.ticks_ms()
        
        self.oled_c = Pin(Lab6.OLED_C, Pin.IN)
        self.oled_c_ts = time.ticks_ms()
        
        self.button_timer = Timer(1)
        self.button_timer.init(period=10, mode=Timer.PERIODIC,callback=self.button_cb)
        
        # IMU
        self.imu_timer = Timer(2)
        self.imu_timer.init(period=Lab6.IMU_INT, mode=Timer.PERIODIC, callback=self.imu_cb)
        self.imu_buf = bytearray(6)
        self.x = 0
        self.y = 0
        self.z = 0
        self.imu_init()

        # Character Recognition
        self.charIdx = -1
        self.calibrating = False
        self.readings_x = []
        self.readings_y = []
        self.readings_z = []

        # Test LED 2
        self.test_led = Pin(Lab6.TEST_LED2, Pin.OUT)
        self.test_led.off()

        return

################## OLED ####################

    def print_text_slow(self,text):
        self.oled.fill(0)
        self.oled.show()
        row = 0
        col = 0
        for i in range(len(text)):
            t = text[i]
            self.oled.text(t, col*8, row*10)
            self.oled.show()
            col = col + 1
            if col > 15:
                col = 0
                row = row + 1
            time.sleep_ms(1)
        return
    
    def print_text(self,text,row):
        for x in range(128):
            for y in range(10):
                self.oled.pixel(x, y + row*10, 0)
        self.oled.text(text, 0, row*10)
        self.oled.show()
        return

##################### IMU #######################
    
    def imu_init(self):
        b = bytearray(1)
        b[0] = 0
        self.i2c.writeto_mem(Lab6.IMU_ADDR, 0x2d, b)
        b[0] = 16
        self.i2c.writeto_mem(Lab6.IMU_ADDR, 0x2d, b)
        b[0] = 8
        self.i2c.writeto_mem(Lab6.IMU_ADDR, 0x2d, b)
        return

    def imu_cb(self, timer):
        self.imu_x()
        self.imu_y()
        self.imu_z()
        if self.calibrating:
            print("LOG: (X,Y,Z) ({}, {}, {})".format(self.x, self.y, self.z))
            self.readings_x.append(self.x)
            self.readings_y.append(self.y)
            self.readings_z.append(self.z)
        return

    def imu_x(self):
        self.imu_buf = self.i2c.readfrom_mem(Lab6.IMU_ADDR, Lab6.IMU_REG, 6)
        self.x = (int(self.imu_buf[1]) << 8) | self.imu_buf[0]
        if self.x > 32767:
            self.x = self.x - 65536
        return

    def imu_y(self):
        self.imu_buf = self.i2c.readfrom_mem(Lab6.IMU_ADDR, Lab6.IMU_REG, 6)
        self.y = (int(self.imu_buf[3]) << 8) | self.imu_buf[2]
        if self.y > 32767:
            self.y = self.y - 65536
        return

    def imu_z(self):
        self.imu_buf = self.i2c.readfrom_mem(Lab6.IMU_ADDR, Lab6.IMU_REG, 6)
        self.z = (int(self.imu_buf[5]) << 8) | self.imu_buf[4]
        if self.z > 32767:
            self.z = self.z - 65536
        return

################## GEOLOCATE ####################
    
    def update_location(self):
        print("LOG: Updating location")
        self.google.geolocate()
        
        lat = self.google.location["location"]["lat"]
        lng = self.google.location["location"]["lng"]

        text = "lat: {:.2f}lon: {:.2f}".format(lat, lng)
        self.print_text_slow(text)
        return

################## WEATHER ####################

    def update_weather(self):
        print("LOG: Updating weather")
        self.google.geolocate()
        self.weather.get_current_weather(self.google.location)
        temp = self.weather.weather["main"]["temp"]
        desc = self.weather.weather["weather"][0]["main"]
        text = "Temp: {}F \nDesc: {}".format(temp, desc)
        print(text)
        self.print_text_slow(text)
        return

################## TWITTER ####################

    def send_tweet(self):
        tweet = "Twitter Hello!!"
        self.twitter.send_tweet(tweet)
        return

################## BUTTONS ####################
    
    def button_cb(self, timer):
        t = time.ticks_ms()
        if self.button.value() == 1 and (t - self.button_ts) > Lab6.DEBOUNCE_TIME:
            self.button_handler()
        if self.button2.value() == 1 and (t - self.button2_ts) > Lab6.DEBOUNCE_TIME:
            self.button2_handler()
        if self.oled_a.value() == 0 and (t - self.oled_a_ts) > Lab6.DEBOUNCE_TIME:
            self.oled_a_handler()
        if self.oled_c.value() == 0 and (t - self.oled_c_ts) > Lab6.DEBOUNCE_TIME:
            self.oled_c_handler()
        return

    def button_handler(self):
        self.button_ts = time.ticks_ms()
        self.charIdx = (self.charIdx + 1) % len(self.COLUMBIA)
        prompt = "Letter: {}".format(self.COLUMBIA[self.charIdx])
        self.print_text(prompt, 0)
        print("LOG: selected letter {}".format(self.COLUMBIA[self.charIdx]))
        return

    def button2_handler(self):
        self.button2_ts = time.ticks_ms()
        self.calibrating = not self.calibrating
        if self.calibrating:
            prompt = "Calibrating ..."
        else:
            prompt = "Done cal."
            self.send_readings_to_server()
        self.print_text(prompt, 1)
        print("LOG: {}".format(prompt))
        return

    def oled_a_handler(self):
        self.oled_a_ts = time.ticks_ms()
        self.update_weather()
        return
    
    def oled_c_handler(self):
        self.oled_c_ts = time.ticks_ms()
        self.send_tweet()
        return

################## HTTP ####################

    def send_readings_to_server(self):
        print("LOG: sending {} readings to server".format(len(self.readings_x)))
        
        url = Lab6.HTTP + Lab6.IP + Lab6.PATH + Lab6.ACCELSTART + 'char=' + Lab6.COLUMBIA[self.charIdx]
        method = "GET"
        print("LOG: communicating to server with uri {}".format(url))
        resp = requests.request(method, url)
        print("LOG: {}{}".format(resp.status_code, resp.reason))
       
        for i in range(len(self.readings_x)):
            #time.sleep_ms(Lab6.SLEEP)
            reading = str(self.readings_x[i]) + ',' + str(self.readings_y[i]) + ',' + str(self.readings_z[i]) 
            url = Lab6.HTTP + Lab6.IP + Lab6.PATH + Lab6.ACCELDATA + 'val=' + reading
            print("LOG: communicating to server with uri {}".format(url))
            resp = requests.request(method, url)
            print("LOG: {}{}".format(resp.status_code, resp.reason))
       
        #time.sleep_ms(Lab6.SLEEP)
        url = Lab6.HTTP + Lab6.IP + Lab6.PATH + Lab6.ACCELSTOP + 'char=' + Lab6.COLUMBIA[self.charIdx]
        method = "GET"
        print("LOG: communicating to server with uri {}".format(url))
        resp = requests.request(method, url)
        print("LOG: {}{}".format(resp.status_code, resp.reason))

        self.readings_x = []
        self.readings_y = []
        self.readings_z = []
        return

##############################################
##############################################
