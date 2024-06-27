import os
import pickle
import numpy as np

import mlflow
from flask import Flask, request, jsonify
from mlflow.tracking import MlflowClient

os.environ["AWS_PROFILE"] = "ArunG"

MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
RUN_ID = '9129b1c2b1ce401e9ab1d1d94a19249b'
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
# path = client.download_artifacts(run_id=RUN_ID, path='dict_vectorizer.bin')
# print(f'downloading the dict vectorizer to {path}')

# with open(path, 'rb') as f_out:
#     dv = pickle.load(f_out)


logged_model = f's3://mlflow-artifacts-gansi/1/{RUN_ID}/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
# model_dependencies = mlflow.pyfunc.get_model_dependencies(logged_model)
model = mlflow.pyfunc.load_model(logged_model)

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

def predict(features):
    # new_list = np.array(list(features.values())).reshape(1,-1)
    # print(new_list)
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
