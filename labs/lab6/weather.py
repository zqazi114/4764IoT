import urequests as requests

class OpenWeather:
    
    HOST = "http://api.openweathermap.org/"
    CUR_WEA = "data/2.5/"
    API_KEY = "&APPID=811382203d89cb442979b56c6056f713"

    def __init__(self):
        self.weather = {}
        self.loc = {}
        return

################## WEATHER ####################

    def get_current_weather(self, loc):
        self.loc = loc
        lat = loc["location"]["lat"]
        lon = loc["location"]["lng"]
        path = "weather?lat={}&lon={}".format(lat, lon)
        method = "GET"
        url = OpenWeather.HOST + OpenWeather.CUR_WEA + path + OpenWeather.API_KEY
        print("LOG: getting weather with url: {}".format(url))

        resp = requests.request(method, url)
        print("{} {}".format(resp.status_code, resp.reason))
        self.weather = resp.json()
        return

################################################
################################################
