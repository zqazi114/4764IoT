from pymongo import MongoClient
import datetime
import pprint
import numpy as np

COLUMBIA = ["C", "O", "L", "U", "M", "B", "I", "A"]

class Mongo:

    # Constants
    ip = '34.224.78.191'#'127.0.0.1'
    port = '27017'
    user = 'esp8266'
    pwd = 'esp8266'
    dbName = 'esp8266_db'
    collName = 'accel_data'
    
######################## MONGO #############################
    def __init__(self, name='esp8266_db'):
        self.uri = 'mongodb://' + Mongo.user + ':' + Mongo.pwd + '@' + Mongo.ip + '/' + Mongo.dbName
        print("LOG: connecting to {} with uri {}".format(name, self.uri))
        self.client = MongoClient(self.uri)
        self.db = self.client[name]
        self.collection = self.db[Mongo.dbName]
        print("LOG: connected to MongoDB at {}".format(Mongo.ip))
        print("LOG: databases {}".format(self.client.database_names()))
        return
        
    def write_test(self):
        post = {"author" : "Zain",
                        "content" : "Hi botch",
                        "tags" : ["mongodb", "python", "tutorial"],
                        "date" : datetime.datetime.utcnow()
                        }
        
        posts = self.db[Mongo.collName]
        post_id = posts.insert_one(post).inserted_id
        
        print("LOG: created post with id {}".format(post_id))
        
        return
        
######################## ACCEL #############################
    def write_accel_to_db(self, guid, char, X, Y, Z):
        coll = self.db[Mongo.collName]
        for i in range(len(X)):
                doc = { "guid" : guid,
                        "character" : char,
                        "x" : X[i], 
                        "y" : Y[i], 
                        "z" : Z[i], 
                      }
                doc_id = coll.insert_one(doc).inserted_id
        print("LOG: added {} readings for character {} with id {}".format(len(X), char, doc_id))
        
        return
        
    def get_accel_from_db(self, char="C"):
        coll = self.db[Mongo.collName]
        guids = coll.distinct('guid')
        data = []
        for guid in guids:
            docs = coll.find({'guid' : guid, 'character' : char})
            x = []
            y = []
            z = []
            for doc in docs:
                x.append(int(doc['x']))
                y.append(int(doc['y']))
                z.append(int(doc['z']))
            if len(x) > 0:
                data.append([x,y,z])
        return data
        
############################################################
############################################################
