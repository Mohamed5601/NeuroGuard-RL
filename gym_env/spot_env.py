import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class SpotTradingEnv(gym.Env):
    
    def __init__(self, df, window_size=50, initial_balance=1000000):
        super(SpotTradingEnv, self).__init__()
        
        # 1. تنظيف البيانات فوراً (إصلاح مشكلة الأبعاد)
        self.df = df.reset_index(drop=True)
        
        # حذف عمود الزمن لأنه يسبب مشاكل في الحسابات
        if 'timestamp' in self.df.columns:
            self.df = self.df.drop(columns=['timestamp'])
            
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.fee = 0.001  # عمولة 0.1% (باينانس)
        
        # 0: Hold (انتظار), 1: Buy (شراء), 2: Sell (بيع)
        self.action_space = spaces.Discrete(3) 

        # حساب حجم المدخلات بدقة
        # (عدد المؤشرات الفنية + 2 ميزات المحفظة)
        num_features = self.df.shape[1] 
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, 
            shape=(window_size, num_features + 2), 
            dtype=np.float32
        )
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # نبدأ دائماً بعد انقضاء نافذة البيانات الأولى
        self.current_step = self.window_size
        
        self.balance = self.initial_balance
        self.shares_held = 0  
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance 
        
        return self._get_observation(), {}

    def step(self, action):
        self.current_step += 1
        
        # الحصول على السعر الحالي (تأكدنا من حذف timestamp لذا الأرقام سليمة)
        current_price = self.df['close'].iloc[self.current_step]
        
        prev_net_worth = self.net_worth
        
        # تنفيذ الأوامر
        # 1. الشراء (بكل الرصيد)
        if action == 1 and self.shares_held == 0:
            amount_to_buy = self.balance * (1 - self.fee)
            self.shares_held = amount_to_buy / current_price
            self.balance = 0
            
        # 2. البيع (كل الكمية)
        elif action == 2 and self.shares_held > 0:
            amount_sold = self.shares_held * current_price
            self.balance += amount_sold * (1 - self.fee)
            self.shares_held = 0
            
        # تحديث قيمة المحفظة
        self.net_worth = self.balance + (self.shares_held * current_price)
        self.max_net_worth = max(self.net_worth, self.max_net_worth)
        
        # --- 🧠 حساب المكافأة الذكية ---
        
        # أ) العائد اللوغاريتمي (أساس الربح)
        reward = np.log(self.net_worth / prev_net_worth) * 100
        
        # ب) عقوبة التراجع (Drawdown Penalty)
        # نعاقبه إذا نزل عن أعلى قمة وصل لها
        drawdown = (self.max_net_worth - self.net_worth) / self.max_net_worth
        if drawdown > 0:
            reward -= (drawdown * 0.1)

        # ج) عقوبة "الحركة الزائدة" (Overtrading Penalty) - هام لفريم 30 دقيقة
        # نخصم مبلغ تافه عند كل عملية بيع أو شراء لنجبره على الثبات وانتظار الفرصة
        if action in [1, 2]:
            reward -= 0.02 

        # شروط التوقف
        terminated = False
        
        # الإفلاس (خسارة 50%)
        if self.net_worth <= self.initial_balance * 0.5:
            terminated = True
            reward -= 10 # عقوبة قاسية
            
        # نهاية البيانات
        if self.current_step >= len(self.df) - 1:
            terminated = True

        info = {
            'net_worth': self.net_worth, 
            'profit': self.net_worth - self.initial_balance
        }
        
        return self._get_observation(), reward, terminated, False, info

    def _get_observation(self):
        # قص البيانات للنافذة الحالية
        obs_df = self.df.iloc[self.current_step - self.window_size : self.current_step].copy()
        
        # إضافة ميزات المحفظة
        in_position = 1.0 if self.shares_held > 0 else 0.0
        
        unrealized_pnl = 0.0
        if self.shares_held > 0:
            # ربح الصفقة المفتوحة حالياً
            unrealized_pnl = (self.net_worth / self.max_net_worth) - 1

        # توسيع القيم لتناسب حجم المصفوفة (Matrix Broadcasting)
        position_col = np.full((self.window_size, 1), in_position, dtype=np.float32)
        pnl_col = np.full((self.window_size, 1), unrealized_pnl, dtype=np.float32)
        
        # دمج كل شيء: [بيانات السوق | هل أنا شاري؟ | هل أنا كسبان؟]
        obs = np.hstack((obs_df.values, position_col, pnl_col))
        
        # تنظيف أي قيم غير منطقية (NaN/Inf)
        obs = np.nan_to_num(obs, nan=0.0)
        
        return obs.astype(np.float32)