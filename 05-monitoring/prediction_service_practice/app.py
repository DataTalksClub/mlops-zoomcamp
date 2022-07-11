import logging
import os
import uuid

import mlflow
import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient

RUN_ID = os.getenv("RUN_ID")
BUCKET_ID = os.getenv("BUCKET_ID")
MONGO_ADDRESS = os.getenv("MONGO_ADDRESS", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "ride_prediction")
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'

EVIDENTLY_SERVICE_ADDRESS = os.getenv("EVIDENTLY_SERVICE_ADDRESS", "http://127.0.0.1:5001")
LOGGED_MODEL = f's3://{BUCKET_ID}/week-4-experiments/1/{RUN_ID}/artifacts/model'


model = mlflow.pyfunc.load_model(LOGGED_MODEL)
mongo_client = MongoClient(MONGO_ADDRESS)
mongo_db = mongo_client[MONGO_DATABASE]
mongo_collection = mongo_db['ride_prediction_collection']



app = Flask("Ride-Prediction-Service")
logging.basicConfig(level=logging.INFO)


def prepare_features(ride):
    """Function to prepare features before making prediction"""

    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def save_db(pred_result: dict):
    """Save data to mongo db collection"""

    result = pred_result.copy()

    mongo_collection.insert_one(result)


def send_to_evidently(record: dict):
    """Save data to evidently to detect model drift"""

    rec = record.copy()
    requests.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/taxi", json=[rec])


@app.route("/", methods=["GET"])
def get_info():
    """Function to provide info about the app"""
    info = """<H1>Ride Prediction Service</H1>
              <div class="Data Request"> 
                <H3>Data Request Example</H3> 
                <div class="data">
                <p> "ride = {
                    "PULocationID": 10,
                    "DOLocationID": 50,
                    "trip_distance": 40
                    }"
                </p>
                </div>    
               </div>"""
    return info

@app.route("/predict-duration", methods=["POST"])
def predict_duration():
    """Function to predict duration"""

    data = request.get_json()
    features = prepare_features(data)
    prediction = model.predict(features)
    ride_id = str(uuid.uuid4())
    pred_data = {
            "ride_id": ride_id,
            "PU_DO": features["PU_DO"],
            "trip_distance": features["trip_distance"],
            "status": 200,
            "duration": prediction[0],
            "model_version": RUN_ID
            }

    save_db(pred_result=pred_data)
    try:
        send_to_evidently(record=pred_data)
    except Exception as e:
        app.logger.info(f"Could not log to evidently due to {e}")

    result = {
        "statusCode": 200,
        "data" : pred_data
        }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
