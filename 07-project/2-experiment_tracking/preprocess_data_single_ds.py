import mlflow
import pandas as pd
from sklearn.utils import shuffle


print(f"tracking URI: '{mlflow.get_tracking_uri()}'")
mlflow.search_experiments()

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

mlflow.set_experiment("my-experiment-1")

y = pd.read_csv("07-project/true_fake_label.csv")
X = pd.read_csv("07-project/true_fake_data.csv.zip", index_col=0)
X, y = shuffle(X, y)

with mlflow.start_run():
    params = {"C": 0.1, "random_state": 42}
    mlflow.log_params(params)

    lr = LogisticRegression(**params).fit(X, y)
    y_pred = lr.predict(X)
    mlflow.log_metric("accuracy", accuracy_score(y, y_pred))

    mlflow.sklearn.log_model(lr, artifact_path="models")
    print(f"default artifacts URI: '{mlflow.get_artifact_uri()}'")


from mlflow.tracking import MlflowClient
client = MlflowClient()

from mlflow.exceptions import MlflowException
try:
    client.get_registered_model()
except MlflowException:
    print("It's not possible to access the model registry :(")




