import pandas as pd
import numpy as np

# For reading stock data from yahoo
from pandas_datareader.data import DataReader
import yfinance as yf
from pandas_datareader import data as pdr

# Scale the data
from sklearn.preprocessing import MinMaxScaler

# Keras with the model
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# For time stamps   
import datetime as dt

def load_stock_data(stock_symbol, start_date, end_date):

    # Download stock data
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

    # Keep only 'Close' price
    dataset = stock_data[['Close']].values
    return dataset

def preprocess_data(dataset, lookback=60):
    # Scaling the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)

    # Split into train and test data
    training_data_len = int(len(scaled_data) * 0.95)
    train_data = scaled_data[:training_data_len]
    test_data = scaled_data[training_data_len - lookback:]

    # Prepare training dataset
    x_train, y_train = [], []
    for i in range(lookback, len(train_data)):
        x_train.append(train_data[i-lookback:i, 0])
        y_train.append(train_data[i, 0])

    # Prepare test dataset
    # Split the data into x_train and y_train data sets
    x_test, y_test = [], []

    # takes 60 previous days to predict the next days value
    for i in range(lookback, len(test_data)):
        x_test.append(test_data[i-lookback:i, 0])
        y_test.append(test_data[i, 0])

    # Reshape for LSTM [samples, time_steps, features]
    # x_train = np.array(x_train).reshape(-1, lookback, 1)
    # x_test = np.array(x_test).reshape(-1, lookback, 1)

    # Reshape the data
    x_train = np.reshape(x_train, (np.array(x_train).shape[0], np.array(x_train).shape[1], 1))

    # Convert the x_train and y_train to numpy arrays
    # x_train, y_train = np.array(x_train), np.array(y_train)

    return x_train, y_train, x_test, y_test, scaler

def getPredictions(dataset, dateStart, dateEnd = dt.datetime.now(), firstLayer= 192, secondLayer=96, firstDensity=30, secondDensity=1, epochs=2):
    if pd.isnull(dataset) or len(list(dataset)) == 0:
        raise TypeError("Dataset must have values")
    if not isinstance( dateStart and dateEnd, dt.date):
        raise TypeError("both dates must have DateTime format")

    model = Sequential()
    model.add(LSTM(units=firstLayer, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(units=secondLayer, return_sequences=False))
    model.add(Dense(firstDensity))
    model.add(Dense(secondDensity))

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(x_train, y_train, batch_size=1, epochs=epochs)

    # Create the testing data set
    # Create a new array containing scaled values from index 1543 to 2002 
    test_data = scaled_data[training_data_len - 60: , :]

    # Create the data sets x_test and y_test
    x_test = []
    y_test = dataset[training_data_len:, :]

    for i in range(60, len(test_data)):
        x_test.append(test_data[i-60:i, 0])

    # Convert the data to a numpy array
    x_test = np.array(x_test)

    # Reshape the data
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

    # Get the models predicted price values 
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    # MSE: Measures the average squared difference between predicted and actual values. Lower is better.
    # RMSE: More interpretable as it’s in the same unit as the target variable.
    # MAE: Directly measures the average absolute error.
    # R²: Indicates how well the predictions fit the actual data (closer to 1 is better).

    # Assuming y_test are the actual values and y_pred are the predicted values
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
    #rmse = root_mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    return {
        predictions: predictions,
        mse: mse,
        rmse: rmse,
        mae: mae,
        r2: r2
    }

end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365*5)
dataset = load_stock_data('AAPL', start_date, end_date)
preprocess_data(dataset)
getPredictions('AAPL', start_date,end_date)
