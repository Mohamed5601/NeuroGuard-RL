from executor.binance_connector import BinanceConnector
from utils.notifier import send_telegram_message # <--- تم إضافة استدعاء التليجرام

print("--- 📡 Testing Binance Connection & Telegram ---")

connector = BinanceConnector()

# 1. تجربة جلب السعر
print("... Fetching BTC price ...")
price = connector.get_btc_price()

if price:
    print(f"✅ Current BTC Price: ${price}")
else:
    print("❌ Failed to get price.")

# 2. تجربة صفقة وهمية + إرسال تليجرام
print("\n... Testing Mock Trade Logic ...")
# دالة Mock Trade بتطبع بس على الشاشة
trade_success = connector.execute_mock_trade('buy', 100) 

if trade_success:
    # هنا هنبعت الرسالة بنفسنا للموبايل
    msg = (
        f"🧪 <b>TEST TRADE EXECUTED</b>\n"
        f"Type: BUY\n"
        f"Price: ${price}\n"
        f"Amount: $100\n"
        f"Status: Simulation OK ✅"
    )
    send_telegram_message(msg) # <--- الأمر الذي كان ناقصاً
    print("📱 Telegram notification sent check your phone!")

# 3. تجربة الرصيد (المتوقع فشلها)
print("\n... Checking Balance (Expected Failure with fake keys) ...")
balance = connector.get_usdt_balance()
print(f"💰 Wallet Balance: {balance} USDT")