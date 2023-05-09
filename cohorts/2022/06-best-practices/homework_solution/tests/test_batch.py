from datetime import datetime

import pandas as pd

import batch


def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)


def test_prepare_data():
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
    ]

    categorical = ['PUlocationID', 'DOlocationID']
    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
    df = pd.DataFrame(data, columns=columns)

    df_actual = batch.prepare_data(df, categorical)

    data_expected = [
        ('-1', '-1', 8.0),
        ( '1',  '1', 8.0),
    ]

    columns_test = ['PUlocationID', 'DOlocationID', 'duration']
    df_expected = pd.DataFrame(data_expected, columns=columns_test)
    print(df_actual)

    assert (df_actual['PUlocationID'] == df_expected['PUlocationID']).all()
    assert (df_actual['DOlocationID'] == df_expected['DOlocationID']).all()
    assert (df_actual['duration'] - df_expected['duration']).abs().sum() < 0.0000001


