import os
import pprint
from pymongo import MongoClient

import requests

MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27017/")
FLASK_URL = "http://127.0.0.1:9696/predict-duration"


mongo_client = MongoClient(MONGODB_ADDRESS)
mongo_db = mongo_client['prediction_service']
mongo_collection = mongo_db['data']
ride_test_data = {
    "PULocationID": 10, 
    "DOLocationID": 50,
    "trip_distance": 40
    }


if __name__ == "__main__":
    requests.post(url=FLASK_URL ,json=ride_test_data)
    for coll in mongo_collection.find():
        pprint.pprint(coll)
    