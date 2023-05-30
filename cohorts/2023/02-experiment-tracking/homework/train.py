import os
import pickle
import click

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

import mlflow
import mlflow.sklearn

mlflow.autolog(exclusive=False)

from mlflow.tracking import MlflowClient

from mlflow import log_metric, log_param, log_artifacts

#Set the MLflow server and backend and artifact stores
mlflow.set_tracking_uri("http://localhost:5000")

mlflow.set_experiment("mlops_zoomcamp")


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)

def run_train(data_path: str):
    with mlflow.start_run():
        
        mlflow.set_tag("developer","lisana berberi")

        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = mean_squared_error(y_val, y_pred, squared=False)

        #print("logs: ", mlflow.log_metric("rmse", rmse))
        print("Tracking_uri: ", mlflow.get_tracking_uri())
        print("Artifact_uri: ", mlflow.get_artifact_uri())
        print("Model saved in run %s" % mlflow.active_run().info.run_uuid) 

       # mlflow.log_artifact(local_path="models/lin_reg.bin", artifact_path="models_pickle")

    mlflow.end_run()


if __name__ == '__main__':
        run_train()
  

