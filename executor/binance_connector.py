import ccxt
import sys
import os
import pandas as pd  # إضافة ممتازة لمعالجة البيانات
from datetime import datetime

# --- تصحيح المسار لضمان قراءة ملف config.py الذي أنشأناه في المرحلة 1 ---
# هذا يضمن أننا نستخدم نفس المفاتيح الموجودة في .env ولا نكرر الأكواد
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config

class BinanceConnector:
    def __init__(self):
        # تحميل الإعدادات من الملف المركزي (consistency)
        config = load_config()
        self.api_key = config['BINANCE_KEY']
        self.secret = config['BINANCE_SECRET']
        
        # 1. اتصال عام (Public) - لجلب الأسعار والشموع (سريع)
        self.public_exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

        # 2. اتصال خاص (Private) - للتداول والرصيد
        self.private_exchange = None
        if self.api_key and self.secret and self.api_key != "PLACEHOLDER":
            self.private_exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        else:
            print("⚠️ Warning: Private keys not found or invalid. Trading functions disabled.")

    def get_btc_price(self):
        """جلب السعر اللحظي"""
        try:
            ticker = self.public_exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            print(f"❌ Error fetching price: {e}")
            return None

    def get_usdt_balance(self):
        """جلب الرصيد المتاح"""
        if not self.private_exchange:
            print("⚠️ No private connection (Keys missing)")
            return 0.0
            
        try:
            balance = self.private_exchange.fetch_balance()
            return balance['free'].get('USDT', 0.0)
        except Exception as e:
            print(f"❌ Error fetching balance: {e}")
            return 0.0

    def execute_mock_trade(self, side, amount_usdt):
        """محاكاة تداول وهمي للاختبار"""
        price = self.get_btc_price()
        if price:
            btc_amount = amount_usdt / price
            print(f"\n🧪 [MOCK TRADE] Executed {side.upper()} Order:")
            print(f"   Price: {price} USDT")
            print(f"   Amount: {amount_usdt} USDT (~{btc_amount:.6f} BTC)")
            print("   ✅ Simulation Successful")
            return True
        else:
            print("❌ Failed to execute mock trade: No price data")
            return False

    def get_historical_data(self, symbol='BTC/USDT', timeframe='30m', limit=100):
        """
        جلب الشموع التاريخية وإرجاعها كـ DataFrame مباشرة
        """
        try:
            # fetch_ohlcv returns: [Time, Open, High, Low, Close, Volume]
            candles = self.public_exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not candles:
                return pd.DataFrame()

            # تحويل مباشر لـ DataFrame هنا (يوفر كود في المراحل القادمة)
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # تنسيق التاريخ
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return pd.DataFrame()

# --- اختبار سريع للكلاس ---
if __name__ == "__main__":
    connector = BinanceConnector()
    print(f"Current Price: {connector.get_btc_price()}")
    df = connector.get_historical_data()
    print(f"\nData Shape: {df.shape}")
    print(df.head(2))