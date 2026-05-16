class RiskEngine:
    def __init__(self, daily_loss_limit=0.03):
        """
        daily_loss_limit: 0.03 تعني 3%
        """
        self.daily_loss_limit = daily_loss_limit
        self.initial_balance = None
        self.is_kill_switch_active = False

    def set_initial_balance(self, balance):
        """
        يتم استدعاؤها في بداية اليوم لتسجيل الرصيد الافتتاحي
        """
        self.initial_balance = balance
        self.is_kill_switch_active = False # إعادة ضبط المفتاح

    def check_health(self, current_balance):
        """
        تعيد True لو الوضع آمن
        تعيد False لو فعلنا وقف الخسارة الإجباري
        """
        if self.is_kill_switch_active:
            return False, "⛔ KILL SWITCH ACTIVATED PREVIOUSLY"

        if self.initial_balance is None:
            # لم يتم تحديد رصيد البداية، نفترض الأمان مؤقتاً
            return True, "✅ No initial balance set"

        # حساب نسبة الخسارة
        # مثال: 95 - 100 = -5 ... -5 / 100 = -0.05 (خسارة 5%)
        pnl_percent = (current_balance - self.initial_balance) / self.initial_balance

        # لو الخسارة (بالسالب) أقل من الحد المسموح (سالب 3%)
        if pnl_percent < -self.daily_loss_limit:
            self.is_kill_switch_active = True
            return False, f"🚨 CRITICAL: Max Drawdown Hit! Loss: {pnl_percent*100:.2f}%"
        
        return True, "✅ Safe"