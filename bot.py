# bot.py
import os
import threading
import time
from flask import Flask
from google import genai        # agar Gemini ishlatayotgan bo'lsang
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ENV
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
# GEMINI_API_KEY ni genai.Client() avtomatik oladi (so'ralsa)
client = genai.Client()

# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Bot ishga tushdi.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-mini",   # kamroq resursli model tavsiya qilinadi
            contents=prompt
        )
        answer = getattr(resp, "text", None) or str(resp)
    except Exception as e:
        answer = "Xatolik yuz berdi: " + str(e)
    await update.message.reply_text(answer)

def run_telegram():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Starting telegram polling...", flush=True)
    app.run_polling()

# Minimal Flask healthcheck
flask_app = Flask("health")

@flask_app.route("/", methods=["GET"])
def index():
    return "OK", 200

if __name__ == "__main__":
    # 1) Telegram polling in background thread
    t = threading.Thread(target=run_telegram, daemon=True)
    t.start()

    # 2) Start Flask app on port assigned by Render
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting health server on port {port}", flush=True)
    flask_app.run(host="0.0.0.0", port=port)

