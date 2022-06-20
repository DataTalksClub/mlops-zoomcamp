import os

import mlflow
from flask import Flask, jsonify, request

RUN_ID = os.getenv('RUN_ID')

# Uncomment below two lines if model not stored on s3
# MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
# client = mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

logged_model = f's3://mlops-zoomcamp-nakul/week-4-experiments/1/{RUN_ID}/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
