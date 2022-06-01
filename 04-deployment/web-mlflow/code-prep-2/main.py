import os
import mlflow

from flask import Flask
from flask import request
from flask import jsonify

loaded_model = mlflow.pyfunc.load_model("./model/")

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