import requests
import hashlib
import asyncio
import threading
from telegram import Bot
import os
from flask import Flask

# --- Конфігурація ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
IMAGE_URL = "https://api.loe.lviv.ua/media/690e8dca879d5_GPV-mobile.png"
CHECK_INTERVAL = 300  # секунд (5 хвилин)

# --- Flask сервер ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Скрипт живий і стежить за графіком 24/7!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# --- Основна логіка ---
async def check_and_send():
    bot = Bot(token=BOT_TOKEN)
    last_hash = None

    async with bot:
        while True:
            try:
                r = requests.get(IMAGE_URL, timeout=10)
                if r.status_code == 200:
                    current_hash = hashlib.md5(r.content).hexdigest()
                    if current_hash != last_hash:
                        await bot.send_photo(
                            chat_id=CHAT_ID,
                            photo=r.content,
                            caption="⚡ Нове оновлення графіка відключень електроенергії"
                        )
                        print("🆕 Картинка відправлена")
                        last_hash = current_hash
                    else:
                        print("ℹ️ Без змін")
                else:
                    print("⚠️ Помилка завантаження:", r.status_code)
            except Exception as e:
                print("❌ Помилка:", e)

            await asyncio.sleep(CHECK_INTERVAL)

def start_async_loop():
    asyncio.run(check_and_send())

# --- Запуск ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    start_async_loop()
