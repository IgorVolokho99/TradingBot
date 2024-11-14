from pprint import pprint
from sqlalchemy.orm import sessionmaker, scoped_session

import ccxt
import pandas as pd
import pytz
import time

from src.database.models import BtcUsdt, engine


def prepare_df(df: pd.DataFrame):
    df['utc_time'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['msc_time'] = pd.to_datetime(df['timestamp'] + 3600000 * 3, unit='ms')
    df['timestamp'] = df['timestamp'].astype(str)
    df['utc_time'] = df['utc_time'].dt.to_pydatetime()
    df['msc_time'] = df['msc_time'].dt.to_pydatetime()
    df['open_price'] = df['open_price'].astype(float)
    df['close_price'] = df['close_price'].astype(float)
    df['high_price'] = df['high_price'].astype(float)
    df['low_price'] = df['low_price'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df


def fetch_historical_data(symbol, timeframe, since, save_file=None):
    exchange = ccxt.binance()
    all_data = []
    limit = 1000
    print(f"Начало загрузки данных для {symbol} с {pd.to_datetime(since, unit='ms')}...")

    while since < exchange.milliseconds():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=limit)
            if not ohlcv:
                break
            session_factory = sessionmaker(engine)
            session = scoped_session(session_factory)
            all_data.extend(ohlcv)
            df = pd.DataFrame(ohlcv,
                              columns=['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])

            df = prepare_df(df)

            since = ohlcv[-1][0] + 1
            for i in range(len(df)):
                obj = BtcUsdt(**(df.iloc[i].to_dict()))
                session.add(obj)
                session.commit()

            print(f"Загружено {len(all_data)} строк, текущая дата: {pd.to_datetime(since, unit='ms')}")
            pprint(all_data)
            time.sleep(0.5)
        except Exception as e:
            print(f"Ошибка: {e}")
            break


symbol = 'BTC/USDT'
timeframe = '1h'
start_date = '2017-09-01T00:00:00Z'
start_time = ccxt.Exchange().parse8601(start_date)
save_path = 'btc_usdt_hourly_with_timezones.csv'

data = fetch_historical_data(symbol, timeframe, start_time, save_file=save_path)

print(data.head())
