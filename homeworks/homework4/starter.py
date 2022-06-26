#!/usr/bin/env python
# coding: utf-8

import sys

import pickle
import pandas as pd

with open('model.bin', 'rb') as f_in:
    dv, lr = pickle.load(f_in)

categorical = ['PUlocationID', 'DOlocationID']

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df

year = int(sys.argv[1]) # 2021
month = int(sys.argv[2]) # 2

input_file = f'https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_{year:04d}-{month:02d}.parquet'
print(f'...getting the data from : {input_file}')

df = read_data(f'https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_{year:04d}-{month:02d}.parquet')
df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

dicts = df[categorical].to_dict(orient='records')
X_val = dv.transform(dicts)
y_pred = lr.predict(X_val)

print(y_pred.mean())

df_result = pd.DataFrame()
df_result['ride_id'] = df['ride_id']
df_result['predicted_duration'] = y_pred

output_file = f'fhv_tripdata_{year:04d}-{month:02d}.parquet'

df_result.to_parquet(
    output_file,
    engine='pyarrow',
    compression=None,
    index=False
)