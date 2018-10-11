import network
import time
import socket
import urequests

HOME_SSID = "It hurts when IP"
HOME_PASS = "empirestate3"
COLUMBIA_SSID = "Columbia University"
DELAY = 3
TIMEOUT = 10

class Network:

    def __init__(self,loc):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        print("LOG: initialized Network class.")
        self.socket = socket.socket()
        if loc == "uni":
            self.connect(ssid=COLUMBIA_SSID, password="")
        elif loc == "home":
            self.connect(ssid=HOME_SSID, password=HOME_PASS)
        return

    def connect(self, ssid=COLUMBIA_SSID, password=""):
        while self.sta_if.isconnected() == False:
            self.sta_if.active(True)
            if ssid == COLUMBIA_SSID:
                self.sta_if.connect(ssid)
            else:
                self.sta_if.connect(ssid, password)
            t = time.ticks_ms() 
            while(self.sta_if.isconnected() == False):
                if (time.ticks_ms() - t > TIMEOUT*1000):
                    print("LOG: network connection timed out.")
                    break
                pass
            if self.sta_if.isconnected():
                print("LOG: connected to {0}.".format(ssid))
                print("LOG: ipconfig: {}".format(self.sta_if.ifconfig()))
                break
            else:
                print("ERROR: could not connect to {0}.".format(ssid))
        return

#################### TEST #######################

    def create_socket(self, host, port):
        print("LOG: connecting to {} on port {}.".format(host, port))
        addr_info = socket.getaddrinfo(host, port)
        ip = addr_info[0][-1]
        print("LOG: ip retrieved as {}.".format(ip))
        self.socket.connect(ip)
        print("LOG: created socket.")
        return

    def star_wars_test(self):
        host = "towel.blinkenlights.nl"
        port = 23
        self.create_socket(host, port)
        while True:
            data = self.socket.recv(500)
            print(str(data, 'utf8'), end="")
        self.socket.close()
        return

    def micropython_http_test(self):
        url = "http://micropython.org/ks/test.html"
        self.http_get(url)
        while True:
            data = self.socket.recv(100)
            if data:
                print(str(data, 'utf8'), end='')
            else:
                break
        self.socket.close()
        return

################################################
################################################
