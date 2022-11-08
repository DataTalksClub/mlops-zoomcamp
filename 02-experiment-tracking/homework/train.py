import argparse
import os
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def run(data_path):

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_valid, y_valid = load_pickle(os.path.join(data_path, "valid.pkl"))

    rf = RandomForestRegressor(max_depth=10, random_state=0)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_valid)

    rmse = mean_squared_error(y_valid, y_pred, squared=False)
    return rmse

def mlflow_experiment_registry(experiment_name, data_path):
    mlflow.set_experiment(experiment_name)
    mlflow.sklearn.autolog()
    
    with mlflow.start_run():
        rmse = run(data_path)
        mlflow.log_metric("rmse",rmse)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-path",
        default="./output",
        help="the location where the processed NYC taxi trip data was saved."
    )

    parser.add_argument(
        '--experiment-name', 
        default='random-forest-experiment', 
        help='Name of the experiment'
    )

    args = parser.parse_args()
    #run(args.data_path)
    mlflow_experiment_registry(args.experiment_name, args.data_path)
