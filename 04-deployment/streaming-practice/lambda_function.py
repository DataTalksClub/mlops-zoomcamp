import base64
import json
import logging
import os

import boto3
import mlflow


logging.basicConfig(level=logging.INFO)


STREAM_NAME = os.getenv("STREAM_NAME")
RUN_ID = os.getenv("RUN_ID")
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'
logged_model = f's3://mlops-zoomcamp-nakul/week-4-experiments/1/{RUN_ID}/artifacts/model'
stream_client = boto3.client('kinesis')

def send_to_stream(stream_name, data, partition_key=1):
    """Function to send data to another stream"""
    
    response = stream_client.put_record(
        StreamName=stream_name,
        Data=json.dumps(data),
        PartitionKey=str(partition_key)
        )
    logging.info(f"Success!. Response is {response}")

def prepare_features(ride):
    """Function to prepare features"""

    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

def predict(features):
    """Function to provide prediction"""

    model = mlflow.pyfunc.load_model(logged_model)
    prediction = model.predict(features)
    return prediction[0]

def lambda_handler(event, context):
    """Lambda handler to read data from some stream and write transformatio
        to another stream
    """
    
    predictions = []
    for record in event["Records"]:
        raw_data = record["kinesis"]["data"]
        decoded_event = base64.b64decode(raw_data).decode('utf-8')
        ride_event = json.loads(decoded_event)
        
        features = prepare_features(ride_event['ride'])
        predicted_duration = predict(features)
        
        prediction_event = {
            'model': 'ride_prediction_model',
            'version': RUN_ID,
            'prediction': {
                'ride_id' : ride_event["ride_id"],
                'prediction': predicted_duration
            }
        }
        
        if not TEST_RUN:
            send_to_stream(stream_name=STREAM_NAME, data=prediction_event, partition_key=ride_event["ride_id"])
        predictions.append(prediction_event)
        
        
    result = {'statusCode': 200, 'predictions': predictions}
    logging.info(f"payload: {result}")
    
    return result
