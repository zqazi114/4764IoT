from machine import Pin, I2C, Timer, RTC
import ssd1306
import time

from google import GoogleAPI
from iotnetwork import Network
from weather import OpenWeather
from tstwitter import Twitter

class Lab4:

    # Pin Definition
    TEST_LED = 0
    TEST_LED2 = 2
    LED = 14
    LOC_BUTTON = 12
    SCL = 5
    SDA = 4
    OLED_A = 13 
    OLED_B = 15 
    OLED_C = 16 

    # I2C Addresses
    OLED_ADDR = 0x3f
    IMU_ADDR = 0x53
    IMU_REG = 0x32
    
    # 
    DEBOUNCE_TIME = 1000
    DIGITS = (0, 3, 6, 9, 12, 15)
    
    # Saved Networks
    HOME_SSID = "It hurts when IP"
    HOME_PASS = "empirestate3"
    
    def __init__(self,loc="uni"):
        # Test LED
        self.test_led = Pin(Lab4.TEST_LED, Pin.OUT)
        self.test_led.off()
        
        # Class Vars
        self.network = Network()
        self.google = GoogleAPI()
        self.weather = OpenWeather()
        self.connect_network(loc)
        self.twitter = Twitter()

        # Timers
        self.location_timer = Timer(-1)
        #self.location_timer.init(period=5000, mode=Timer.PERIODIC, callback=self.location_cb)
        
        # LED
        self.led = Pin(Lab4.LED, Pin.OUT)

        # OLED
        self.i2c = I2C(scl=Pin(Lab4.SCL), sda=Pin(Lab4.SDA), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled_brightness = 0.5 
        self.oled_direction = 0
        self.ticks = 0
        
        # Buttons
        self.loc_button = Pin(Lab4.LOC_BUTTON, Pin.IN)
        self.loc_button_ts = time.ticks_ms()
        self.loc_button_pending = False

        self.oled_a = Pin(Lab4.OLED_A, Pin.IN)
        self.oled_a_ts = time.ticks_ms()
        self.oled_a_pending = False

        self.oled_b = Pin(Lab4.OLED_B, Pin.IN)
        self.oled_b_ts = time.ticks_ms()
        self.oled_b_pending = False
        
        self.oled_c = Pin(Lab4.OLED_C, Pin.IN)
        self.oled_c_ts = time.ticks_ms()
        self.oled_c_pending = False
        
        self.button_timer = Timer(1)
        self.button_timer.init(period=10, mode=Timer.PERIODIC,callback=self.button_cb)
 
        # Test LED 2
        self.test_led = Pin(Lab4.TEST_LED2, Pin.OUT)
        self.test_led.off()

        return

    def connect_network(self, loc):
        while self.network.sta_if.isconnected() == False:
            if loc == "home":
                self.network.connect(Lab4.HOME_SSID, Lab4.HOME_PASS)
            elif loc == "uni":
                self.network.connect()
        return

################## OLED ####################

    def print_text(self,text):
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

################## GEOLOCATE ####################
    
    def update_location(self):
        self.google.geolocate()
        print(self.google.location)
        
        lat = self.google.location["location"]["lat"]
        lng = self.google.location["location"]["lng"]

        text = "lat: {:.2f}lon: {:.2f}".format(lat, lng)
        self.print_text(text)
        return

################## WEATHER ####################

    def update_weather(self):
        self.google.geolocate()
        self.weather.get_current_weather(self.google.location)
        temp = self.weather.weather["main"]["temp"]
        desc = self.weather.weather["weather"][0]["main"]
        text = "Temp: {}F \nDesc: {}".format(temp, desc)
        print(text)
        self.print_text(text)
        return

################## TWITTER ####################

    def send_tweet(self):
        tweet = "The weather is great today!!"
        self.twitter.send_tweet(tweet)
        return

################## TIMERS ####################
    
    def button_cb(self, timer):
        t = time.ticks_ms()
        if self.loc_button.value() == 1 and (t - self.loc_button_ts) > Lab4.DEBOUNCE_TIME:
            self.loc_button_pending = True
            self.loc_button_ts = time.ticks_ms()
            self.update_location()
        if self.oled_a.value() == 0 and (t - self.oled_a_ts) > Lab4.DEBOUNCE_TIME:
            self.oled_a_ts = time.ticks_ms()
            self.update_weather()
        if self.oled_c.value() == 0 and (t - self.oled_c_ts) > Lab4.DEBOUNCE_TIME:
            self.oled_c_ts = time.ticks_ms()
            self.send_tweet()
        return

##############################################
##############################################
