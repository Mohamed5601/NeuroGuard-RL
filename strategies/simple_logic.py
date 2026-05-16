import pandas as pd  # <--- ده السطر اللي كان ناقص وعمل المشكلة

def generate_signal(df):
    """
    بناءً على البيانات، قرر: BUY, SELL, or HOLD
    الاستراتيجية للتجربة:
    - شراء: لو السعر الحالي أكبر من متوسط 50 شمعة (اتجاه صاعد)
    - بيع: لو السعر الحالي أقل من متوسط 50 شمعة (اتجاه هابط)
    """
    # التأكد من أن الجدول موجود وفيه بيانات كافية
    if df is None or df.empty or len(df) < 50:
        return "HOLD"

    # هات آخر شمعة (أحدث سعر)
    latest = df.iloc[-1]
    
    # تأكد إن المؤشرات اتحسبت (مش NaN)
    # NaN بتحصل لو الشموع أقل من الفترة المطلوبة للمتوسط
    if pd.isna(latest['sma_50']) or pd.isna(latest['rsi']):
        return "HOLD"

    current_price = latest['close']
    sma_50 = latest['sma_50']
    rsi = latest['rsi']

    print(f"🧐 Analyzing: Price=${current_price}, SMA50=${sma_50:.2f}, RSI={rsi:.2f}")

    # --- منطق القرار (Trend Following Logic) ---
    
    # 1. حالة الشراء (السعر فوق المتوسط + RSI مش متشبع شراء)
    if current_price > sma_50 and rsi < 70:
        return "BUY"
    
    # 2. حالة البيع (السعر تحت المتوسط)
    elif current_price < sma_50:
        return "SELL"
    
    return "HOLD"