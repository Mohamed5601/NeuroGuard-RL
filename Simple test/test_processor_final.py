import pandas as pd
import os
import time
# تأكد من أن هذه الاستدعاءات صحيحة وأن المكتبات مثبتة
from data.processor import DataProcessor 

def run_processor_test():
    print("--- 🔬 FINAL PROCESSOR TEST ---")
    
    # 1. تهيئة وبدء سحب البيانات (1500 شمعة)
    processor = DataProcessor()
    print("\nStarting Data Fetch and Indicator Calculation...")
    start_time = time.time()

    # نستخدم prepare_multitimeframe_data
    df = processor.prepare_multitimeframe_data('BTC/USDT', start_limit=1500)
    
    end_time = time.time()
    
    if df.empty:
        print("❌ TEST FAILED: DataFrame is empty.")
        return

    # 2. التحقق من سلامة البيانات
    print(f"\n✅ Data Processing Success!")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")

    # المؤشرات المطلوبة (نستخدم الأحرف الصغيرة كما تم إنشاؤها) 🛡️
    required_indicators = ['rsi', 'macd', 'atr', 'bb_pos']
    
    # التحقق من وجودها
    missing = [i for i in required_indicators if i not in df.columns]

    if not missing:
        print("✅ All required indicators are present.")
        
        # 3. طباعة العينة (تم تصحيح الحروف الكبيرة)
        print("\n📊 Sample Row (Last Candle):")
        # هذا هو السطر الذي كان يسبب KeyError، وتم تصحيح الأحرف الكبيرة
        print(df[['rsi', 'macd', 'atr', 'bb_pos']].iloc[-1]) 
        
    else:
        print(f"❌ TEST FAILED: Missing indicators: {missing}")
        
if __name__ == "__main__":
    run_processor_test()