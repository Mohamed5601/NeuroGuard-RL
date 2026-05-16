import requests
import sys
import os

# نضيف المسار الرئيسي عشان نقدر نستدعي config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config

config = load_config()

def send_telegram_message(message):
    """
    دالة لإرسال رسالة فورية إلى تليجرام
    """
    token = config['TELEGRAM_TOKEN']
    chat_id = config['TELEGRAM_CHAT_ID']
    
    if not token or not chat_id:
        print(f"⚠️ تنبيه محلي: {message} (لم يتم الإرسال لتليجرام لعدم وجود المفاتيح)")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ خطأ في إرسال تليجرام: {response.text}")
        else:
            print(f"✅ تم إرسال تليجرام: {message}")
    except Exception as e:
        print(f"❌ خطأ اتصال بتليجرام: {e}")