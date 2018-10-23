import urequests as requests
#from urlencoder import urlencode

class Twitter:

    HOST = "http://api.thingspeak.com/apps/"
    PATH = "thingtweet/1/statuses/update"
    API_KEY = "NUUNJ5VJ7F3DOBLK"

    def __init__(self):
         
        return

################## TWEET ####################

    def send_tweet(self, text):
        print("LOG: sending tweet: {}".format(text))
        method = "POST"
        url = Twitter.HOST + Twitter.PATH
        data = {'api_key' : Twitter.API_KEY ,'status' : text}
        data = urlencode(data)
        #headers = { 'X-THINGSPEAKAPIKEY' : Twitter.API_KEY,
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        print("LOG: twitter url: {}".format(url))
        resp = requests.request(method, url, headers=headers, data=data)
        print("LOG: Twitter status: {}".format(resp.status_code))
        return

################################################
################################################
