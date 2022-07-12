import json
import os
import pickle

import pandas
from prefect import flow, task
from pymongo import MongoClient
import pyarrow.parquet as pq

from evidently import ColumnMapping

from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab,RegressionPerformanceTab

from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection, RegressionPerformanceProfileSection


@task
def upload_target(filename):
    client = MongoClient("mongodb://localhost:27018/")
    collection = client.get_database("prediction_service").get_collection("data")
    with open(filename) as f_target:
        for line in f_target.readlines():
            row = line.split(",")
            collection.update_one({"id": row[0]}, {"$set": {"target": float(row[1])}})
    client.close()


@task
def load_reference_data(filename):
    MODEL_FILE = os.getenv('MODEL_FILE', './prediction_service/lin_reg.bin')
    with open(MODEL_FILE, 'rb') as f_in:
        dv, model = pickle.load(f_in)
    reference_data = pq.read_table(filename).to_pandas()
    # Create features
    reference_data['PU_DO'] = reference_data['PULocationID'].astype(str) + "_" + reference_data['DOLocationID'].astype(str)

    # add target column
    reference_data['target'] = reference_data.lpep_dropoff_datetime - reference_data.lpep_pickup_datetime
    reference_data.target = reference_data.target.apply(lambda td: td.total_seconds() / 60)
    reference_data = reference_data[(reference_data.target >= 1) & (reference_data.target <= 60)]
    features = ['PU_DO', 'PULocationID', 'DOLocationID', 'trip_distance']
    x_pred = dv.transform(reference_data[features].to_dict(orient='records'))
    reference_data['prediction'] = model.predict(x_pred)
    return reference_data


@task
def fetch_data():
    client = MongoClient("mongodb://localhost:27018/")
    data = client.get_database("prediction_service").get_collection("data").find()
    df = pandas.DataFrame(list(data))
    return df


@task
def run_evidently(ref_data, data):
    ref_data.drop('ehail_fee', axis=1, inplace=True)
    data.drop('ehail_fee', axis=1, inplace=True)  # drop empty column (until Evidently will work with it properly)
    profile = Profile(sections=[DataDriftProfileSection(), RegressionPerformanceProfileSection()])
    mapping = ColumnMapping(prediction="prediction", numerical_features=['trip_distance'],
                            categorical_features=['PULocationID', 'DOLocationID'],
                            datetime_features=[])
    profile.calculate(ref_data, data, mapping)

    dashboard = Dashboard(tabs=[DataDriftTab(), RegressionPerformanceTab(verbose_level=0)])
    dashboard.calculate(ref_data, data, mapping)
    return json.loads(profile.json()), dashboard


@task
def save_report(result):
    client = MongoClient("mongodb://localhost:27018/")
    client.get_database("prediction_service").get_collection("report").insert_one(result[0])


@task
def save_html_report(result):
    result[1].save("evidently_report_example.html")


@flow
def batch_analyze():
    upload_target("target.csv")
    ref_data = load_reference_data("./evidently_service/datasets/green_tripdata_2021-01.parquet")
    data = fetch_data()
    result = run_evidently(ref_data, data)
    save_report(result)
    save_html_report(result)

batch_analyze()
