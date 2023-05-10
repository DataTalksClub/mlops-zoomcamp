import pandas as pd
import pyarrow.parquet as pq


data_files = ["../datasets/green_tripdata_2021-03.parquet", "../datasets/green_tripdata_2021-04.parquet"]
output_file = "green_tripdata_2021-03to04.parquet"

df = pd.DataFrame()
for file in data_files:
    data = pq.read_table(file).to_pandas()
    df = pd.concat([data, df], ignore_index=True)

df.to_parquet(
    output_file,
    engine='pyarrow',
    compression=None,
    index=False
)
