import pandas as pd
import gym
import numpy as np
from typing import Tuple


class TradingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, data: pd.DataFrame, window_size: int = 168):
        super(TradingEnv, self).__init__()

        if not isinstance(data, pd.DataFrame):
            raise ValueError("data должен быть pandas DataFrame")

        self.data = data.reset_index(drop=True)
        self.window_size = window_size
        self.current_step = self.window_size

        self.num_features = 9 + 2

        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.window_size, self.num_features),
            dtype=np.float32
        )

        self.action_space = gym.spaces.Discrete(3)

        self.initial_balance = 1000.0
        self.balance = self.initial_balance
        self.position = 0.0

        self.last_portfolio_value = self.initial_balance

        self.transaction_fee_percent = 0.001

    def reset(self) -> np.ndarray:
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.position = 0.0
        self.last_portfolio_value = self.balance + self.position * self.data.iloc[self.current_step]['close_price']
        observation = self._get_observation()
        return observation

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        current_price = self.data.iloc[self.current_step]['close_price']

        penalty = 0.0

        if action == 1:
            if self.balance > 0:
                btc_bought = (self.balance / current_price) * (1 - self.transaction_fee_percent)
                self.position += btc_bought
                self.balance = 0.0
            else:
                penalty = -1.0

        elif action == 2:
            if self.position > 0:
                usd_gained = self.position * current_price * (1 - self.transaction_fee_percent)
                self.balance += usd_gained
                self.position = 0.0
            else:
                penalty = -1.0

        elif action == 0:
            penalty = -1.0

        portfolio_value = self.balance + self.position * current_price

        profit = portfolio_value - self.last_portfolio_value

        reward = profit + penalty

        if profit > 0:
            reward += profit * 0.01  #

        self.last_portfolio_value = portfolio_value

        self.current_step += 1
        done = self.current_step >= len(self.data) - 1

        observation = self._get_observation()

        info = {
            'balance': self.balance,
            'position': self.position,
            'portfolio_value': portfolio_value
        }

        return observation, reward, done, info

    def _get_observation(self) -> np.ndarray:
        obs = self.data.iloc[self.current_step - self.window_size:self.current_step][
            [
                'open_price',
                'close_price',
                'high_price',
                'low_price',
                'volume',
                'ma_7',
                'ma_21',
                'std_7',
                'rsi_14'
            ]
        ].values

        if len(obs) < self.window_size:
            padding = np.zeros((self.window_size - len(obs), obs.shape[1]))
            obs = np.vstack((padding, obs))

        # Добавляем баланс и позицию к наблюдениям
        additional_features = np.array([[self.balance, self.position]] * self.window_size)
        obs = np.hstack((obs, additional_features))

        return obs.astype(np.float32)
