import time
import sys
import os
import traceback
from datetime import datetime

# --- 1. التأكد من المسارات واستدعاء الملفات ---
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import load_config
    from executor.binance_connector import BinanceConnector
    from executor.risk_engine import RiskEngine
    from data.feature_extractor import calculate_indicators
    from strategies.simple_logic import generate_signal
    from utils.notifier import send_telegram_message

except ImportError as e:
    print(f"🚨 CRITICAL ERROR: Missing Module -> {e}")
    sys.exit(1)

# --- 2. إعدادات التشغيل ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1m'  
TRADE_AMOUNT = 50  
SLEEP_TIME = 20    

# ⭐ إعداد رصيد وهمي للحماية من القسمة على صفر في حالة المفاتيح المزيفة ⭐
MOCK_BALANCE_DEFAULT = 1000.0 

def run_live_bot():
    print(f"🚀 Initializing Bot for {SYMBOL} on {TIMEFRAME} timeframe...")
    
    # تهيئة الكلاسات
    connector = BinanceConnector()
    risk_engine = RiskEngine(daily_loss_limit=0.03)
    
    # محاولة جلب الرصيد الحقيقي
    real_balance = connector.get_usdt_balance()
    
    # 🛡️ التصحيح هنا: لو الرصيد صفر (بسبب خطأ المفاتيح)، نستخدم رصيد وهمي
    if real_balance > 0:
        initial_balance = real_balance
        using_mock_money = False
    else:
        initial_balance = MOCK_BALANCE_DEFAULT
        using_mock_money = True
        print(f"⚠️ Keys invalid or balance 0. Using MOCK BALANCE: ${initial_balance}")

    risk_engine.set_initial_balance(initial_balance)
    
    # متغير الذاكرة (هل نملك عملة أم لا)
    is_in_position = False 

    send_telegram_message(
        f"✅ <b>Bot Started Successfully</b>\n"
        f"Symbol: {SYMBOL}\n"
        f"Initial Balance: ${initial_balance:.2f} ({'MOCK' if using_mock_money else 'REAL'})\n"
        f"Mode: MOCK TRADING"
    )

    print("🔄 Entering Main Loop (Press Ctrl+C to stop)...")

    # --- 3. بداية الحلقة اللا نهائية ---
    while True:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n--- Cycle Start: {now} ---")

            # أ) تحديد الرصيد الحالي للفحص
            # لو شغالين بفلوس وهمية، بنفترض إن الرصيد لسه زي ما هو (للحماية من الانهيار)
            if using_mock_money:
                current_balance = initial_balance 
            else:
                current_balance = connector.get_usdt_balance()

            # ب) فحص الأمان (Risk Check)
            is_safe, risk_msg = risk_engine.check_health(current_balance)
            
            if not is_safe:
                print(f"⛔ RISK STOP: {risk_msg}")
                send_telegram_message(f"⛔ <b>KILL SWITCH TRIGGERED</b>\nReason: {risk_msg}")
                break 
            
            # ج) جلب البيانات
            df = connector.get_historical_data(symbol=SYMBOL, timeframe=TIMEFRAME, limit=100)
            
            if df is None or df.empty:
                print("⚠️ Warning: Empty data. Retrying...")
                time.sleep(10)
                continue

            # د) حساب المؤشرات والاستراتيجية
            df_analyzed = calculate_indicators(df)
            signal = generate_signal(df_analyzed)
            
            # طباعة المعلومات للمراقبة
            current_price = df_analyzed.iloc[-1]['close']
            rsi_val = df_analyzed.iloc[-1]['rsi'] if 'rsi' in df_analyzed.columns else 0
            
            status_text = "Holding BTC" if is_in_position else "Waiting in USDT"
            print(f"💰 Price: ${current_price} | RSI: {rsi_val:.2f} | 🚦 Signal: {signal} | 🧘 Status: {status_text}")

            # هـ) منطق التنفيذ (Execution Logic)
            if signal == "BUY" and not is_in_position:
                print("🟢 Executing BUY Order...")
                success = connector.execute_mock_trade('buy', TRADE_AMOUNT)
                if success:
                    is_in_position = True 
                    send_telegram_message(f"🟢 <b>BUY Order Executed</b>\nPrice: {current_price}")

            elif signal == "SELL" and is_in_position:
                print("🔴 Executing SELL Order...")
                success = connector.execute_mock_trade('sell', TRADE_AMOUNT)
                if success:
                    is_in_position = False 
                    send_telegram_message(f"🔴 <b>SELL Order Executed</b>\nPrice: {current_price}")
            
            elif signal == "BUY" and is_in_position:
                print("⏳ Signal is BUY, but we are already in position. Holding.")
            elif signal == "SELL" and not is_in_position:
                print("⏳ Signal is SELL, but we have nothing to sell. Waiting.")

            # و) الانتظار
            print(f"💤 Sleeping for {SLEEP_TIME} seconds...")
            time.sleep(SLEEP_TIME)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
            send_telegram_message("🛑 Bot stopped manually.")
            break
            
        except Exception as e:
            error_msg = f"⚠️ Unexpected Error: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            send_telegram_message(error_msg)
            time.sleep(60)

if __name__ == "__main__":
    run_live_bot()