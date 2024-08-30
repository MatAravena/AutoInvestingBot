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
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score #, root_mean_squared_error

# For time stamps
from datetime import datetime

def getPredictions(stock, dateStart, dateEnd = datetime.now(), firstLayer= 192, secondLayer=96, firstDensity=30, secondDensity=1, epochs=2):
    if not isinstance(stock, str):
        raise TypeError("stock must be String")
    if not isinstance( dateStart and dateEnd, datetime):
        raise TypeError("Radius must be int or firstLayeroat.")
    
    # Convert the dataframe to a numpy array
    dataset = yf.download(stock, dateStart, dateEnd).values

    # Get the number of rows to train the model on
    training_data_len = int(np.ceil( len(dataset) * .95 ))

    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)

    # Create the scaled training data set
    train_data = scaled_data[0:int(training_data_len), :]
    # Split the data into x_train and y_train data sets
    x_train = []
    y_train = []

    for i in range(60, len(train_data)):
        x_train.append(train_data[i-60:i, 0])
        y_train.append(train_data[i, 0])

    # Convert the x_train and y_train to numpy arrays 
    x_train, y_train = np.array(x_train), np.array(y_train)

    # Reshape the data
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

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

    pass