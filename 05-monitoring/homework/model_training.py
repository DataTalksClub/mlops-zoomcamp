import pickle

import pandas as pd
import pyarrow.parquet as pq
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression


def read_dataframe(filename):
    df = pq.read_table(filename).to_pandas()

    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    return df

def add_features(train_data="./datasets/green_tripdata_2021-03.parquet",
                 additional_training_data=None):
    df_train = read_dataframe(train_data)

    if additional_training_data:
        extra_data = read_dataframe(additional_training_data)
        df_train = pd.concat([df_train, extra_data], axis=0, ignore_index=True)



    df_train['PU_DO'] = df_train['PULocationID'] + '_' + df_train['DOLocationID']

    categorical = ['PU_DO'] 
    numerical = ['trip_distance']

    dv = DictVectorizer()

    train_dicts = df_train[categorical + numerical].to_dict(orient='records')
    X_train = dv.fit_transform(train_dicts)

    target = 'duration'
    y_train = df_train[target].values

    return X_train, y_train, dv




if __name__ == "__main__":
    X_train, y_train, dv = add_features()
    
    print("Training model with one month of data")
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    
    with open('prediction_service/lin_reg.bin', 'wb') as f_out:
        pickle.dump((dv, lr), f_out)

    X_train, y_train, dv = add_features(additional_training_data="./datasets/green_tripdata_2021-04.parquet")
    print("Training model with two months of data")
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    with open('prediction_service/lin_reg_V2.bin', 'wb') as f_out:
        pickle.dump((dv, lr), f_out)
