import os
import pickle

from flask import Flask
from flask import request
from flask import jsonify


MODEL_FILE = os.getenv('MODEL_FILE', 'lin_reg.bin')

with open(MODEL_FILE, 'rb') as f_in:
    dv, model = pickle.load(f_in)


app = Flask('duration')

@app.route('/predict', methods=['POST'])
def predict():
    record = request.get_json()

    record['PU_DO'] = '%s_%s' % (record['PULocationID'], record['DOLocationID'])

    X = dv.transform([record])
    y_pred = model.predict(X)

    result = {
        'duration': float(y_pred),
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)