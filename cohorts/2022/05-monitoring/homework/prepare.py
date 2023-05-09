from tqdm import tqdm
import requests

files = ["green_tripdata_2021-03.parquet", "green_tripdata_2021-04.parquet", "green_tripdata_2021-05.parquet"]
path = "./datasets"
print(f"Download files:")
for file in files:

    # Change the url based on what works for you whether s3 or cloudfront
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file}"
    resp = requests.get(url, stream=True)
    save_path = f"{path}/{file}"
    with open(save_path, "wb") as handle:
        for data in tqdm(resp.iter_content(),
                         desc=f"{file}",
                         postfix=f"save to {save_path}",
                         total=int(resp.headers["Content-Length"])):
            handle.write(data)
