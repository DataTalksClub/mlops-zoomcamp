import requests

url = 'http://localhost:9696/predict'

ride = {
    'lpep_pickup_datetime': '2021-01-01 00:15:56',
    'PULocationID': 43,
    'DOLocationID': 151,
    'passenger_count': 1.0,
    'trip_distance': 1.01
}

response = requests.post(url, json=ride).json()
print(response)