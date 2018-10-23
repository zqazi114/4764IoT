import socket
import time
import uuid
from mongodb import Mongo

# HTTP stuff
DEFAULTIP = '0.0.0.0'
DEFAULTPORT = 80

HTTPOK = """HTTP/1.1 200 OK\n
Content-Type: text/html\n
\n
<html><body>ACK</body></html>\n"""

HTTPBAD = """HTTP/1.1 414 NACK\n
Content-Type: text/html\n
\n
<html><body>NACK</body></html>\n"""

DELAY = 100

class Server:
    # Commands
    CLOCK = "clock"
    DISP = "display"
    MSG = "message"
    ACCELSTART = "accelstart"
    ACCELDATA = "acceldata"
    ACCELSTOP = "accelstop"

    MAXREADINGS = 100

############################################
    def __init__(self, ip=DEFAULTIP, port=DEFAULTPORT):
        
        # Server
        self.addr = socket.getaddrinfo(ip, port)[0][-1]
        self.socket = socket.socket()
       
        # Mongo
        self.mongo = Mongo()
        self.char = ""
        self.readings_x = []
        self.readings_y = []
        self.readings_z = []
        self.guid = ""

        return
    
################## SERVER ####################
    def listen_once(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.listen(1)
        print('LOG: listening once on', self.addr)

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
            response = HTTPOK
        else:
            response = HTTPBAD
        cl.send(str.encode(response))
        cl.close()
        self.stop_server() 
        return

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
                response = HTTPOK
            else:
                response = HTTPBAD
            cl.send(str.encode(response))
            cl.close()
        self.stop_server() 
        return


################## PROCESS ####################
    def process_request(self, c, p):
        print("LOG: received command: {}, param: {}".format(c, p))
        if c == Server.CLOCK:
            on = p.split('=')[1]
            print("LOG: received {} - {}".format(c, on))
        elif c == Server.DISP:
            on = p.split('=')[1]
            print("LOG: received {} - {}".format(c, on))
        elif c == Server.MSG:
            msg = p.split('=')[1]
            print("LOG: received {} - {}".format(c, msg))
        elif c == Server.ACCELSTART:
            char = p.split('=')[1]
            print("LOG: received {} - {}".format(c, char))
            self.start_storing_data(char)
        elif c == Server.ACCELDATA:
            val = p.split('=')[1]
            print("LOG: received {} {}".format(c, val))
            self.write_to_mongo(val)
        elif c == Server.ACCELSTOP:
            char = p.split('=')[1]
            print("LOG: received {} - {}".format(c, char))
            self.stop_storing_data(char)
        else:
            print("ERROR: unrecognized command received")
            return False
        return True

    def stop_server(self):
        print("LOG: Stopping server.")
        self.socket.close()
        return

################### MONGO ####################
    def start_storing_data(self, char):
        self.guid = str(uuid.uuid4())
        self.char = char
        print("LOG: starting to store char-{} under guid-{}".format(self.char, self.guid))
        return

    def write_to_mongo(self, val):
        x,y,z = val.split(',')
        self.readings_x.append(x)
        self.readings_y.append(y)
        self.readings_z.append(z)
        if len(self.readings_x) >= Server.MAXREADINGS:
            self.mongo.write_accel_to_db(self.guid, self.char, self.readings_x, self.readings_y, self.readings_z)
            self.readings_x = []
            self.readings_y = []
            self.readings_z = []
        return

    def stop_storing_data(self, char):
        self.mongo.write_accel_to_db(self.guid, self.char, self.readings_x, self.readings_y, self.readings_z)
        self.readings_x = []
        self.readings_y = []
        self.readings_z = []
        self.guid = ""
        self.char = ""
        print("LOG: stopping storing data")
        return

############################################
############################################

s = Server()
s.listen()
