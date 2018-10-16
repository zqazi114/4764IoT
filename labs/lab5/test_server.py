import socket

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

class Server:

    # Commands
    CLOCK = "clock"
    DISP = "display"
    MSG = "message"

############################################
    def __init__(self, loc="uni", ip=DEFAULTIP):
        
        # Server
        self.addr = socket.getaddrinfo(ip, 80)[0][-1]
        self.socket = socket.socket()
        
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
        return True

############################################
    def stop_server(self):
        self.socket.close()
        return

############################################
############################################
############################################

s = Server()
s.listen()