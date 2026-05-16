import pandas as pd
from executor.binance_connector import BinanceConnector
from data.feature_extractor import calculate_indicators
from strategies.simple_logic import generate_signal

print("--- 🧠 Testing The Updated Brain (DataFrame Flow) ---")

# 1. الاتصال وجلب البيانات (المفروض ترجع جدول جاهز)
print("\n1️⃣  Initializing Connector...")
connector = BinanceConnector()

print("... Fetching last 100 candles (as DataFrame)...")
df_candles = connector.get_historical_data(limit=100)

# اختبار نوع البيانات (لازم يكون DataFrame)
if isinstance(df_candles, pd.DataFrame) and not df_candles.empty:
    print(f"✅ Data Fetched Successfully!")
    print(f"   Shape: {df_candles.shape} (Rows, Columns)")
    print(f"   Columns: {list(df_candles.columns)}")
    
    # 2. حساب المؤشرات
    print("\n2️⃣  Calculating Indicators (SMA, RSI)...")
    df_with_indicators = calculate_indicators(df_candles)
    
    # التأكد إن العواميد الجديدة ظهرت
    if 'sma_50' in df_with_indicators.columns and 'rsi' in df_with_indicators.columns:
        print("✅ Indicators Added Successfully!")
        
        # طباعة آخر شمعة عشان نشوف الأرقام
        latest = df_with_indicators.iloc[-1]
        print("\n📊 Latest Candle Data:")
        print(f"   Date: {latest['timestamp']}")
        print(f"   Close Price: ${latest['close']}")
        print(f"   SMA 50: {latest['sma_50']:.2f}")
        print(f"   RSI: {latest['rsi']:.2f}")
        
        # 3. اتخاذ القرار
        print("\n3️⃣  Generating Strategy Signal...")
        decision = generate_signal(df_with_indicators)
        print(f"🚀 FINAL DECISION: {decision}")
        
    else:
        print("❌ Error: Indicators columns (sma_50, rsi) missing!")

else:
    print("❌ Failed to fetch data or data is empty.")