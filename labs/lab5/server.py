from machine import Pin, PWM, I2C, Timer, RTC
from iotnetwork import Network
import ssd1306
import socket
import time

# Pin definitions
TEST_LED = 0
TEST_LED2 = 2
LED = 14
SDA = 4
SCL = 5

# I2C Addresses
OLED_ADDR = 0x3f

# HTTP stuff
DEFAULTIP = '0.0.0.0'
RESPOK = """<!DOCTYPE html>
<html>
    <head> <title>ACK</title> </head>
</html>
"""
RESPBAD = """<!DOCTYPE html>
<html>
    <head> <title>NACK</title> </head>
</html>
"""

DELAY = 100

class Server:

    # Commands
    CLOCK = "clock"
    DISP = "display"
    MSG = "message"

############################################
    def __init__(self, loc="uni", ip=DEFAULTIP):
        
        #LED
        self.freq = 1
        self.duty = 512
        self.led = PWM(Pin(LED),freq=self.freq,duty=self.duty)

        # OLED
        self.i2c = I2C(scl=Pin(SCL), sda=Pin(SDA), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.display = True

        # RTC
        self.rtc = RTC()
        date = [2018, 11, 14, 0, 0, 0, 0, 0]
        self.rtc.datetime(date)
        self.clock_timer = Timer(2)
        self.clock_timer.init(period=1000, mode=Timer.PERIODIC, callback=self.clock_cb)

        # Network
        self.network = Network(loc)

        # Server
        self.addr = socket.getaddrinfo(ip, 80)[0][-1]
        self.socket = socket.socket()
        
        # test LED
        self.test_led = Pin(TEST_LED, Pin.OUT)
        self.test_led.off()
        
        return
    
    def clock_cb(self, timer):
        if self.display:
            self.oled.fill(0)
            self.oled.show()
            date = self.rtc.datetime()
            dateStr = "{}/{:02d}".format(date[1], date[2])
            timeStr = "{:02d}:{:02d}:{:02d}:{:02d}".format(date[3], date[4], date[5], date[6])
            self.oled.text(dateStr + " " + timeStr, 0, 20, 1)
            self.oled.show()
        else:
            self.oled.fill(0)
            self.oled.show()
        return

    def print_text(self,text):
        self.oled.fill(0)
        self.oled.show()
        for i in range(len(text)):
            t = text[:i+1]
            self.oled.text(t, 0, 0)
            self.oled.show()
            time.sleep_ms(DELAY)
        return

############################################
    def listen_once(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.listen(1)
        print('LOG: listening on', self.addr)

        cl, addr = self.socket.accept()
        print('LOG: client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            sline = str(line)
            if 'HTTP' in sline and 'esp8266' in sline:
                path = sline.split(' ')
                path = path[1].split('/', 2)
                path = path[2].split('&')
                command = path[0]
                parameters = path[1]
            if not line or line == b'\r\n':
                break
        processed = self.process_request(command, parameters)
        if processed:
            response = RESPOK
        else:
            response = RESPBAD
        cl.send(str.encode(response))
        cl.close()
        self.stop_server() 
        return

############################################
    def listen(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.listen(1)
        print('LOG: listening on', self.addr)

        while True:
            cl, addr = self.socket.accept()
            print('LOG: client connected from', addr)
            cl_file = cl.makefile('rwb', 0)
            while True:
                line = cl_file.readline()
                sline = str(line)
                if 'HTTP' in sline and 'esp8266' in sline:
                    path = sline.split(' ')
                    path = path[1].split('/', 2)
                    path = path[2].split('&')
                    command = path[0]
                    parameters = path[1]
                if not line or line == b'\r\n':
                    break
            processed = self.process_request(command, parameters)
            if processed:
                response = RESPOK
            else:
                response = RESPBAD
            cl.send(str.encode(response))
            cl.close()
        self.stop_server() 
        return


############################################
    def process_request(self, c, p):
        print("LOG: received command: {}, param: {}".format(c, p))
        if c == Server.CLOCK:
            on = p.split('=')[1]
            self.show_clock(on)
        elif c == Server.DISP:
            on = p.split('=')[1]
            self.show_display(on)
        elif c == Server.MSG:
            msg = p.split('=')[1]
            self.show_message(msg)
        else:
            print("ERROR: unrecognized command received")
            return False
        return True

############################################
    def show_clock(self, on):
        print("LOG: showing clock {}".format(on))
        return

    def show_display(self, on):
        print("LOG: showing display {}".format(on))
        if on == 'on':
            self.display = True
        elif on == 'off':
            self.display = False
        return

    def show_message(self, msg):
        print("LOG: showing message {}".format(msg))
        self.print_text(msg)
        return

############################################
    def stop_server(self):
        self.socket.close()
        return

############################################
############################################
############################################
