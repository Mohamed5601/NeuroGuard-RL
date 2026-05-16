import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gym_env.spot_env import SpotTradingEnv

def run_simulation():
    print("--- 🔮 Starting Out-of-Sample Simulation ---")
    
    data_path = "data/2024_simulation_data.parquet"
    model_path = "models/backtest_model.zip"
    stats_path = "models/backtest_vec_normalize.pkl"

    if not os.path.exists(data_path):
        print("❌ Run train_backtest.py first!")
        return

    # 1. Load Data
    df_test = pd.read_parquet(data_path)
    print(f"📊 Testing on {len(df_test)} candles (Unseen Data)")

    # 2. Reconstruct Environment
    env = DummyVecEnv([lambda: SpotTradingEnv(df_test, initial_balance=1000)])
    
    # Load Stats
    env = VecNormalize.load(stats_path, env)
    env.training = False     # FREEZE UPDATE
    env.norm_reward = False

    # Load Brain
    model = PPO.load(model_path)

    # 3. Run
    obs = env.reset()
    done = False
    balance_history = [] 

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        balance_history.append(info[0]['net_worth'])
        if done[0]: break

    # 4. Results
    final_balance = balance_history[-1]
    roi = ((final_balance - 1000) / 1000) * 100

    print(f"🏁 Final Balance: ${final_balance:.2f} (ROI: {roi:.2f}%)")
    
    plt.plot(balance_history)
    plt.title(f"Simulation ROI: {roi:.2f}%")
    plt.savefig("simulation_result.png")
    print("🖼️ Chart saved.")

if __name__ == "__main__":
    run_simulation()