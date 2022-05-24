## Homework

The goal of this homework is to get familiar with MLflow - You.


## Q1. Install MLflow

To get started with MLflow you'll need to install the MLflow Python package. For this we recommend to create a separate Python environment, for example you can use use [conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-envs), and then install the package there with `pip` or `conda`.

Once you installed the package, run the command `mlflow --version` and check the output.

How does the output look like?
* version 1.X.X
* mlflow 1.X.X
* mlflow, version 1.X.X
* mlflow version is 1.X.X


## Q2. Download and preprocess the data

We'll use the same dataset used in the videos of the 1st and 2nd module: "Green Taxi Trip Records". Download the data for January, February and March 2021 in parquet format from [here](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

Use the script `preprocess_data.py` located in the folder `homework` to preprocess the data. The script will load the data from the folder `<TAXI_DATA_FOLDER>` (the folder where you have downloaded the data), fit a `DictVectorizer` on the training set (January 2021 data) and then save the preprocessed datasets and the model to disk. 

Your task is to download the datasets and then execute this command:

`python preprocess_data.py --raw_data_path <TAXI_DATA_FOLDER> --dest_path ./output`

Tip: make to execute to move to the folder `02-experiment-tracking/homework/` before executing the command and to change the value of `<TAXI_DATA_FOLDER>` to the location where you saved the data.

How many files were saved to `OUTPUT_FOLDER`?
* 1
* 3
* 4
* 7


## Q3. Train a model with autolog

We will train a random forest regressor on the taxi dataset. We have prepared the training script `train.py` for this exercise, which can be also found in the folder `homework`. The script will load the datasets produced in the previous step, train the model on the training set and finally calculate the RMSE on the validation set.

Your task is to modify the script to enable **autologging** with MLflow, execute the script and then launch the MLflow UI to check that the experiment run was properly tracked. 

Tip 1: don't forget to wrap the training code with a `with mlflow.start_run():` statement as we showed in the videos.

Tip 2: don't modify the hyperparameters of the model to make sure that the training will finish quickly.

How many parameters, metrics and tags are automatically logged by MLflow?
* 19, 11, 0
* 17, 6, 2
* 10, 3, 1
* 20, 15, 2

## Q4. Launch the tracking server locally

We will want to manage the entire lifecycle of our ML model and that's why in this step you'll need to launch a tracking server. This way we will also have access to the model registry. 

Your task is to launch the tracking server on your local machine and select a SQLite db for the backend store and a folder called `artifacts` for the artifacts store. You should keep the tracking server running to work on the next two exercises that use the server.

What are the two parameters that you need to pass to properly configure the server?
* `backend-store-uri` and `default-artifact-root`
* `backend-store-uri` and `serve-artifacts`
* `backend-store-uri` and `artifacts-only`
* `backend-store-uri` and `artifacts-destination`


## Q5. Tune the hyperparameters of the model

Now let's try to reduce the validation error by tuning the hyperparameters of the random forest regressor using `hyperopt`. We have prepared the script `hpo.py` for this exercise. 

Your task is to modify the script `hpo.py` and make sure that the validation RMSE is logged to MLflow for each run of the hyperparameter optimization (you will need to add a few lines of code to the `objective` function) and run the script without passing any parameters. After that, open the MLflow UI and explore the runs from the experiment called `random-forest-hyperopt` to answer the question below.

Important: don't use autologging for this exercise. The idea is to just log the information that you need to answer the question below, including:
* the list of hyperparameters that are passed to the `objective` function during the optimization.
* the RMSE obtained on the validation set (February 2021 data).

What is the set of hyperparameters that resulted in the lowest validation RMSE?
* `max_depth=1, min_samples_leaf=1, min_samples_split=2, n_estimators=10`
* `max_depth=20, min_samples_leaf=4, min_samples_split=10, n_estimators=50`
* `max_depth=11, min_samples_leaf=2, min_samples_split=3, n_estimators=23`
* `max_depth=19, min_samples_leaf=3, min_samples_split=5, n_estimators=28`


## Q6. Promote the best model to the model registry

The results from the hyperparameter optimization are quite good so we can assume that we are ready to test some of these models in production. In this exercise you'll promote the best model to the model registry. We have prepared a script called `register_model.py`, which will check the results from the previous step and select the top 5 runs. After that it will calculate the RMSE of those models on the test set (March 2021 data) and save the results to a new experiment called `random-forest-best-models`.

Your task is update the script `register_model.py` so that it selects the model with lowest RMSE on the test set and registers it to the model registry.

Tip 1: you can use the method `search_runs` from the `MlflowClient` to get the model with lowest RMSE.
Tip 2: to register the model you can use the method `mlflow.register_model` and you will need to pass the right model_uri in the form of string that looks like this: `"runs:/<RUN_ID>/model"`, and the name of the model (make sure to choose a good one!).

What is the test RMSE of the best model?
* 6.1
* 6.55
* 6.97
* 7.71