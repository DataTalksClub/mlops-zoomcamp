import pandas as pd
from datetime import datetime

from batch import prepare_data


def dt(hour, minute, second=0):
    return datetime(2022, 1, 1, hour, minute, second)


def test_prepare_data():
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2), dt(1, 10)),
        (1, 2, dt(2, 2), dt(2, 3)),
        (None, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (2, 3, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
    ]

    categorical = ['PULocationID', 'DOLocationID']
    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)

    df_actual = prepare_data(df, categorical)

    data_expected = [
        ('-1', '-1', 8.0),
        ('1',  '-1', 8.0),
        ('1', '2', 1.0),
    ]

    columns_test = ['PULocationID', 'DOLocationID', 'duration']
    df_expected = pd.DataFrame(data_expected, columns=columns_test)
    print(df_actual)

    assert (df_actual['PULocationID'] == df_expected['PULocationID']).all()
    assert (df_actual['DOLocationID'] == df_expected['DOLocationID']).all()
    assert (df_actual['duration'] - df_expected['duration']).abs().sum() < 0.0000001


