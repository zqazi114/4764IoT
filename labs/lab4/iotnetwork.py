import network
import time
import socket
import urequests

COLUMBIA_SSID = "Columbia University"
DELAY = 3
TIMEOUT = 10

class Network:

    def __init__(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        print("LOG: initialized Network class.")
        self.socket = socket.socket()
        
        return

    def connect(self, ssid=COLUMBIA_SSID, password=""):
        if self.sta_if.isconnected():
            print("LOG: already connected.")
        else:
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
            else:
                print("ERROR: could not connect to {0}.".format(ssid))
                #self.sta_if.active(False)
        return

    def create_socket(self, host, port):
        print("LOG: connecting to {} on port {}.".format(host, port))
        addr_info = socket.getaddrinfo(host, port)
        ip = addr_info[0][-1]
        print("LOG: ip retrieved as {}.".format(ip))
        self.socket.connect(ip)
        print("LOG: created socket.")
        return

#################### TEST #######################

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
                #print("ERROR: could not GET from {}".format(url))
                break
        self.socket.close()
        return
        

#################### HTTP #######################

    def http_get(self, host, path):
        self.create_socket(host, 80)
        cmd = bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8')
        print("LOG: sending {} to {}".format(cmd, url))
        self.socket.send(bytes(cmd))

        return
    
    def http_get(self, url):
        _, _, host, path = url.split('/', 3)
        self.create_socket(host, 80)

        cmd = bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8')
        print("LOG: {}.".format(cmd))
        self.socket.send(bytes(cmd))

        return

    def http_post(self, url):
        _, _, host, path = url.split('/', 3)
        self.create_socket(host, 80)

        cmd = bytes('POST /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8')
        print("LOG: {}.".format(cmd))
        self.socket.send(bytes(cmd))

        return

################################################
################################################
