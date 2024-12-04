import numpy as np


def generate_signals(predicted_prices, actual_prices):
    # Calculate the difference between consecutive predicted prices
    predictions_diff = np.diff(predicted_prices, axis=0)

    # Initialize signals array (same length as predicted prices minus the first)
    signals = np.zeros(len(predictions_diff))

    # Generate Buy (1) and Sell (-1) signals
    for i in range(1, len(predictions_diff)):
        # Buy signal: if the predicted price is higher than the current price
        if predictions_diff[i] > 0:
            signals[i] = 1  # Buy
        # Sell signal: if the predicted price is lower than the current price
        elif predictions_diff[i] < 0:
            signals[i] = -1  # Sell
    
    # Return buy/sell signals aligned with the predicted data
    return signals

def backtest_strategy(predicted_prices, actual_prices, initial_balance=10000):
    # Generate Buy (1) and Sell (-1) signals based on predicted prices
    signals = generate_signals(predicted_prices, actual_prices)

    # Initialize variables
    cash = initial_balance  # Start with a set balance
    stock_held = 0  # Initially, no stock is held
    portfolio_value = []  # To track the portfolio value over time

    for i in range(len(signals)):
        if signals[i] == 1:  # Buy signal
            if cash > 0:
                # Buy the stock with all available cash
                stock_held = cash / actual_prices[i]
                cash = 0
                print(f"Buying at price {actual_prices[i]}")
        
        elif signals[i] == -1:  # Sell signal
            if stock_held > 0:
                # Sell all the stock
                cash = stock_held * actual_prices[i]
                stock_held = 0
                print(f"Selling at price {actual_prices[i]}")

        # Calculate total portfolio value (cash + value of held stock)
        portfolio_value.append(cash + stock_held * actual_prices[i])

    # Final portfolio value
    final_portfolio_value = cash + stock_held * actual_prices[-1]
    
    return final_portfolio_value, portfolio_value

def generate_signals_with_threshold(predicted_prices, actual_prices, threshold=0.01):
    predictions_diff = np.diff(predicted_prices, axis=0)
    signals = np.zeros(len(predictions_diff))
    
    # Only generate buy/sell signals when the price change exceeds the threshold
    for i in range(1, len(predictions_diff)):
        pct_change = (predicted_prices[i] - predicted_prices[i-1]) / predicted_prices[i-1]

        if pct_change > threshold:  # Buy signal
            signals[i] = 1
        elif pct_change < -threshold:  # Sell signal
            signals[i] = -1

    return signals

grid_result, x_test, y_test = [], [], []

# Predicted stock prices (example from your LSTM model)
predicted_prices = grid_result.best_estimator_.predict(x_test)

# Actual stock prices
actual_prices = y_test.flatten()  # Assuming y_test contains actual values

# Run the backtest and get final portfolio value
final_value, portfolio_values = backtest_strategy(predicted_prices, actual_prices)

print(f"Final portfolio value: {final_value}")