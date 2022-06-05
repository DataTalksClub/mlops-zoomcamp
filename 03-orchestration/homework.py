import glob
import os
import pickle
import subprocess
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from prefect import flow, get_run_logger, task
from prefect.deployments import DeploymentSpec
from prefect.flow_runners import SubprocessFlowRunner
from prefect.orion.schemas.schedules import CronSchedule
from prefect.task_runners import SequentialTaskRunner
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

RETRIES = 2


def download_data(path=None, root_location=None, logger=None):
    """Function to download data"""

    download_url = f"https://nyc-tlc.s3.amazonaws.com/trip+data/{path}"
    logger.info(f"Downloading file from {download_url} to location {root_location}")
    subprocess.call(['wget', '-O', root_location + path, download_url])


@task(retries=RETRIES)
def get_paths(date:str = None):
    """
    Function to fetch training and vdalidation data
    file paths
    """

    file_path = "fhv_tripdata_{}.parquet"
    
    relative_date = ''
    if date is None:
        relative_date = datetime.now().date()
    else:
        relative_date = datetime.strptime(date, '%Y-%m-%d')

    relative_train_date = relative_date - relativedelta(months=2)
    relative_val_date = relative_date - relativedelta(months=1)

    train_data_year = relative_train_date.year
    train_data_month = relative_train_date.month
    val_data_year = relative_val_date.year
    val_data_month = relative_val_date.month

    train_year_month = datetime(train_data_year, train_data_month, 1).date().strftime('%Y-%m')
    val_year_month = datetime(val_data_year, val_data_month, 1).date().strftime('%Y-%m')

    train_file_path = file_path.format(train_year_month)
    val_file_path = file_path.format(val_year_month)

    return train_file_path, val_file_path


@task(retries=RETRIES)
def read_data(path, logger=None):
    """Function to read parquet file from path location"""

    root_file_path = "../data/"
    full_data_path = root_file_path + path

    if os.path.exists(full_data_path):
        df = pd.read_parquet(full_data_path)
    else:
        logger.info(f"No {full_data_path} exists, downloading file")
        download_data(path=path, root_location=root_file_path, logger=logger)
        df = pd.read_parquet(full_data_path)
    
    return df

@task(retries=RETRIES)
def get_latest_models(model_prefix="model", preprocessor_prefix="dv", file_extension=".bin", logger=None):
    """Function to fetch latest models sorted"""

    models = glob.glob(f"models/{model_prefix}*{file_extension}")
    preprocessors = glob.glob(f"models/{preprocessor_prefix}*{file_extension}")
    models.sort(reverse=True)
    preprocessors.sort(reverse=True)

    logger.info(f"Latest model is {models[0]}")
    logger.info(f"latest prerprocessor is {preprocessors[0]}")

    preprocessor_size = os.path.getsize(f'{preprocessors[0]}')
    model_size = os.path.getsize(f'{models[0]}')

    logger.info(f"Preprocessor size is {preprocessor_size} bytes")
    logger.info(f"Model size is {model_size} bytes")

    with open(models[0], "rb") as m_in:
        model = pickle.load(m_in)

    with open(preprocessors[0], "rb") as p_in:
        preprocessor = pickle.load(p_in)

    return model, preprocessor


@task(retries=RETRIES)
def prepare_features(df, categorical, train=True, logger=None):
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    mean_duration = df.duration.mean()
    if train:
        logger.info(f"The mean duration of training is {mean_duration}")
    else:
        logger.info(f"The mean duration of validation is {mean_duration}")
    
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df


@task(retries=RETRIES)
def train_model(df, categorical, date, file_extension=".bin", logger=None):

    train_dicts = df[categorical].to_dict(orient='records')
    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts) 
    y_train = df.duration.values

    logger.info(f"The shape of X_train is {X_train.shape}")
    logger.info(f"The DictVectorizer has {len(dv.feature_names_)} features")

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_train)
    mse = mean_squared_error(y_train, y_pred, squared=False)
    logger.info(f"The MSE of training is: {mse}")

    # Writing preprocessor file
    with open(f"models/dv-{date}{file_extension}", 'wb') as p_out:
        pickle.dump(dv, p_out)

    # Writing model file
    with open(f"models/model-{date}{file_extension}", 'wb') as m_out:
        pickle.dump(lr, m_out)


@task(retries=RETRIES)
def run_model(df, categorical, dv, lr, logger=None):
    val_dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(val_dicts) 
    y_pred = lr.predict(X_val)
    y_val = df.duration.values

    mse = mean_squared_error(y_val, y_pred, squared=False)
    logger.info(f"The MSE of validation is: {mse}")


@flow(name="newyork-taxi-model-flow", task_runner=SequentialTaskRunner())
def main(date:str = None):

    logger = get_run_logger()
    categorical = ['PUlocationID', 'DOlocationID']

    train_path, val_path = get_paths(date=date).result()

    df_train = read_data(train_path, logger=logger).result()
    df_train_processed = prepare_features(df_train, categorical, logger=logger).result()

    df_val = read_data(val_path, logger=logger).result()
    df_val_processed = prepare_features(df_val, categorical, train=False, logger=logger).result()

    # train the model
    train_model(df_train_processed, categorical, date=date, logger=logger)

    lr, dv = get_latest_models(logger=logger).result()
    run_model(df_val_processed, categorical, dv, lr, logger=logger)


DeploymentSpec(flow=main,
               schedule=CronSchedule(cron="0 9 15 * *"),
               name="model-training-homework-week-3",
               flow_runner=SubprocessFlowRunner(),
               tags=["ml"])
