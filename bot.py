# bot.py
import os
import threading
from flask import Flask
from google import genai        # yoki openai agar OpenAI ishlatayotgan bo'lsangiz
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ENV
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
client = genai.Client()

# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Bot ishga tushdi.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-mini",
            contents=prompt
        )
        answer = getattr(resp, "text", None) or str(resp)
    except Exception as e:
        answer = "Xatolik yuz berdi: " + str(e)
    await update.message.reply_text(answer)

def create_telegram_app():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    return app

# Minimal Flask healthcheck
flask_app = Flask("health")

@flask_app.route("/", methods=["GET"])
def index():
    return "OK", 200

if __name__ == "__main__":
    # 1) Start Flask healthcheck in background thread (daemon=True)
    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        # disable reloader
        flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2) Start Telegram in main thread (this will create the asyncio loop correctly)
    print("Starting telegram polling in main thread...", flush=True)
    telegram_app = create_telegram_app()
    telegram_app.run_polling()
