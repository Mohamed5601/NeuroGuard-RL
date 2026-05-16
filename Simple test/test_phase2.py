from utils.notifier import send_telegram_message
from executor.risk_engine import RiskEngine

# 1. تجربة التليجرام
print("--- 1. Testing Telegram ---")
send_telegram_message("🤖 Hello! This is a test from your Crypto Bot.")

# 2. تجربة نظام المخاطر
print("\n--- 2. Testing Risk Engine ---")
risk = RiskEngine(daily_loss_limit=0.03) # حد خسارة 3%

# سيناريو: بدأنا بـ 1000 دولار
risk.set_initial_balance(1000)
print(f"💰 Initial Balance: $1000")

# سيناريو أ: الرصيد نزل لـ 980 (خسارة 2%) -> مفروض آمن
is_safe, msg = risk.check_health(980)
print(f"Current $980: {msg}")

# سيناريو ب: الرصيد نزل لـ 960 (خسارة 4%) -> مفروض خطر ويفصل
is_safe, msg = risk.check_health(960)
print(f"Current $960: {msg}")

if not is_safe:
    send_telegram_message(msg) # نبعت تنبيه بالخطر