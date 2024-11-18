import pandas as pd
from sqlalchemy import create_engine

from src.core_service.settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB


def load_data():
    """
    Загружает данные из базы данных, добавляет технические индикаторы и возвращает их в виде pandas DataFrame.
    """
    db_username = POSTGRES_USER
    db_password = POSTGRES_PASSWORD
    db_host = POSTGRES_HOST
    db_port = POSTGRES_PORT
    db_name = POSTGRES_DB
    table_name = 'btc_usdt'

    connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'

    engine = create_engine(connection_string)

    query = f"""
    SELECT
        utc_time AS date,
        open_price,
        close_price,
        high_price,
        low_price,
        volume
    FROM
        {table_name}
    ORDER BY
        utc_time ASC
    """

    data = pd.read_sql(query, engine)

    engine.dispose()

    print(f"Загружено {len(data)} записей.")

    data['date'] = pd.to_datetime(data['date'])
    data.sort_values('date', inplace=True)
    data.reset_index(drop=True, inplace=True)

    data = add_technical_indicators(data)

    return data


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    data['ma_7'] = data['close_price'].rolling(window=7).mean()
    data['ma_21'] = data['close_price'].rolling(window=21).mean()

    data['std_7'] = data['close_price'].rolling(window=7).std()

    data['rsi_14'] = compute_rsi(data['close_price'], window=14)

    data.fillna(method='bfill', inplace=True)

    return data


def compute_rsi(series: pd.Series, window: int) -> pd.Series:
    delta = series.diff()
    up, down = delta.clip(lower=0), -delta.clip(upper=0)
    gain = up.rolling(window=window).mean()
    loss = down.rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi.fillna(0, inplace=True)
    return rsi
