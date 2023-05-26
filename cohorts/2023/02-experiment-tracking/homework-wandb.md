## Homework with Weights & Biases

The goal of this homework is to get familiar with Weights & Biases for experiment tracking, model management, hyperparameter optimization, and many more.

# Q1. Install the Package

To get started with Weights & Biases you'll need to install the appropriate Python package.

For this we recommend creating a separate Python environment, for example, you can use [conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-envs), 
and then install the package there with `pip` or `conda`.

Once you installed the package, run the command `wandb --version` and check the output.

What's the version that you have?

## Q2. Download and preprocess the data

We'll use the Green Taxi Trip Records dataset to predict the amount of tips for each trip. 

Download the data for January, February and March 2022 in parquet format from [here](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

Use the script `preprocess_data.py` located in the folder [`homework-wandb`](homework-wandb) to preprocess the data.

The script will:

* initialize a Weights & Biases run.
* load the data from the folder `<TAXI_DATA_FOLDER>` (the folder where you have downloaded the data),
* fit a `DictVectorizer` on the training set (January 2022 data),
* save the preprocessed datasets and the `DictVectorizer` to your Weights & Biases dashboard as an artifact of type `preprocessed_dataset`.

Your task is to download the datasets and then execute this command:

```
python preprocess_data.py --wandb_project <WANDB_PROJECT_NAME> --wandb_entity <WANDB_USERNAME> --raw_data_path <TAXI_DATA_FOLDER> --dest_path ./output
```

Tip: go to `02-experiment-tracking/homework-wandb/` folder before executing the command and change the value of `<WANDB_PROJECT_NAME>` to the name of your Weights & Biases project, `<WANDB_USERNAME>` to your Weights & Biases username, and `<TAXI_DATA_FOLDER>` to the location where you saved the data.

Once you navigate to the `Files` tab of your artifact on your Weights & Biases page, what's the size of the saved `DictVectorizer` file?

* 54 kB
* 154 kB
* 54 MB
* 154 MB
