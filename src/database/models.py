from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base, as_declarative
from sqlalchemy.orm import sessionmaker

from src.core_service.settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

Base = declarative_base()


class BtcUsdt(Base):
    __tablename__ = "btc_usdt"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, unique=True, nullable=False)
    utc_time = Column(DateTime, unique=True, nullable=False)
    msc_time = Column(DateTime, unique=True, nullable=False)
    open_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

