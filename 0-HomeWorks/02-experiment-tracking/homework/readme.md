1. mlflow, version 2.12.2
2. output folder=4
3. min-sample-split=2
4. locally-- mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts

x=[default-artifact-root]
server-- mlflow server --backend-store-uri sqlite:///mlflow.db --x ./artifacts

5. rsme: 5.3354
6. test rsme: 5.567


