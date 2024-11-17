from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta
from src.database.models import BtcUsdt, engine


def prepare_df(df: pd.DataFrame):
    """Подготовка данных перед вставкой в базу."""
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


def fetch_historical_data(symbol, timeframe, start_date):
    """Загрузка данных начиная с указанной даты."""
    exchange = ccxt.binance()
    limit = 1000
    start_time = exchange.parse8601(start_date)  # Начальная дата
    end_time = exchange.milliseconds()  # Текущая дата

    print(f"Начало загрузки данных для {symbol} с {pd.to_datetime(start_time, unit='ms')}...")

    session_factory = sessionmaker(engine)
    session = scoped_session(session_factory)

    while start_time < end_time:
        try:
            # Тут ограничение
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=start_time, limit=limit)
            if not ohlcv:
                print("Данные закончились.")
                break

            df = pd.DataFrame(ohlcv,
                              columns=['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            df = prepare_df(df)

            # Инсертим в базу
            for i in range(len(df)):
                obj_data = df.iloc[i].to_dict()
                try:
                    obj = BtcUsdt(**obj_data)
                    session.add(obj)
                except IntegrityError:
                    session.rollback()  # Может дублирование, по тупом присылает
                    print(f"Дубликат записи: {obj_data['msc_time']}")

            session.commit()
            start_time = ohlcv[-1][0] + 1

            print(f"Загружено {len(ohlcv)} строк, текущая дата: {pd.to_datetime(start_time, unit='ms')}")
            time.sleep(0.5)  # Пауза из-за API
        except Exception as e:
            session.rollback()
            print(f"Ошибка: {e}")
            break

    session.close()
    print("Загрузка завершена.")


def main():
    symbol = 'BTC/USDT'
    timeframe = '1h'
    start_date = '2017-09-01T00:00:00Z'

    fetch_historical_data(symbol, timeframe, start_date)


if __name__ == "__main__":
    main()
