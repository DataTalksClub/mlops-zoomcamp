import os
import pickle
import click

import mlflow
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, root_mean_squared_error


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

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))
    with mlflow.start_run():
        mlflow.set_tag('developer', 'Eniola')
        mlflow.log_param('Train-data-path', './output/train.pk1')
        mlflow.log_param('Val-data-path', './output/val.pk1')
        mlflow.log_param('Test-data-path', './output/test.pk1')

        max_depth = 10
        mlflow.log_param('max_depth', max_depth)
    
        rf = RandomForestRegressor(max_depth=max_depth, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = root_mean_squared_error(y_val, y_pred)

        RF_PARAMS = ['max_depth', 'n_estimators', 'min_samples_split', 'min_samples_leaf', 'random_state']
        params = rf.get_params(RF_PARAMS)

        mlflow.log_param('parameters', params)
        #mlflow.log_param('rf_parameters', RF_PARAMS)
        mlflow.log_metric('rmse', rmse)


if __name__ == '__main__':
    run_train()
 