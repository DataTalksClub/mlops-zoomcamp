
import uuid
from datetime import datetime

import mlflow
import pandas as pd
from dateutil.relativedelta import relativedelta
from prefect import flow, get_run_logger, task
from prefect.context import get_run_context
from prefect.task_runners import SequentialTaskRunner

AWS_S3_BUCKET = "mlops-zoomcamp-nakul"
OBJECT_PATH = "week4-scoring"
categorical = ['PULocationID', 'DOLocationID']

def load_model(run_id=""): 
    """Load model to predict the ride"""

    logged_model = f's3://{AWS_S3_BUCKET}/week-4-experiments/1/{run_id}/artifacts/model'
    model = mlflow.pyfunc.load_model(logged_model)

    return model


def get_file_paths(year: int, month: int, run_id: str=""):
    """Get file path based on year and month"""

    input_file_path =  f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year:04d}-{month:02d}.parquet'
    output_file_path = f's3://{AWS_S3_BUCKET}/{OBJECT_PATH}/year={year:04d}/month={month:02d}/{run_id}.parquet'

    return input_file_path, output_file_path

@task
def read_data(filename):
    """Read parquet data"""
    
    logger = get_run_logger()
    df = pd.read_parquet(filename)
    logger.info(f"Read the filename {filename}")
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    df['ride_id'] = [str(uuid.uuid4()) for ride in range(0, df.shape[0])]
    
    return df

@task
def prepare_dictionaries(df: pd.DataFrame):
    """Preparing dictionaries"""

    df['PU_DO'] = df[categorical[0]] + '_' + df[categorical[1]]
    categorical_var = ['PU_DO']
    numerical_var = ['trip_distance']
    dicts = df[categorical_var + numerical_var].to_dict(orient='records')
    return dicts

@task
def score_rides(dicts: dict, run_id: str=""):
    """Scoring rides"""

    model = load_model(run_id=run_id)
    predictions = model.predict(dicts)

    return predictions

@task
def save_results(preds: list, rides: pd.DataFrame, run_id: str="", output_file: str=""):
    """Saving batched results"""

    df = rides.copy()
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = preds
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    df_result.to_parquet(output_file, index=False)

def get_year_month(date: datetime):
    """Get year month for scoring data"""

    relative_date = date - relativedelta(months=1)

    year = relative_date.year
    month = relative_date.month

    return year, month


@flow(name="newyork-taxi-model-flow", task_runner=SequentialTaskRunner())
def batch_score(date: datetime=None, run_id: str=""):
    """Run batch prediction and create local copy and upload to cloud"""
    
    run_date=''
    if date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time
    else:
        run_date = date

    logger = get_run_logger()
    year, month = get_year_month(date=run_date)
    logger.info(f"Year is {year} and month is {month} for scoring data")

    input_file_path, output_file_path = get_file_paths(year=year, month=month, run_id=run_id)
    logger.info(f"Data will be read from {input_file_path}")
    logger.info(f"Predictions will be written to {output_file_path}")

    rides_df = read_data(filename=input_file_path).result()
    logger.info("Data is read correctly")
    
    rides_dict = prepare_dictionaries(rides_df).result()
    logger.info("Data is prepared for scoring")

    predictions = score_rides(dicts=rides_dict, run_id=run_id).result()
    logger.info("Rides have been scored")
    save_results(preds=predictions, rides=rides_df, run_id=run_id, output_file=output_file_path)

    logger.info(f"Scoring completed and results written to {output_file_path}")


def run():
    year =  2021
    month = 3

    run_id = '20c7e3f3b3584b769bf6cacd4643d43d'

    batch_score(
        run_id=run_id,
        date=datetime(year=year, month=month, day=1)
    )

if __name__ == "__main__":
    run()
