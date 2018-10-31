#from mongo_http import Mongo_HTTP
from lab6 import Lab6

def main():
    loc = "home"
    l = Lab6(loc)
    mongo = 0#Mongo_HTTP()
    #mongo.write_test()
    #mongo.get_data_for_collection()
    #readings = np.random.random(10)
    #mongo.write_accel_to_db(readings)
    #guid = 'f20f810c-14d0-4b65-8a02-d4bbdcb4dedf'
    #mongo.get_accel_from_db(guid)

    return mongo

m = main()
