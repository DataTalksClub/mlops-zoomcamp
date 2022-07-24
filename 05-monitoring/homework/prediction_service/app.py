import logging
import os
import pickle
import uuid

from flask import Flask, jsonify, request
from pymongo import MongoClient


MONGO_ADDRESS = os.getenv("MONGO_ADDRESS", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "ride_prediction")
LOGGED_MODEL = os.getenv("MODEL_FILE", "lin_reg.bin")
MODEL_VERSION = os.getenv("MODEL_VERSION", "1")

with open(LOGGED_MODEL, 'rb') as f_in:
    dv, model = pickle.load(f_in)


mongo_client = MongoClient(MONGO_ADDRESS)
mongo_db = mongo_client[MONGO_DATABASE]
mongo_collection = mongo_db.get_collection("data")


app = Flask("Ride-Prediction-Service")
logging.basicConfig(level=logging.INFO)


def prepare_features(ride):
    """Function to prepare features before making prediction"""

    record = ride.copy()
    record['PU_DO'] = '%s_%s' % (record['PULocationID'], record['DOLocationID'])

    features = dv.transform([record])
   
    return features, record


def save_db(record, pred_result):
    """Save data to mongo db collection"""

    rec = record.copy()
    rec["prediction"] = pred_result[0]
    mongo_collection.insert_one(rec)



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

    ride = request.get_json()
    features, record = prepare_features(ride)

    prediction = model.predict(features)
    ride_id = str(uuid.uuid4())
    pred_data = {
            "ride_id": ride_id,
            "PU_DO": record["PU_DO"],
            "trip_distance": record["trip_distance"],
            "status": 200,
            "duration": prediction[0],
            "model_version": MODEL_VERSION
            }

    save_db(record, prediction)

    result = {
        "statusCode": 200,
        "data" : pred_data
        }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
