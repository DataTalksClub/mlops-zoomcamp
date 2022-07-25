from datetime import datetime

import pandas as pd
from pandas import Timestamp

from batch import prepare_data


def dt(hour, minute, second=0):
    """Function to prepare datetime object"""

    return datetime(2021, 1, 1, hour, minute, second)


def test_data_prep():
    """Test function to create fake data in bucket and checks if data exists"""

    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (1, 1, dt(1, 2, 0), dt(2, 2, 1)),
    ]

    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
    categorical = ['PUlocationID', 'DOlocationID']
    df = pd.DataFrame(data, columns=columns)

    result_output = prepare_data(raw_data=df, categorical=categorical).to_dict(orient='records')

    expected_output = [
        {
            'PUlocationID': '-1',
            'DOlocationID': '-1',
            'pickup_datetime': Timestamp('2021-01-01 01:02:00'),
            'dropOff_datetime': Timestamp('2021-01-01 01:10:00'),
            'duration': 8.000000000000002,
        },
        {
            'PUlocationID': '1',
            'DOlocationID': '1',
            'pickup_datetime': Timestamp('2021-01-01 01:02:00'),
            'dropOff_datetime': Timestamp('2021-01-01 01:10:00'),
            'duration': 8.000000000000002,
        },
    ]

    assert result_output == expected_output
