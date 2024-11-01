import time

import pandas as pd
import numpy as np
from binance.client import Client

from settings import API_KEY, API_SECRET

client = Client(API_KEY, API_SECRET)

short_window = 10
long_window = 50
target_profit = 1.05
stop_loss = 0.98


def fetch_data(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                         'taker_buy_quote_asset_volume', 'ignore'])
    data['close'] = data['close'].astype(float)
    return data


def calculate_moving_averages(data, short_window, long_window):
    data['SMA10'] = data['close'].rolling(window=short_window).mean()
    data['SMA50'] = data['close'].rolling(window=long_window).mean()
    return data


def generate_signals(data):
    data['signal'] = np.where(data['SMA10'] > data['SMA50'], 1, 0)
    data['position'] = data['signal'].diff()
    return data


def trading_strategy():
    data = fetch_data()
    data = calculate_moving_averages(data, short_window, long_window)
    data = generate_signals(data)

    initial_price = None

    for i in range(1, len(data)):
        current_price = data['close'][i]

        if data['position'][i] == 1 and initial_price is None:
            initial_price = current_price
            print(f"Сигнал на покупку по цене: {initial_price}")

        elif initial_price:
            if current_price >= initial_price * target_profit:
                print(f"Фиксация прибыли по цене: {current_price}")
                initial_price = None

            elif current_price <= initial_price * stop_loss:
                print(f"Стоп-лосс сработал по цене: {current_price}")
                initial_price = None

        elif data['position'][i] == -1 and initial_price:
            print(f"Сигнал на продажу по цене: {current_price}")
            initial_price = None


trading_strategy()
