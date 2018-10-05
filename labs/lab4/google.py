import urequests as requests

class GoogleAPI:

    HOST = "https://www.googleapis.com"
    GEOLOC = "/geolocation/v1/geolocate?key="
    API_KEY = "AIzaSyARiGoZmSd90XRbYXo8ek3GBK1Tn3E2r-w"

    def __init__(self):
        self.location = {}
        return

################## GEOLOCATE ####################

    def geolocate(self):
        url = GoogleAPI.HOST + GoogleAPI.GEOLOC + GoogleAPI.API_KEY
        method = "POST"
        headers = { 'Host' : 'www.googleapis.com',
                    'Content-Type' : 'application/json',
                    'Content-Length' : '0',
                  }
        print("LOG: geolocating with url: {}".format(url))

        resp = requests.request(method, url, headers=headers)
        print("{} {}".format(resp.status_code, resp.reason))
        self.location = resp.json()
        return

################################################
################################################
