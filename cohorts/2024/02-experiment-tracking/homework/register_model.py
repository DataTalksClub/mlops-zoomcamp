import os
import pickle
import click
import mlflow

from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, root_mean_squared_error

HPO_EXPERIMENT_NAME = "random-forest-hyperopt"
EXPERIMENT_NAME = "random-forest-best-models"
RF_PARAMS = ['max_depth', 'n_estimators', 'min_samples_split', 'min_samples_leaf', 'random_state']
MLFLOW_TRACKING_URI = 'sqlite:///mlflow.db'

#mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.sklearn.autolog()


def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def train_and_log_model(data_path, params):
    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))
    X_test, y_test = load_pickle(os.path.join(data_path, "test.pkl"))

    with mlflow.start_run():
        mlflow.set_tag('model', 'random forest')
        mlflow.log_param('parameters', params)

        params = {
            'max_depth': 19, 
            'min_samples_leaf': 2, 
            'min_samples_split': 2, 
            'n_estimators': 11, 
            'random_state': 42
        }

        for param in RF_PARAMS:
            params[param] = int(params[param])
            
        rf = RandomForestRegressor(**params)
        rf.fit(X_train, y_train)

        # Evaluate model on the validation and test sets
        val_rmse = root_mean_squared_error(y_val, rf.predict(X_val))
        mlflow.log_metric("val_rmse", val_rmse)
        test_rmse = root_mean_squared_error(y_test, rf.predict(X_test))
        mlflow.log_metric("test_rmse", test_rmse)
        mlflow.sklearn.log_model(RandomForestRegressor, artifact_path='models_mlflow')
        


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
@click.option(
    "--top_n",
    default=5,
    type=int,
    help="Number of top models that need to be evaluated to decide which one to promote"
)
def run_register_model(data_path: str, top_n: int):

    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

    # Retrieve the top_n model runs and log the models
    experiment = client.get_experiment_by_name(HPO_EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=top_n,
        order_by=["metrics.val_rmse ASC"]
    )
    for run in runs:
        train_and_log_model(data_path=data_path, params=run.data.params)

    # Select the model with the lowest test RMSE
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=top_n,
        order_by=["metrics.test_rmse ASC"])[0] #client.search_runs()[0]

    # Register the best model
    model_name ='taxi_random_forest'
    run_id = best_run.info.run_id 
    model_uri = f'runs:/{run_id}/model'
    mlflow.register_model(model_uri=model_uri, name=model_name)




if __name__ == '__main__':
    run_register_model()
