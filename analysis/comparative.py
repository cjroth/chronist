import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly as py
import cufflinks as cf
py.tools.set_credentials_file(username='cjroth', api_key='N7E7pw9PBszV5t4DVQqu')

# Specify which participant to analyze and how to resample and roll up the data
participant = 'a'
resample_rule = '1d'
rolling_mean_window = 60
# scale = (-1, 1)
scale = None
timeframe = ('2016-04-01', '2017-02-01')

if (not os.path.isdir('data')):
    raise Exception('Data directory does not exist. Are you sure you running this from the right directory?')

data_dir = 'data/' + participant
if (not os.path.isdir(data_dir)):
    raise Exception('Participant does not exist.')

# Specify which datasets to look for, which columns to use, and how to draw their lines on the chart
datasets = [
    # dataset      column                    datatype       linetype
    ('lifeslice',  'emotions.valence',       'scale',       'g-'),
    # ('imessage',   'sentiment.comparative',  'scale',       'r-'),
    # ('facebook',   'sentiment.comparative',  'scale',       'b-'),
    # ('dayone',     'sentiment.comparative',  'scale',       'y-'),
    # ('750words',   'sentiment.comparative',  'scale',       'm-'),
    # ('lifeslice',  'appearance.age',         'category',    'm-'),
]

# Specify how we define outliers
def find_outliers(series):
    ''' specifies how outliers are defined '''
    iqr = (series.quantile(0.25) * 1.5, series.quantile(0.75) * 1.5)
    outliers = (series < iqr[0]) | (series > iqr[1])
    return outliers

# Create a function to normalize values from -1 to 1
def normalize(series):
    min = series.min()
    max = series.max()
    return ((series - min) / (max - min) - 0.5) * 2

def prepare_category(csv, column):

    # Read the csv, merging `date` and `time` columns into a single `date_time` column of type Timestamp and use this as the index
    raw = pd.read_csv(csv, parse_dates=[['date', 'time']], index_col=['date_time']).dropna()

    # Convert the age column to categories
    prepared = raw[column].astype('category')

    # Remove datum that are not definite age ranges
    prepared = prepared.cat.remove_categories(['Under 18','65+'])
    prepared = prepared.dropna()

    # Map age ranges to their mean age
    prepared = prepared.apply(lambda x: {
        '18 - 24' : 21.0,
        '25 - 34' : 29.5,
        '35 - 44' : 39.5,
        '45 - 54' : 49.5,
        '55 - 64' : 59.5
    }[x]).astype('float')

    # Resample by taking the mean value of each day
    prepared = prepared.resample(resample_rule).mean()

    # Fill in empty days by using the mean of surrounding days
    prepared = prepared.fillna(prepared.mean())

    # Calculate the rolling mean (aka simple moving average)
    prepared = prepared.rolling(rolling_mean_window, center=True).mean()

    return prepared, raw

# Define a function that takes a csv file path and prepares the data to be analyzed and charted
def prepare_scale(csv, column):

    # Read the csv, merging `date` and `time` columns into a single `date_time` column of type Timestamp and use this as the index
    raw = pd.read_csv(csv, parse_dates=[['date', 'time']], index_col=['date_time']).dropna()

    # Remove outliers outside of the interquartile range (IQR) * 1.5
    number_total = raw.shape[0]
    outliers = find_outliers(raw[column])
    raw = raw[~outliers]
    number_remaining = raw.shape[0]
    number_outliers = number_total - number_remaining
    print("{csv}: Total Rows: {number_total} Outliers Removed: {number_outliers} Rows Remaining: {number_remaining}".format(**locals()))

    prepared = raw[column]

    # Resample by taking the mean value of each day
    prepared = raw[column].resample(resample_rule).mean()

    # Fill in empty days by using the mean of surrounding days
    prepared = prepared.fillna(prepared.mean())

    # Calculate the rolling mean (aka simple moving average)
    prepared = prepared.rolling(rolling_mean_window, center=True).mean()

    # Normalize values to a range of -1 to 1
    prepared = normalize(prepared)

    # Print the start and end dates
    range = tuple(i.strftime('%Y-%m-%d') for i in (prepared.index[0], prepared.index[-1]))
    print("{csv}: Date Range: {range[0]} to {range[1]}".format(**locals()))

    return prepared, raw

def prepare(raw):
    
    # Remove rows with empty values
    raw = raw.dropna()

    # Remove outliers outside of the interquartile range (IQR) * 1.5
    # number_total = raw.size
    outliers = find_outliers(raw)
    raw = raw[~outliers]
    # number_remaining = raw.size
    # number_outliers = number_total - number_remaining
    # print("Total Rows: {number_total} Outliers Removed: {number_outliers} Rows Remaining: {number_remaining}".format(**locals()))

    # Normalize values to a range of -1 to 1
    raw = normalize(raw)
    
    return raw

# Create a new dataframe to hold the resampled, cleaned data for analysis
index = pd.date_range(*(datetime.datetime.strptime(i, '%Y-%m-%d') for i in timeframe))
data = pd.DataFrame(index=index)

# Create a line chart
fig, ax = plt.subplots(1)
fig.autofmt_xdate()
if scale != None:
    ax.set_ylim(*scale)

# Set up a Bokeh chart
p1 = figure(x_axis_type='datetime', title='Chronist')
p1.grid.grid_line_alpha = 0.3
p1.xaxis.axis_label = 'Date'
p1.yaxis.axis_label = 'Value'
p1.legend.location = 'top_left'

chart = [
    'lifeslice.emotions.valence',
    'imessage.sentiment.comparative',
]

colors = ['#B2DF8A', '#A6CEE3']

# Prepare data and chart it
for index, pair in enumerate(datasets):

    dataset  = pair[0]
    column   = pair[1]
    datatype = pair[2]
    linetype = pair[3]

    # Define where the dataset CSV lives
    csv = data_dir + '/' + dataset + '.csv'

    label = dataset + '.' + column

    # Skip this dataset if it does not exist for the participant
    if (not os.path.exists(csv)):
        continue

    if (datatype == 'scale'):
        data[label], raw = prepare_scale(csv, column)
    else:
        data[label], raw = prepare_category(csv, column)


    if label in chart:

        # Add the sentiment comparative rolling mean to the chart
        ax.plot(data.index, data[label], linetype)

        p1.line(np.array(data.index, dtype=np.datetime64), data[label], color=colors[index], legend=label)

data.to_csv(data_dir + '/combined.csv')

# py.plotly.plot([{
#     'x': data.index,
#     'y': data[col],
#     'name': col
# }  for col in data.columns], filename='chronist', kind='scatter')

# output_file('public/' + participant + '.html', title='Chronist: Participant ' + participant.upper() + ' Visualization')
# show(gridplot([[p1]], responsive=True)) # open a browser








# https://plot.ly/pandas/time-series/

# cf.datagen.lines(1,500).ta_plot(study='sma',periods=[13,21,55],title='Simple Moving Averages')


import plotly.graph_objs as go

# upper_bound = go.Scatter(
#     name='Upper Bound',
#     x=df['Time'],
#     y=df['10 Min Sampled Avg']+df['10 Min Std Dev'],
#     mode='lines',
#     marker=dict(color="444"),
#     line=dict(width=0),
#     fillcolor='rgba(68, 68, 68, 0.3)',
#     fill='tonexty' )

raw = prepare(raw['emotions.valence'])

trace_markers = go.Scatter(
    name='lifeslice.emotions.valence',
    x=raw.index,
    y=raw,
    mode="markers",
    # line=dict(color='rgb(31, 119, 180)'),
    # fillcolor='rgba(68, 68, 68, 0.3)',
)

trace = go.Scatter(
    name=data['lifeslice.emotions.valence'],
    x=data.index,
    y=data['lifeslice.emotions.valence'],
    mode="lines",
    line=dict(color='rgb(31, 119, 180)'),
    # fillcolor='rgba(68, 68, 68, 0.3)',
    fill='tonexty' )

# lower_bound = go.Scatter(
#     name='Lower Bound',
#     x=df['Time'],
#     y=df['10 Min Sampled Avg']-df['10 Min Std Dev'],
#     marker=dict(color="444"),
#     line=dict(width=0),
#     mode='lines' )

# Trace order can be important
# with continuous error bars
# data = [lower_bound, trace, upper_bound]
d = [trace_markers, trace]

layout = go.Layout(
    yaxis=dict(title='Wind speed (m/s)'),
    title='Continuous, variable value error bars',
    showlegend = False)
fig = go.Figure(data=d, layout=layout)

# IPython notebook
# py.iplot(fig, filename='pandas-time-series-error-bars')

url = py.plotly.plot(fig, filename='chronist')
