import csv
import os
import pandas as pd
import numpy as np

original_df = None

class Metrics:
    average_open = 0.0
    average_high = 0.0
    average_low = 0.0
    average_close = 0.0
    average_units = 0.0 

# reads file and returns a data frame
def read_file(filename) -> pd.DataFrame:
    return pd.read_csv(filename)

if os.path.exists('../../Data/NASDAQ_20101105.txt'):
    original_df = read_file('../../Data/NASDAQ_20101105.txt')
else:
    print('file DNE')

# format date column ti have slashes.
dates = original_df['DATE']
formatted_dates = []
for date in dates:
    date = str(date)
    year = date[:4]
    month = date[4:6]
    day = date[6:]

    formatted_dates.append(f'{month}/{day}/{year}')

original_df['DATE'] = formatted_dates

print(original_df)