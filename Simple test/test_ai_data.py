import pandas as pd
import os
from data.processor import DataProcessor

print("--- 🏗️ Testing AI Data Pipeline ---")

# 1. تشغيل المعالجة
processor = DataProcessor()
# هنسحب 1500 شمعة للتجربة
print("... Fetching and processing data (5m, 1h, 4h) ...")
df_final = processor.prepare_multitimeframe_data('BTC/USDT', start_limit=1500)

# 2. اختبار القيم
print("\n🔍 Inspecting Data Quality:")

# هل هناك قيم فارغة؟
nan_count = df_final.isna().sum().sum()
if nan_count == 0:
    print("✅ No NaN values found (Clean Data).")
else:
    print(f"❌ Warning: Found {nan_count} NaN values!")

# هل الأعمدة موجودة؟
expected_cols = ['log_ret', 'rsi', 'log_ret_1h', 'rsi_1h', 'log_ret_4h']
missing_cols = [c for c in expected_cols if c not in df_final.columns]

if not missing_cols:
    print("✅ All Multi-Timeframe columns are present.")
else:
    print(f"❌ Missing columns: {missing_cols}")

# 3. حفظ واختبار ملف Parquet
file_path = processor.save_to_parquet(df_final, 'test_data.parquet')

# قراءة الملف للتأكد
if os.path.exists(file_path):
    df_loaded = pd.read_parquet(file_path)
    print(f"✅ File loaded successfully from Parquet.")
    print("\n📊 Sample Data (First 3 rows):")
    print(df_loaded[['close', 'log_ret', 'rsi', 'rsi_1h', 'rsi_4h']].head(3))
else:
    print("❌ Failed to save file.")