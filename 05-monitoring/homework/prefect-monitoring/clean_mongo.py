from pymongo import MongoClient

MONGO_CLIENT_ADDRESS = "mongodb://localhost:27017/"
MONGO_DATABASE = "prediction_service"


if __name__ == "__main__":
    client = MongoClient(MONGO_CLIENT_ADDRESS)
    client.drop_database(MONGO_DATABASE)
