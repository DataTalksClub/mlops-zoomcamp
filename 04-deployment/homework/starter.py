import argparse
import logging
import pickle

import pandas as pd

#Initialing the logger
logging.basicConfig(level=logging.INFO)
categorical = ['PUlocationID', 'DOlocationID']

def load_model(): 

    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    return dv, lr


def get_file_path(year, month):

    return f'https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_{year:04d}-{month:02d}.parquet'


def read_data(filename):
    
    df = pd.read_parquet(filename)
    logging.info(f"Read the filename {filename}")
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


def run(year, month):

    dv, lr = load_model()
    file_path = get_file_path(year=year, month=month)
    df = read_data(filename=file_path)
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    logging.info(f"Mean predicted duration for year {year} and month {month} is {y_pred.mean()}")
    
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    df['predictions'] = y_pred

    df_result = df[['ride_id', 'predictions']].copy()

    # writing results to parquet
    output_file = f"output/{year:04d}-{month:02d}-results.parquet"
    df_result.to_parquet(output_file, engine='pyarrow', compression=None, index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", help="year in YYYY format", default=2021, type=int)
    parser.add_argument("-m", "--month", help="month in MM format or M format", default=1, type=int)
    args = parser.parse_args()

    year = args.year
    month = args.month

    if args.month < 1 and args.month > 12:
        logging.info("Invalid month, please choose value between 1 and 12")
    else:
        run(year, month)
