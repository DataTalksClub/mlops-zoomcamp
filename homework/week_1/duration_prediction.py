# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: mlops-env
#     language: python
#     name: python3
# ---

# # Import modules and read data

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

jan_data = pd.read_parquet('data/yellow_tripdata_2022-01.parquet')
feb_data = pd.read_parquet('data/yellow_tripdata_2022-02.parquet')

# Join the data of both months in one dataframe

taxi_data = pd.concat([jan_data, feb_data], axis=0)

# # Analyze and prepare data

taxi_data.head()

print(taxi_data.shape)

print(taxi_data.dtypes)

# Compute column of trip duration

taxi_data['duration'] = taxi_data.tpep_dropoff_datetime - taxi_data.tpep_pickup_datetime
taxi_data['duration'] = taxi_data.duration.astype('timedelta64[m]')

print(taxi_data.describe())

# Create features from the datetime columns of pickup and dropoffs 

taxi_data['dropoff_hour'] = taxi_data.tpep_dropoff_datetime.dt.hour
taxi_data['pickup_hour'] = taxi_data.tpep_pickup_datetime.dt.hour

# Remove outliers by defining them as trips with duration between 1 and 60 minutes

taxi_data_filtered = taxi_data[taxi_data.duration.between(1,60)].copy(deep=True)
print(f'{taxi_data_filtered.shape[0] / taxi_data.shape[0]} rows were kept')

# # Preprocessing steps

# Fit the encode on the full data to ensure no ID's are missed

taxi_data_enc = taxi_data_filtered[['PULocationID','DOLocationID']]
enc = OneHotEncoder(drop='if_binary')
enc.fit(taxi_data_enc)

# Split the data into train and validation according to the month

X_train = taxi_data_filtered[taxi_data_filtered.tpep_pickup_datetime.dt.month == 1]
X_val = taxi_data_filtered[taxi_data_filtered.tpep_pickup_datetime.dt.month == 2]
Y_train = X_train.duration.copy(deep=True)
Y_val = X_val.duration.copy(deep=True)

# Select the only two features to train the model and encode them

X_train = enc.transform(X_train[['PULocationID','DOLocationID']])
X_val = enc.transform(X_val[['PULocationID','DOLocationID']])

# Check the number of categories encoded

print(X_val.shape)

# # Train Linear Regression

# Fit the model to the train data and predict

reg = LinearRegression().fit(X_train, Y_train)

# Test the accuracy of the model in the training data

Y_train_pred = reg.predict(X_train)
mean_squared_error(Y_train, Y_train_pred, squared=False)

# Test the accuracy of the model of the validation data

Y_val_pred = reg.predict(X_val)
mean_squared_error(Y_val, Y_val_pred, squared=False)

# The score in validation is slightly higher than in trainning meaning we are in overfitting
