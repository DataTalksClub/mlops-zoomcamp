import argparse
import os
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("brian_green_taxi")

# enable autologging
mlflow.sklearn.autolog()

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def run(data_path):

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("brian_green_taxi")
   
    with mlflow.start_run():

        # enable autologging
        mlflow.sklearn.autolog()

        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_valid, y_valid = load_pickle(os.path.join(data_path, "valid.pkl"))

        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_valid)

        rmse = mean_squared_error(y_valid, y_pred, squared=False)
        mlflow.log_metric('valid_rmse', rmse)

        mlflow.sklearn.log_model(rf, artifact_path="artifacts")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        default="./output",
        help="the location where the processed NYC taxi trip data was saved."
    )
    args = parser.parse_args()

    run(args.data_path)
