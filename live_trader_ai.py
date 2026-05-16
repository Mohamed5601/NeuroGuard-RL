import time
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

# --- إعدادات البوت ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '30m'     # يجب أن يطابق فريم التدريب
WINDOW_SIZE = 50      # يجب أن يطابق نافذة التدريب
TRADE_AMOUNT_USDT = 50 # حجم الصفقة بالدولار
MOCK_MODE = True      # True = تداول وهمي للتجربة | False = تداول حقيقي بأموالك

# --- إصلاح المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from data.processor import DataProcessor
    from executor.binance_connector import BinanceConnector 
    # تأكد من وجود binance_connector.py في مجلد executor
    # أو سنستخدم ccxt مباشرة إذا لم يكن جاهزاً
except ImportError:
    print("⚠️ جاري استخدام ccxt مباشرة لعدم العثور على الموصل...")
    import ccxt

class AITrader:
    def __init__(self):
        print("🤖 Initializing AI Trader...")
        
        # 1. تحميل الموديل والذاكرة
        model_path = "models/backtest_model.zip"
        stats_path = "models/backtest_vec_normalize.pkl"
        
        if not os.path.exists(model_path) or not os.path.exists(stats_path):
            print("❌ Critical Error: Model files not found! Run training first.")
            sys.exit(1)
            
        self.model = PPO.load(model_path)
        
        # خدعة لتحميل إحصائيات التطبيع بدون بيئة كاملة
        # ننشئ بيئة فارغة فقط لتحميل الـ Stats
        self.processor = DataProcessor()
        # نسحب عينة صغيرة جداً فقط لتهيئة الهيكل
        dummy_df = self.processor.download_data(SYMBOL, TIMEFRAME, limit=100)
        dummy_df = self.processor._add_indicators(dummy_df)
        dummy_df.dropna(inplace=True)
        # نحذف timestamp كما فعلنا في spot_env
        if 'timestamp' in dummy_df.columns: dummy_df = dummy_df.drop(columns=['timestamp'])
        
        from gym_env.spot_env import SpotTradingEnv
        dummy_env = DummyVecEnv([lambda: SpotTradingEnv(dummy_df, window_size=WINDOW_SIZE)])
        self.norm_env = VecNormalize.load(stats_path, dummy_env)
        self.norm_env.training = False # تجميد التحديث
        self.norm_env.norm_reward = False
        
        # حالة المحفظة المحلية (للمحاكاة الوهمية)
        self.is_holding = False
        self.entry_price = 0.0
        
        # الاتصال بـ Binance (لجلب الأسعار فقط حالياً)
        self.exchange = getattr(import_ccxt(), 'binance')({'enableRateLimit': True})
        
    def get_latest_data(self):
        # نحتاج آخر (WINDOW_SIZE) شمعة لندخلها للموديل
        # نسحب أكثر قليلاً (100) لنضمن دقة المؤشرات (RSI, MACD)
        limit = 100
        ohlcv = self.exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # إضافة المؤشرات
        df = self.processor._add_indicators(df)
        
        # تنظيف وحذف التايم ستامب
        df.dropna(inplace=True)
        processing_df = df.drop(columns=['timestamp'], errors='ignore')
        
        # التأكد من أن لدينا بيانات كافية
        if len(processing_df) < WINDOW_SIZE:
            return None, 0
            
        # نأخذ آخر نافذة فقط
        window_data = processing_df.iloc[-WINDOW_SIZE:].copy()
        
        # إعداد المدخلات الإضافية (Position + PnL)
        # ملاحظة: هنا نغذي الموديل بحالتنا الحالية
        in_position = 1.0 if self.is_holding else 0.0
        pnl = 0.0
        current_price = df['close'].iloc[-1]
        
        if self.is_holding:
            pnl = (current_price / self.entry_price) - 1
            
        position_col = np.full((WINDOW_SIZE, 1), in_position, dtype=np.float32)
        pnl_col = np.full((WINDOW_SIZE, 1), pnl, dtype=np.float32)
        
        # التجميع النهائي للمصفوفة
        obs = np.hstack((window_data.values, position_col, pnl_col))
        obs = np.nan_to_num(obs, nan=0.0)
        
        return obs, current_price

    def normalize_observation(self, obs):
        # تطبيق نفس معادلات التطبيع التي تعلمها البوت
        return self.norm_env.normalize_obs(obs)

    def run(self):
        print(f"🚀 AI Trader Running on {SYMBOL} [{TIMEFRAME}]")
        print(f"🛡️ Mode: {'MOCK (Safe)' if MOCK_MODE else 'REAL MONEY (Danger)'}")
        print("Waiting for next candle update...")
        
        while True:
            try:
                # 1. تجهيز البيانات
                obs_raw, current_price = self.get_latest_data()
                if obs_raw is None:
                    print("⚠️ Not enough data yet, waiting...")
                    time.sleep(60)
                    continue

                # 2. التطبيع
                obs_norm = self.normalize_observation(obs_raw)
                
                # 3. سؤال الذكاء الاصطناعي
                action, _ = self.model.predict(obs_norm, deterministic=True)
                
                # 4. ترجمة القرار
                signal = "HOLD"
                if action == 1: signal = "BUY"
                elif action == 2: signal = "SELL"
                
                # طباعة الحالة
                timestamp = datetime.now().strftime("%H:%M:%S")
                status = "🟢 HOLDING" if self.is_holding else "⚪ USDT"
                print(f"[{timestamp}] Price: {current_price:.2f} | Status: {status} | 🧠 AI says: {signal}")

                # 5. التنفيذ (Mock Mode)
                if signal == "BUY" and not self.is_holding:
                    print(f"   🛒 OPENING BUY POSITION @ {current_price}")
                    self.is_holding = True
                    self.entry_price = current_price
                    # (هنا سنضع كود الشراء الحقيقي لاحقاً)
                    
                elif signal == "SELL" and self.is_holding:
                    profit = ((current_price - self.entry_price) / self.entry_price) * 100
                    print(f"   💰 CLOSING SELL POSITION @ {current_price} | PnL: {profit:.2f}%")
                    self.is_holding = False
                    self.entry_price = 0.0
                    # (هنا سنضع كود البيع الحقيقي لاحقاً)

                # الانتظار قليلاً (نصف دقيقة) لتجنب الضغط على الـ API
                # في النسخة المتقدمة سننتظر إغلاق الشمعة
                time.sleep(30) 

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)

def import_ccxt():
    import ccxt
    return ccxt

if __name__ == "__main__":
    bot = AITrader()
    bot.run()