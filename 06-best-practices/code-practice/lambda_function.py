import os

from model import init

STREAM_NAME = os.getenv("STREAM_NAME")
RUN_ID = os.getenv("RUN_ID")
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'

model_service = init(run_id=RUN_ID,
                     prediction_stream_name=STREAM_NAME, 
                     test_run=TEST_RUN)


def lambda_handler(event, context):
    return model_service.lambda_handler(event=event)
