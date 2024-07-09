import lambda_function

def test_prepare_features():
    ride = {
        'PULocationID': 10,
        'DOLocationID': 50,
        'trip_distance': 40
    }
    
    actual_features = lambda_function.prepared_features(ride)
    expected_features = {
        'PU_DO': '10_50',
        'trip_distance': 40
    }
    
    assert actual_features == expected_features
    
    
    