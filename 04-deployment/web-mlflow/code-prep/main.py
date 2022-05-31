import os
import mlflow

from flask import Flask
from flask import request
from flask import jsonify


MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_RUN_ID = os.getenv('MODEL_RUN_ID')
logged_model = f'runs:/{MODEL_RUN_ID}/model'
loaded_model = mlflow.pyfunc.load_model(logged_model)

app = Flask('duration')

@app.route('/predict', methods=['POST'])
def predict():
    record = request.get_json()

    record['PU_DO'] = '%s_%s' % (record['PULocationID'], record['DOLocationID'])

    y_pred = loaded_model.predict(record)

    result = {
        'duration': float(y_pred),
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)