from model import ModelService

RUN_ID = "Test123"
#STREAM_NAME = "TestStream"

model_service = ModelService(run_id=RUN_ID)


def test_features():
    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66,
    }

    output_result = model_service.prepare_features(ride=ride)

    expected_result = {
        "PU_DO" : "130_205",
        "trip_distance": 3.66
    }

    assert output_result == expected_result


def test_base64_decode():
    ride_event = {"data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ=="}
    raw_ride_data = ride_event["data"]

    output_result = model_service.decode_base64(raw_ride_data)

    expected_result = {'ride' : {'DOLocationID': 205,
                                 'PULocationID': 130,
                                 'trip_distance': 3.66
                                 },
                                 'ride_id': 256
                      }

    assert output_result == expected_result 


class MockModel(ModelService):

    def __init__(self, val: float=10):
        self.val = val

    def predict(self, ride):
        n = len([ride])
        return [self.val]*n


def test_predict():

    model = MockModel(10)
    ride = {
        "PU_DO" : "130_205",
        "trip_distance": 3.66
    }

    model_service = ModelService(model=model)

    output_prediction = model_service.predict(ride)
    expected_prediction = 10.0
    assert output_prediction == expected_prediction


def test_lambda():

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
        'predictions': [{
            'model': 'ride_prediction_model',
                'version': RUN_ID,
                'prediction': {
                    'ride_id' : 256,
                    'prediction': 11
                }
        }]
    }

    assert event_output == expected_output

