import argparse
import os
import pickle

import mlflow
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_squared_error

HPO_EXPERIMENT_NAME = "random-forest-hyperopt"
EXPERIMENT_NAME = "random-forest-best-models"

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.sklearn.autolog()

def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def inference(data_path, model):
    X_test, y_test = load_pickle(os.path.join(data_path, "test.pkl"))

    with mlflow.start_run():
        test_rmse = mean_squared_error(y_test, model.predict(X_test), squared=False)
        mlflow.log_metric("test_rmse", test_rmse)


def run(data_path, log_top):

    client = MlflowClient()

    # retrieve the top_n model runs and log the models to MLflow
    experiment = client.get_experiment_by_name(HPO_EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=log_top,
        order_by=["metrics.rmse ASC"]
    )

    # Getting run ids for all top 5 models
    run_ids = [dict(dict(run)['info'])['run_id'] for run in runs]
    
    for id in run_ids:
        model_uri = f"runs:/{id}/model"
        model = mlflow.pyfunc.load_model(model_uri)
        inference(data_path=data_path, model=model)
        
    # select the model with the lowest test RMSE
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    best_run = client.search_runs(experiment_ids=experiment.experiment_id,
                                  run_view_type=ViewType.ACTIVE_ONLY,
                                  max_results=1,
                                  order_by=["metrics.test_rmse ASC"]
                                  )

    # Getting the best run id for test dataset
    best_run_id = [dict(dict(run)['info'])['run_id'] for run in best_run][0]
    
    # register the best model
    model_name = "green_taxi_duration_model"
    model_uri = f"runs:/{best_run_id}/model"
    mlflow.register_model(model_uri=model_uri, name=model_name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        default="./output",
        help="the location where the processed NYC taxi trip data was saved."
    )
    parser.add_argument(
        "--top_n",
        default=5,
        type=int,
        help="the top 'top_n' models will be evaluated to decide which model to promote."
    )
    args = parser.parse_args()

    run(args.data_path, args.top_n)
