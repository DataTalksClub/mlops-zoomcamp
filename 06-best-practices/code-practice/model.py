import base64
import json
import logging
import os

import boto3
import mlflow

logging.basicConfig(level=logging.INFO)

# Retrieve the logger instance
logger = logging.getLogger()


def get_model_location(run_id: str = ""):
    """Function to get local or S3 model path"""

    model_path = os.getenv('MODEL_PATH')
    if model_path:
        return model_path
    else:
        bucket_name = os.getenv("MODEL_BUCKET", "mlops-zoomcamp-nakul")
        experiment_id = os.getenv("MODEL_EXPERIMENT", "1")
        model_path = (
            f"""s3://{bucket_name}/week-4-experiments/{experiment_id}/{run_id}/artifacts/model"""
        )
        return model_path


def load_model(run_id: str = ""):
    """Function to load mlflow model from location based on run id"""

    logged_model_path = get_model_location(run_id=run_id)
    model = mlflow.pyfunc.load_model(logged_model_path)
    return model


class ModelService:
    """Class to run model service"""

    def __init__(self, model=None, run_id: str = "", test_run: bool = True, callbacks=None):
        self.run_id = run_id
        self.model = model
        self.test_run = test_run
        self.callbacks = callbacks or []

    def prepare_features(self, ride):
        """Function to prepare features"""

        features = {}
        features['PU_DO'] = f"{ride['PULocationID']}_{ride['DOLocationID']}"
        features['trip_distance'] = ride['trip_distance']
        return features

    def decode_base64(self, raw_data: str = ""):
        """Function to decode base64 string"""

        decoded_event = base64.b64decode(raw_data).decode('utf-8')
        ride_event = json.loads(decoded_event)
        return ride_event

    def predict(self, features):
        """Function to provide prediction"""

        prediction = self.model.predict(features)
        return prediction[0]

    def lambda_handler(self, event):
        """Lambda handler to read data from some stream and write transformatio
        to another stream
        """

        predictions = []
        for record in event["Records"]:
            raw_data = record["kinesis"]["data"]

            ride_event = self.decode_base64(raw_data=raw_data)
            features = self.prepare_features(ride=ride_event["ride"])
            predicted_duration = self.predict(features)

            prediction_event = {
                'model': 'ride_prediction_model',
                'version': self.run_id,
                'prediction': {'ride_id': ride_event["ride_id"], 'prediction': predicted_duration},
            }

            for callback in self.callbacks:
                callback(prediction_event)

            predictions.append(prediction_event)

        result = {'statusCode': 200, 'predictions': predictions}
        logger.info("payload %s", result)

        return result


class KinesisRideCallBack:
    """Kinesis callback class to add to handler when running in prod"""

    def __init__(self, client, stream_name: str = None):
        self.kinesis_client = client
        self.stream_name = stream_name

    def put_record(self, prediction_event: dict = None):
        """This method is used to insert data in streams"""

        ride_id = prediction_event['prediction']['ride_id']
        self.kinesis_client.put_record(
            StreamName=self.stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id),
        )


def create_kinesis_client():
    """Function to provide kinesis client"""

    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')
    if endpoint_url is None:
        return boto3.client('kinesis')
    else:
        return boto3.client('kinesis', endpoint_url=endpoint_url)


def init(run_id: str = "", prediction_stream_name: str = "", test_run: bool = True):
    """Service to be deployed with lambda handler"""

    model = load_model(run_id=run_id)
    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisRideCallBack(
            client=kinesis_client, stream_name=prediction_stream_name
        )
        callbacks.append(kinesis_callback.put_record)

    model_service = ModelService(model=model, run_id=run_id, test_run=test_run, callbacks=callbacks)
    return model_service
