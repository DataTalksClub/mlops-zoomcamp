import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression

from sklearn.metrics import mean_squared_error

from prefect import flow, task, get_run_logger

@task
def read_data(path):
    df = pd.read_parquet(path)
    return df

@task
def prepare_features(df, categorical):
    logger = get_run_logger()
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    logger.info(df.duration.mean())
    
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

@task
def train_model(df, categorical):
    logger = get_run_logger()
    train_dicts = df[categorical].to_dict(orient='records')
    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts) 
    logger.info(X_train.shape)
    y_train = df.duration.values
    logger.info(len(dv.feature_names_))
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_train)
    logger.info(mean_squared_error(y_train, y_pred, squared=False))
    return lr, dv

@task
def run_model(df, categorical, dv, lr):
    val_dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(val_dicts) 
    y_pred = lr.predict(X_val)
    y_val = df.duration.values
    mean_squared_error(y_val, y_pred, squared=False)
    return dv

@flow
def myflow(train_path: str = './data/fhv_tripdata_2021-01.parquet', 
             val_path: str = './data/fhv_tripdata_2021-02.parquet'):

    categorical = ['PUlocationID', 'DOlocationID']
    df_train = read_data(train_path)
    df_processed = prepare_features(df_train, categorical)
    lr, dv = train_model(df_processed, categorical).result()
    df_val = read_data(val_path)
    df_val_processed = prepare_features(df_val, categorical)
    run_model(df_val_processed, categorical, dv, lr)

myflow()
