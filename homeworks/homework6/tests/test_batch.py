import os
import pandas as pd
from datetime import datetime
import pickle

def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)

data = [
    (None, None, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
    (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
]

columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
test_data = pd.DataFrame(data, columns=columns)

def prepare_data(df):
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    
    categorical = ['PUlocationID', 'DOlocationID']
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df
    

def test_dataframe():
    actual_df = prepare_data(test_data)
    
    data = [
        (-1, -1, dt(1, 2), dt(1, 10), 8.0),
        (1, 1, dt(1, 2), dt(1, 10), 8.0)      
    ]

    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime', 'duration']
    expected_result = pd.DataFrame(data, columns=columns)
    
    assert actual_df.shape[0] == expected_result.shape[0]


S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', "http://localhost:4566")

options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL,

    }
}

def test_localstack():

    test_data.to_parquet(
        's3://demo-bucket/file.parquet',
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )
    
    df = pd.read_parquet('s3://demo-bucket/file.parquet', storage_options=options)
    
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    categorical = ['PUlocationID', 'DOlocationID']

    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean(),'\n',
          'predicted sum duration:', y_pred.sum())

    df_result = pd.DataFrame()
    df_result['predicted_duration'] = y_pred
    
    return 

test_localstack()