from server import Server

def main():
    ip = '127.0.0.1'
    loc = "home"
    server = Server(loc=loc)
    #server.listen()
    return server

s = main()
