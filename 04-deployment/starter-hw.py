import pickle
import pandas as pd
import sys

with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)

categorical = ['PULocationID', 'DOLocationID']

def read_data(filename):
    print(filename)
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df

taxi_type = sys.argv[1] # 'green'
year = int(sys.argv[2]) # 2021
month = int(sys.argv[3]) # 3

input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
output_file = f'output/{taxi_type}/{year:04d}-{month:02d}.parquet'

df = read_data(input_file)

dicts = df[categorical].to_dict(orient='records')
X_val = dv.transform(dicts)
y_pred = model.predict(X_val)

df['dur_pred'] = y_pred

df.dur_pred.describe()

df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

df_result = pd.DataFrame()
df_result[['ride_id','dur_pred']] = df[['ride_id','dur_pred']]
df_result 

df_result.to_parquet(
    output_file,
    engine='pyarrow',
    compression=None,
    index=False
)

print(df_result.dur_pred.mean())