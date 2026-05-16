import sys
import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

# --- 1. إصلاح المسارات السحري (لحل مشكلة ModuleNotFoundError) ---
current_dir = os.path.dirname(os.path.abspath(__file__)) # مسار models
root_dir = os.path.dirname(current_dir)              # مسار CRYPTOBOT الرئيسي
sys.path.append(root_dir)
# -----------------------------------------------------------

try:
    from gym_env.spot_env import SpotTradingEnv 
    from data.processor import DataProcessor
except ImportError as e:
    print(f"❌ خطأ: تأكد أن مجلد gym_env و data موجودين داخل {root_dir}")
    sys.exit(1)


def run_walk_forward_training():
    print("--- 🚀 Starting Smart Walk-Forward Training (30m Timeframe) ---")
    
    # --- 2. الإعدادات الاستراتيجية ---
    # فريم 30 دقيقة يحتاج بيانات أقل عدداً لكنها تغطي وقتاً أطول
    TRAIN_WINDOW = 3000   # 3000 شمعة نص ساعة = حوالي شهرين (كافية جداً للتعلم)
    TEST_WINDOW = 336     # اختبار أسبوع واحد (336 شمعة)
    STEP_SIZE = 336       # نتحرك أسبوع بأسبوع
    
    # نحتاج حوالي 15,000 شمعة لتغطية سنة كاملة من بيانات 30 دقيقة
    TOTAL_CANDLES = 20000 

    # --- 3. سحب البيانات ---
    processor = DataProcessor()
    # 💡 التغيير المهم: استخدام فريم 30 دقيقة
    full_df = processor.prepare_multitimeframe_data('BTC/USDT', base_timeframe='30m', start_limit=TOTAL_CANDLES)
    
    if len(full_df) < TRAIN_WINDOW + TEST_WINDOW:
        print("❌ البيانات غير كافية، حاول زيادة الـ limit في processor.py")
        return
    
    walk_forward_results = []
    
    # --- 4. مرحلة التأسيس (Initial Training) ---
    print("\n--- 🧠 جاري بناء النموذج الأولي (The Genesis Model) ---")
    initial_train_df = full_df.iloc[0:TRAIN_WINDOW].reset_index(drop=True)
    
    env = DummyVecEnv([lambda: SpotTradingEnv(initial_train_df, window_size=50)])
    norm_env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=10.)
    
    # 💡 التغيير الجوهري: إعدادات الذكاء "الرزينة" لتقليل العشوائية
    model = PPO(
        "MlpPolicy", 
        norm_env, 
        verbose=1, 
        device='cpu',
        
        # معدل تعلم هادئ: لكي لا ينسى الخبرات السابقة بسرعة
        learning_rate=0.0001, 
        
        # عشوائية منخفضة جداً: ليتوقف عن اللعب ويركز على الربح
        ent_coef=0.001,        
        
        # حجم باتش أكبر: قرارات مدروسة أكثر
        batch_size=128,        
        n_steps=2048,
        gamma=0.99
    )
    
    print("   ... جاري التدريب المكثف الأول ...")
    model.learn(total_timesteps=30000) # تدريب مبدئي قوي
    
    
    # --- 5. حلقة التعلم المستمر (The Loop) ---
    start_index = TRAIN_WINDOW 
    end_index = len(full_df) - TEST_WINDOW 
    
    for i in range(start_index, end_index, STEP_SIZE):
        
        # تقسيم البيانات
        train_start = i - TRAIN_WINDOW + STEP_SIZE
        train_end = i + STEP_SIZE
        test_end = i + STEP_SIZE + TEST_WINDOW
        
        current_train_df = full_df.iloc[train_start:train_end].reset_index(drop=True)
        test_df = full_df.iloc[train_end:test_end].reset_index(drop=True)

        print(f"\n--- 🔄 Cycle {int(i/STEP_SIZE)} | Period: {current_train_df['timestamp'].iloc[-1]} ---")

        # نقل الخبرة (Transfer Learning)
        new_train_env = DummyVecEnv([lambda: SpotTradingEnv(current_train_df, window_size=50)])
        new_norm_env = VecNormalize(new_train_env, norm_obs=True, norm_reward=False, clip_obs=10.)
        
        # نسخ احصائيات التطبيع (مهم جداً عشان البوت ما يتصدمش بالأسعار الجديدة)
        new_norm_env.obs_rms = norm_env.obs_rms
        new_norm_env.ret_rms = norm_env.ret_rms
        
        norm_env = new_norm_env
        model.set_env(norm_env)

        # تدريب سريع لتحديث المعلومات (Fine-tuning)
        model.learn(total_timesteps=10000, reset_num_timesteps=False, progress_bar=True)
        
        # الاختبار (Validation)
        test_env = DummyVecEnv([lambda: SpotTradingEnv(test_df, window_size=50)])
        eval_env = VecNormalize(test_env, norm_obs=True, norm_reward=False, clip_obs=10.)
        eval_env.obs_rms = norm_env.obs_rms # استخدام نفس مقاييس التدريب
        eval_env.training = False 

        obs = eval_env.reset()
        done = [False]
        while not done[0]:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = eval_env.step(action)
        
        # تسجيل النتائج
        final_balance = info[0]['net_worth']
        roi = ((final_balance - 1000000) / 1000000) * 100
        
        walk_forward_results.append({
            'date': test_df['timestamp'].iloc[0],
            'roi': roi,
            'balance': final_balance
        })
        
        # طباعة النتيجة بشكل ملون (اختياري)
        symbol = "✅" if roi > 0 else "🔻"
        print(f"   {symbol} Test Result: {roi:.2f}%")


    # --- 6. الحفظ والنهاية ---
    results_df = pd.DataFrame(walk_forward_results)
    print("\n--- 📊 Final Cumulative Results ---")
    print(results_df)
    
    total_roi = results_df['roi'].sum()
    print(f"\n📈 Total Strategy ROI (approx): {total_roi:.2f}%")

    print("\n💾 Saving Production Files...")
    if not os.path.exists(os.path.join(root_dir, "models")):
        os.makedirs(os.path.join(root_dir, "models"))
        
    model.save(os.path.join(root_dir, "models/backtest_model.zip"))
    norm_env.save(os.path.join(root_dir, "models/backtest_vec_normalize.pkl"))
    
    # حفظ بيانات المحاكاة المستقبلية
    # نأخذ آخر جزء لم يتدرب عليه كبيانات للمحاكاة
    simulation_data = full_df.iloc[-TEST_WINDOW:].reset_index(drop=True)
    
    data_dir = os.path.join(root_dir, "data")
    if not os.path.exists(data_dir): os.makedirs(data_dir)
        
    simulation_data.to_parquet(os.path.join(data_dir, "2024_simulation_data.parquet"))
    print("✅ Done! Ready for Live Simulation.")

if __name__ == "__main__":
    run_walk_forward_training()