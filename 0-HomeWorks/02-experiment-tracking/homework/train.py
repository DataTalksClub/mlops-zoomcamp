import os
import pickle
import click
import mlflow
from scipy.sparse import csr_matrix
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


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
        mlflow.sklearn.autolog()

        # Load training and validation data
        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

        # Convert to CSR matrix if data is sparse
        X_train_csr = csr_matrix(X_train)
        X_val_csr = csr_matrix(X_val)

        # Train the model
        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train_csr, y_train)

        # Predict on the validation set
        y_pred = rf.predict(X_val_csr)

        # Calculate RMSE
        rmse = mean_squared_error(y_val, y_pred, squared=False)
        print(f"RMSE: {rmse}")

        # Log the RMSE
        mlflow.log_metric("rmse", rmse)


if __name__ == '__main__':
    run_train()