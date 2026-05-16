import pandas as pd
from gym_env.spot_env import SpotTradingEnv
from data.processor import DataProcessor

print("--- 🏟️ Testing The Gym Environment ---")

# 1. تجهيز بيانات للتجربة
print("... Loading Data ...")
processor = DataProcessor()
# هنسحب داتا صغيرة للتجربة
df = processor.prepare_multitimeframe_data('BTC/USDT', start_limit=500)

if df.empty:
    print("❌ Error: No data fetched. Check your internet or processor.")
    exit()

# 2. إنشاء البيئة
print("... Initializing Environment ...")
env = SpotTradingEnv(df, window_size=50)

# 3. تشغيل حلقة عشوائية (Random Agent)
obs, info = env.reset()
done = False
total_reward = 0

print("\n🎲 Starting Random Simulation...")

steps = 0
while not done and steps < 100:
    # اختار أكشن عشوائي (0, 1, أو 2)
    action = env.action_space.sample()
    
    # نفذ الخطوة
    obs, reward, terminated, truncated, info = env.step(action)
    
    total_reward += reward
    done = terminated or truncated
    steps += 1
    
    if steps % 10 == 0:
        print(f"Step {steps}: Action={action}, Reward={reward:.4f}, Net Worth={info['net_worth']:.2f}")

print(f"\n✅ Simulation Finished!")
print(f"Final Net Worth: ${info['net_worth']:.2f}")
print("The environment is healthy and ready for AI training.")