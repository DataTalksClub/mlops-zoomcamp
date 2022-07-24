from model import ModelService

RUN_ID = "Test123"
# STREAM_NAME = "TestStream"

model_service = ModelService(run_id=RUN_ID)


def test_features():
    """Function to test feature transformation"""

    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66,
    }

    output_result = model_service.prepare_features(ride=ride)

    expected_result = {"PU_DO": "130_205", "trip_distance": 3.66}

    assert output_result == expected_result


def test_base64_decode():
    """Function to test base64 decoding"""

    ride_event = {
        "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ=="
    }
    raw_ride_data = ride_event["data"]

    output_result = model_service.decode_base64(raw_ride_data)

    expected_result = {
        'ride': {'DOLocationID': 205, 'PULocationID': 130, 'trip_distance': 3.66},
        'ride_id': 256,
    }

    assert output_result == expected_result


class MockModel:
    """Mock class for model prediction method"""

    def __init__(self, val: float = 10):
        self.val = val

    def predict(self, ride):
        """Mock predict function to overwrite existing function"""

        num_rows = len([ride])
        return [self.val] * num_rows


def test_predict():
    """Test function to test predict method"""

    model = MockModel(10)
    ride = {"PU_DO": "130_205", "trip_distance": 3.66}

    model_service = ModelService(model=model)

    output_prediction = model_service.predict(ride)
    expected_prediction = 10.0
    assert output_prediction == expected_prediction


def test_lambda():
    """Test function to test lambda funtion"""

    event = {
        "Records": [
            {
                "kinesis": {
                    "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ==",
                },
            }
        ]
    }

    model = MockModel(11)
    model_service = ModelService(model=model, run_id=RUN_ID)

    event_output = model_service.lambda_handler(event=event)

    expected_output = {
        'statusCode': 200,
        'predictions': [
            {
                'model': 'ride_prediction_model',
                'version': RUN_ID,
                'prediction': {'ride_id': 256, 'prediction': 11},
            }
        ],
    }

    assert event_output == expected_output
