import urequests as requests
#import urlencode

class Twitter:

    HOST = "https://api.thingspeak.com/apps/"
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
        #data = urlencode(data)
        headers = { 'X-THINGSPEAKAPIKEY' : Twitter.API_KEY,
                    'Host' : 'api.thingspeak.com',
                    'Content-Type' : 'application/json',
                    'Content-Length' : 240}
        print("LOG: twitter url: {}".format(url))
        print(headers)
        resp = requests.request(method, url, headers=headers, data=data)
        print("LOG: Twitter status: {}".format(resp.status_code))
        return

################################################
################################################
