import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Specify which participant to analyze and how to resample and roll up the data
participant = 'a'
resample_rule = '1d'
rolling_mean_window = 60

# Specify which datasets to look for, which columns to use, and how to draw their lines on the chart
datasets = [
    # dataset      column                    linetype
    ['lifeslice',  'emotions.valence',       'g-'],
    ['imessage',   'sentiment.comparative',  'r-'],
    ['facebook',   'sentiment.comparative',  'b-'],
    ['dayone',     'sentiment.comparative',  'y-'],
    ['750words',   'sentiment.comparative',  'm-']
]

# Specify how we define outliers
def find_outliers(series):
    iqr = (series.quantile(0.25) * 1.5, series.quantile(0.75) * 1.5)
    outliers = (series < iqr[0]) | (series > iqr[1])
    return outliers
    
# Create a function to normalize values from -1 to 1
def normalize(series):
    return (series - series.mean()) / (series.max() - series.min())

# Define a function that takes a csv file path and prepares the data to be analyzed and charted
def prepare(csv, column):

    # Read the csv, merging `date` and `time` columns into a single `date_time` column of type Timestamp and use this as the index
    raw = pd.read_csv(csv, parse_dates=[['date', 'time']], index_col=['date_time']).dropna()
    
    # Remove outliers whose emotional valence are outside of the interquartile range (IQR) * 1.5
    number_total = raw.shape[0]
    outliers = find_outliers(raw[column])
    raw = raw[~outliers]
    number_remaining = raw.shape[0]
    number_outliers = number_total - number_remaining
    print("{csv}: Total Rows: {number_total} Outliers Removed: {number_outliers} Rows Remaining: {number_remaining}".format(**locals()))
    
    # Normalize values to a range of -1 to 1
    raw[column] = normalize(raw[column])
    
    # Resample the Lifeslice data by taking the mean emotional valence of each day
    prepared = raw[column].resample(resample_rule).mean()
    
    # Fill in empty days by using the mean of surrounding days
    prepared = prepared.fillna(prepared.mean()) # or should we use lifeslice['emotions.valence']?
    
    # Calculate the rolling mean (aka simple moving average)
    prepared = prepared.rolling(rolling_mean_window, center=True).mean()
    
    # Get the start and end dates... mostly just for curiosity's sake
    start_date = prepared.index[0]
    end_date = prepared.index[-1]
    
    # Print the start and end dates
    start_date_string = start_date.strftime('%Y-%m-%d')
    end_date_string = end_date.strftime('%Y-%m-%d')
    print("{csv}: Date Range: {start_date_string} to {end_date_string}".format(**locals()))

    return prepared

# Create a new dataframe to hold the resampled, cleaned data for analysis
data = pd.DataFrame()

# Create a line chart
fig, ax = plt.subplots(1)
fig.autofmt_xdate()

# Prepare data and chart it
for pair in datasets:
    
    dataset = pair[0]
    column = pair[1]
    linetype = pair[2]    
    # Define where the dataset CSV lives
    csv = 'data/' + participant + '/' + dataset + '.csv'
    
    # Skip this dataset if it does not exist for the participant
    if (not os.path.exists(csv)):
        continue
    
    data[dataset + '.' + column] = prepare(csv, column)

    # Add the sentiment comparative rolling mean to the chart
    ax.plot(data.index, data[dataset + '.' + column], linetype)
