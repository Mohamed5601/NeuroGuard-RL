import sys
import os
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback

# إضافة مسار المشروع عشان يشوف الملفات التانية
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gym_env.spot_env import SpotTradingEnv
from data.processor import DataProcessor

def train_model():
    print("--- 🧠 Starting AI Training Session ---")

    # 1. تحميل البيانات (The Fuel)
    print("... Loading Training Data ...")
    processor = DataProcessor()
    
    # هنسحب داتا تاريخية كبيرة للتدريب (مثلاً 2000 شمعة كبداية)
    # ملحوظة: في الوضع الحقيقي بنحتاج عشرات الآلاف، بس دي للتجربة
    df = processor.prepare_multitimeframe_data('BTC/USDT', start_limit=3000)
    
    if df.empty:
        print("❌ Critical Error: No data found for training.")
        return

    # 2. تجهيز البيئة (The Gym)
    print("... Setting up the Environment ...")
    
    # الدالة دي عشان ننشئ البيئة جوه الـ Vectorizer
    def make_env():
        return SpotTradingEnv(df, window_size=50, initial_balance=1000)

    # DummyVecEnv: بيخلينا نقدر نشغل كذا بيئة في نفس الوقت (توازي)
    env = DummyVecEnv([make_env])
    
    # VecNormalize: سر خطير 🛑
    # بيقوم بضبط المكافآت والمدخلات عشان تكون حول الصفر (Normalization)
    # ده بيخلي التدريب أسرع واستقراره أعلى بكتير
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.)

    # 3. إعداد الموديل (The Brain)
    print("... Initializing PPO Agent ...")
    
    # التأكد من وجود كارت شاشة
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ Training on: {device.upper()}")

    model = PPO(
        "MlpPolicy",      # نوع الشبكة العصبية (Multi-Layer Perceptron)
        env,
        verbose=1,        # طباعة التفاصيل أثناء التدريب
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        device=device     # استخدام GPU لو متاح
    )

    # 4. بدء التدريب (The Workout)
    print("\n🏋️‍♂️ Training Started... (This may take a while)")
    
    # عدد الخطوات الإجمالي (للتجربة هنخليها 100 ألف، للحقيقي بتبقى ملايين)
    TOTAL_TIMESTEPS = 100_000 
    
    model.learn(total_timesteps=TOTAL_TIMESTEPS, progress_bar=True)
    print("✅ Training Finished!")

    # 5. الحفظ (Save Implementation)
    save_path = os.path.join(os.path.dirname(__file__), "ppo_crypto_trader")
    stats_path = os.path.join(os.path.dirname(__file__), "vec_normalize.pkl")

    # حفظ مخ الموديل
    model.save(save_path)
    # حفظ إحصائيات البيئة (مهم جداً عشان التداول الحي)
    env.save(stats_path)
    
    print(f"\n💾 Model saved to: {save_path}.zip")
    print(f"💾 Stats saved to: {stats_path}")

if __name__ == "__main__":
    train_model()