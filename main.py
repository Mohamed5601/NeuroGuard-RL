import time
import sys
from config import load_config
from utils.notifier import send_telegram_message
from executor.risk_engine import RiskEngine
from executor.binance_connector import BinanceConnector

# إعدادات بسيطة للتجربة
TRADING_AMOUNT_USDT = 100  # قيمة الصفقة الوهمية
STARTING_BALANCE = 1000    # رصيد البداية الوهمي

def run_bot():
    print("🤖 --- Starting Crypto Bot (Mock Mode) ---")
    
    # 1. تجهيز الأدوات
    risk_system = RiskEngine(daily_loss_limit=0.03)
    risk_system.set_initial_balance(STARTING_BALANCE)
    
    connector = BinanceConnector()
    
    # إرسال رسالة ترحيب عند التشغيل
    send_telegram_message(f"🚀 Bot Started successfully!\nRunning in Mock Mode.")

    # 2. محاكاة دورة عمل (Loop)
    # سنقوم بتجربة دورة واحدة فقط الآن للتأكد أن كل شيء يعمل معاً
    print("\n🔄 Executing Cycle 1...")
    
    # أ) فحص الأمان (Risk Check)
    # سنفترض أن الرصيد الحالي 1005 (ربح بسيط)
    current_mock_balance = 1005 
    is_safe, message = risk_system.check_health(current_mock_balance)
    
    if not is_safe:
        print(f"⛔ STOP: {message}")
        send_telegram_message(f"⛔ Bot Stopped: {message}")
        return

    print(f"✅ Risk Check Passed: {message}")

    # ب) جلب السعر (Market Check)
    btc_price = connector.get_btc_price()
    if not btc_price:
        print("❌ Error: Could not fetch Bitcoin price. Retrying...")
        return

    print(f"📊 Current BTC Price: ${btc_price}")

    # ج) تنفيذ صفقة وهمية (Execution)
    # سنقوم بالشراء مباشرة للتجربة
    print("🛒 Attempting to BUY...")
    trade_success = connector.execute_mock_trade('buy', TRADING_AMOUNT_USDT)
    
    if trade_success:
        send_telegram_message(
            f"✅ <b>MOCK BUY Executed</b>\n"
            f"Price: ${btc_price}\n"
            f"Amount: ${TRADING_AMOUNT_USDT}"
        )
    else:
        print("❌ Trade Failed")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")