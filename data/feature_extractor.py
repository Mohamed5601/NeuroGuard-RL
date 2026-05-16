import pandas as pd
import numpy as np

def calculate_indicators(df):
    """
    يستقبل DataFrame جاهز ويحسب المؤشرات
    """
    # التحقق من أن الجدول غير فارغ
    if df is None or df.empty:
        return None

    # -- لاحظ: حذفنا خطوات تحويل الـ List لأنها بتيجيلنا جاهزة دلوقتي --
    
    # نسخة من البيانات لتجنب التحذيرات
    df = df.copy()

    # حساب المؤشرات
    # 1. المتوسط المتحرك (SMA 50)
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # 2. مؤشر RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df