from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import numpy as np


def train_model(env) -> PPO:
    vec_env = DummyVecEnv([lambda: env])
    policy_kwargs = dict(net_arch=[dict(pi=[128, 128], vf=[128, 128])])
    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        tensorboard_log="./ppo_trading_tensorboard/",
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=256,
        n_epochs=20,
        gamma=0.99,
        policy_kwargs=policy_kwargs,
        ent_coef=0.05
    )
    model.learn(total_timesteps=300_000)
    return model


def test_model(model: PPO, env) -> None:
    obs = env.reset()
    done = False
    total_reward = 0.0
    while not done:
        action, _states = model.predict(obs, deterministic=False)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        print(
            f"Step: {env.current_step}, Action: {action}, Reward: {reward}, Portfolio Value: {info['portfolio_value']}")
    print(f"Total reward during testing: {total_reward}")
