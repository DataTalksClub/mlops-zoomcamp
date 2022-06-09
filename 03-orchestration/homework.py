import pandas as pd
import datetime as dt
import pickle

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from prefect import flow, task, get_run_logger
from prefect.task_runners import SequentialTaskRunner

@task
def read_data(path):
    df = pd.read_parquet(path)
    return df

@task
def prepare_features(df, categorical, train=True):
    logger = get_run_logger()

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

@task
def train_model(df, categorical):
    logger = get_run_logger()

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
    return lr, dv

@task
def run_model(df, categorical, dv, lr):
    logger = get_run_logger()

    val_dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(val_dicts) 
    y_pred = lr.predict(X_val)
    y_val = df.duration.values

    mse = mean_squared_error(y_val, y_pred, squared=False)
    logger.info(f"The MSE of validation is: {mse}")
    return

def get_pre_month(dt_date):
    month, year = (dt_date.month -1, dt_date.year) if dt_date.month != 1 else (12, dt_date.year-1)
    pre_month = dt_date.replace(day=1,month = month, year = year)
    return pre_month
    
@task
def get_paths(date:str):
    logger = get_run_logger()

    if date is None:
        date = f'{dt.date.today():%Y-%m-%d}'
    else:
        try:
            dt.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.info(f"Incorrect date format {date}, should be YYYY-MM-DD")
            
     
    dt_date = dt.datetime.strptime(date, '%Y-%m-%d')
    
    val_month = get_pre_month(dt_date)
    train_month = get_pre_month(val_month)
    
    #convert to strings

    val_month = val_month.strftime("%Y-%m")
    train_month = train_month.strftime("%Y-%m")
    
    val_path = "./data/fhv_tripdata_" + val_month + ".parquet"
    train_path = "./data/fhv_tripdata_" + train_month + ".parquet"

    logger.info(f"Train path: {train_path}")
    logger.info(f"Val path: {val_path}")
    
    return train_path, val_path
    
@flow(task_runner=SequentialTaskRunner())
def main(date="2021-08-15"):

    categorical = ['PUlocationID', 'DOlocationID']

    train_path, val_path = get_paths(date).result()

    df_train = read_data(train_path)
    df_train_processed = prepare_features(df_train, categorical).result()

    df_val = read_data(val_path)
    df_val_processed = prepare_features(df_val, categorical, False).result()

    # train the model
    lr, dv = train_model(df_train_processed, categorical).result()

    #save the models
    model_file = f"./models/model-{date}.bin"
    dv_file = f"./models/dv-{date}.b"

    with open(model_file, "wb") as f_out:
        pickle.dump(lr, f_out)

    with open(dv_file, "wb") as f_out:
        pickle.dump(dv, f_out)


    run_model(df_val_processed, categorical, dv, lr)

from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner

DeploymentSpec(
  flow=main,
  name="momdel_training",
  schedule=CronSchedule(
        cron="0 9 15 * *",
        timezone="America/New_York"),
  flow_runner=SubprocessFlowRunner(),
  tags=["ml"]
)

