import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
# إذا لم يجد الملف، لن يتوقف الكود ولكن سيعطي تحذيراً
load_dotenv()

def load_config():
    """
    دالة لتحميل الإعدادات والتأكد من وجودها
    """
    config = {
        "BINANCE_KEY": os.getenv("BINANCE_API_KEY"),
        "BINANCE_SECRET": os.getenv("BINANCE_SECRET_KEY"),
        "TELEGRAM_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID")
    }

    # التأكد من أن البيانات موجودة (للمستقبل)
    # يمكننا تفعيل هذا السطر لاحقاً لضمان عدم تشغيل البوت بدون مفاتيح
    # if not all(config.values()):
    #     print("⚠️ تحذير: بعض المفاتيح مفقودة في ملف .env")
    
    return config

# تجربة سريعة عند تشغيل الملف مباشرة
if __name__ == "__main__":
    conf = load_config()
    print("✅ تم تحميل الإعدادات بنجاح!")
    print(f"Testing Key Access: {conf['BINANCE_KEY']}") # سيطبع القيمة الوهمية للتأكد