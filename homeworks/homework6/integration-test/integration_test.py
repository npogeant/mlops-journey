import os
import pandas as pd

S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', "http://localhost:4566")

options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL,

    }
}

def read_data():
    df = pd.read_parquet('s3://demo-bucket/file.parquet', storage_options=options)
    
    return df

read_data()