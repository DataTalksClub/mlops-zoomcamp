export AWS_REGION="eu-west-1"
export PREDICTIONS_STREAM_NAME="ride_predictions_mlops-zoomcamp"  # can be dynamically retrieved in ci/cd
export MODEL_BUCKET_DEV="mlflow-models-alexey"
export MODEL_BUCKET_PROD="mlflow-models-mlops-zoomcamp"           # can be dynamically retrieved in ci/cd
# In practice, this is generally picked up from a tool like MLflow or a DB
export RUNID="e1efc53e9bd149078b0c12aeaa6365df"
export LAMBDA_FUNCTION="prediction_lambda_mlops-zoomcamp"         # can be dynamically retrieved in ci/cd


# Copy Model artifacts to newly created bucket
aws s3 sync s3://${MODEL_BUCKET_DEV} s3://${MODEL_BUCKET_PROD}


# Set new var RUN_ID in existing set of vars.
variables="{PREDICTIONS_STREAM_NAME=${PREDICTIONS_STREAM_NAME}, MODEL_BUCKET=${MODEL_BUCKET_PROD}, RUN_ID=${RUN_ID}}"

# https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} --environment "Variables=${variables}"
