// Absolute path?
lambda_function_local_path="../lambda_function.py"
docker_image_local_path="../Dockerfile"
ecr_repo_name="prod_stream_model_duration"
lambda_function_name="prod_prediction_lambda"
model_bucket="prod-mlflow-models"
source_stream_name="prod_ride_events"
output_kinesis_stream="prod_ride_predictions"
