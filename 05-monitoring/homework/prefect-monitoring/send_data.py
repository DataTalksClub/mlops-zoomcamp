import json
import uuid
from datetime import datetime

import pyarrow.parquet as pq
import requests

table = pq.read_table("../datasets/green_tripdata_2021-05.parquet")\
          .to_pandas()\
          .sample(n=5000, random_state=42) #5000 rows sampled
data = table.copy()


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


with open("target.csv", 'w') as f_target:
    for index, row in data.iterrows():
        row['id'] = str(uuid.uuid4())
        duration = (row['lpep_dropoff_datetime'] - row['lpep_pickup_datetime']).total_seconds() / 60
        if duration >= 1 and duration <= 60:
            f_target.write(f"{row['id']},{duration}\n")
        resp = requests.post("http://127.0.0.1:9696/predict-duration",
                             headers={"Content-Type": "application/json"},
                             data=row.to_json()).json()
        print(f"prediction: {resp['data']['duration']}")
