import pandas as pd
import numpy as np

# For reading stock data from yahoo
# from pandas_datareader.data import DataReader
from sklearn.model_selection import GridSearchCV
import yfinance as yf

# Scale the data
from sklearn.preprocessing import MinMaxScaler

# Keras with the model
from scikeras.wrappers import KerasClassifier, KerasRegressor
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf

# For time stamps   
import datetime as dt

# Scaling the dataset
scaler = MinMaxScaler(feature_range=(0, 1))

def load_stock_data(stock_symbol, start_date, end_date):
    # Download stock data
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

    # Keep only 'Close' price
    dataset = stock_data[['Close']].values
    return dataset

def preprocess_data(dataset, lookback):
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
 
    # Convert the x_train and y_train to numpy arrays 
    x_train, y_train = np.array(x_train), np.array(y_train)

    # Reshape the data
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    #To Test **
    # Create the data sets x_test and y_test
    x_test = []
    y_test = dataset[training_data_len:, :]

    for i in range(60, len(test_data)):
        x_test.append(test_data[i-60:i, 0])

    # Convert the data to a numpy array
    x_test = np.array(x_test)

    # Reshape the data
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

    return x_train, y_train, x_test, y_test

# Define the LSTM network architecture
def build_lstm_model(neurons_firstLayer, neurons_secondLayer, n_steps, activation, optimizer, dropout_rate, firstDensity, secondDensity):

    model = Sequential()
    #model.add(LSTM(units=neurons_firstLayer, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(units=neurons_firstLayer, return_sequences=True, input_shape=(n_steps, 1)))
    model.add(Dropout(dropout_rate))

    model.add(LSTM(units=neurons_secondLayer, return_sequences=False))
    model.add(Dropout(dropout_rate))

    model.add(Dense(firstDensity, activation=activation))
    model.add(Dense(secondDensity, activation=activation))

    # Compile the model
    model.compile(loss='mean_squared_error', optimizer=optimizer)
    return model

def getPredictions(dataset, lookback=60, dropout_rate=0.2, epochs=10):
    if pd.isna(dataset).any() or len(dataset) == 0:
        raise TypeError("Dataset must have values")

    x_train, y_train, x_test, y_test = preprocess_data(dataset, lookback)

    # define the grid search parameters
    param_grid = {
        # Classifier parameters
        'batch_size': range(20, 30, 5),
        'epochs': range(10, 70, 10),

        # Model parameters
        'model__neurons_firstLayer': range(64, 512, 64),
        'model__neurons_secondLayer': range(32, 256, 32),
        'model__n_steps': [lookback], # x_train.shape[1],
        'model__optimizer': ['SGD', 'RMSprop', 'Adagrad', 'Adadelta', 'Adam', 'Adamax', 'Nadam'],
        # 'model__activation':['relu', 'tanh', 'sigmoid', 'linear','swish','softmax'],
        'model__activation':['relu', 'softmax'],
        'model__dropout_rate': [dropout_rate],
        'model__firstDensity': range(10, 50, 10),
        'model__secondDensity':  range(10, 50, 10)
    }

    # Build the model
    # model = build_lstm_model(neurons_firstLayer, neurons_secondLayer, n_steps,  optimizer, activation, dropout_rate, firstDensity, secondDensity)
    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    # model = KerasClassifier(build_fn=build_lstm_model)
    # Use KerasRegressor for regression task
    model = KerasRegressor(build_fn=build_lstm_model, verbose=0)

    grid = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=3,                   # Cross-validation with 3 folds
        refit=False,            # Refit the best model on the whole dataset
        scoring="accuracy",     # Use MSE as the scoring metric
        n_jobs = -1,
        error_score='raise'     # To display errors
    )

    print(x_train)
    print(y_train)
 
    # Train the model
    grid_result = grid.fit(
        x_train, 
        y_train,
        # batch_size=1, 
        # epochs=epochs,
        callbacks=[early_stop],
        verbose=1
    )

    return
 
    # Get the models predicted price values
    predictions_model = model.predict(x_test)
    predictions_model = scaler.inverse_transform(predictions_model)

    # Assuming y_test are the actual values and y_pred are the predicted values
    mse = mean_squared_error(y_test, predictions_model)
    rmse = np.sqrt(np.mean(((predictions_model - y_test) ** 2)))
    #rmse = root_mean_squared_error(y_test, predictions_model)
    mae = mean_absolute_error(y_test, predictions_model)
    r2 = r2_score(y_test, predictions_model)

    # Get best model
    bestRFModel = grid_result.best_estimator_

    #Create predictions
    predictions_grid = bestRFModel.predict(x_test)

    # summarize results
    # print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    best_score = grid_result.best_score_
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    rmse_grid = np.sqrt(np.mean(((predictions_grid - y_test) ** 2)))
    mae_grid = mean_absolute_error(y_test, predictions_grid)
    r2_grid = r2_score(y_test, predictions_grid)

    params = grid_result.cv_results_['params']
    # for mean, stdev, param in zip(means, stds, params):
    #     print("%f (%f) with: %r" % (mean, stdev, param))

    return {
        'model' :{
            'predictions': predictions_model,
            mse: means,
            rmse: rmse,
            mae: mae,
            r2: r2
        },
        'grid':{
            'predictions': predictions_grid,
            best_score : best_score,
            mse: means,
            rmse: rmse_grid,
            mae: mae_grid,
            r2: r2_grid,
            stds: stds,
            params: params
        }
    }

stock = 'AAPL'
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365*5)

dataset = load_stock_data(stock, start_date, end_date)
getPredictions(dataset)
