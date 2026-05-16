import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
from datetime import datetime, timedelta
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

# إصلاح المسارات
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from gym_env.spot_env import SpotTradingEnv
    from data.processor import DataProcessor
except ImportError:
    sys.path.append(os.path.dirname(current_dir))
    from gym_env.spot_env import SpotTradingEnv
    from data.processor import DataProcessor

def run_long_simulation():
    print("--- 🌍 Starting REAL Long-Term Simulation (Last 90 Days) ---")
    
    # 1. حساب تاريخ البداية (منذ 90 يوم من الآن)
    # نحول التاريخ إلى Milliseconds لأن ccxt يتعامل بالمللي ثانية
    days_ago = 90
    since_timestamp = int((datetime.now() - timedelta(days=days_ago)).timestamp() * 1000)
    
    print(f"⏳ Downloading market data starting from {days_ago} days ago...")
    
    processor = DataProcessor()
    # نمرر since_timestamp لنسحب بيانات حديثة
    df_test = processor.download_data('BTC/USDT', '30m', limit=4000, since=since_timestamp)
    
    # إضافة المؤشرات
    df_test = processor._add_indicators(df_test)
    df_test.dropna(inplace=True)
    df_test.reset_index(drop=True, inplace=True)
    
    print(f"✅ Loaded {len(df_test)} candles.")
    print(f"📅 Period: {df_test['timestamp'].iloc[0]} -> {df_test['timestamp'].iloc[-1]}")

    # 2. تحميل الموديل والذاكرة
    model_path = "models/backtest_model.zip"
    stats_path = "models/backtest_vec_normalize.pkl"

    if not os.path.exists(model_path):
        print("❌ Error: Model not found!")
        return

    # إعداد البيئة
    env = DummyVecEnv([lambda: SpotTradingEnv(df_test, window_size=50, initial_balance=1000)])
    env = VecNormalize.load(stats_path, env)
    env.training = False     
    env.norm_reward = False

    model = PPO.load(model_path)

    # 3. التشغيل
    obs = env.reset()
    done = False
    
    portfolio_values = []
    buy_signals = 0
    sell_signals = 0
    
    print("\n🚀 Simulating Trades on 2024/2025 Data...")
    
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        
        if action == 1: buy_signals += 1
        elif action == 2: sell_signals += 1
        
        obs, reward, done, info = env.step(action)
        portfolio_values.append(info[0]['net_worth'])
        
        if done[0]: break

    # 4. النتائج
    final_balance = portfolio_values[-1]
    roi = ((final_balance - 1000) / 1000) * 100
    total_actions = buy_signals + sell_signals

    print("\n" + "="*40)
    print(f"🏁 RESULTS (Recent Market Data)")
    print("="*40)
    print(f"💵 Start Balance:  $1000.00")
    print(f"💰 Final Balance:  ${final_balance:.2f}")
    print(f"📈 ROI (Profit):   {roi:.2f}%")
    print(f"🔄 Total Actions:  {total_actions} (Buys + Sells)")
    print("="*40)

    # رسم بياني
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_values, label='AI Portfolio', color='green')
    plt.axhline(y=1000, color='r', linestyle='--', label='Start Balance')
    plt.title(f"AI Performance (Last 90 Days) - ROI: {roi:.2f}%")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("real_test_result.png")
    print("🖼️ Chart saved as 'real_test_result.png'")

if __name__ == "__main__":
    run_long_simulation()