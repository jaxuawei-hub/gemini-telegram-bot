# bot.py
import os
from google import genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
# GEMINI_API_KEY environmentda bo'lishi kerak — google-genai SDK avtomatik oladi
client = genai.Client()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Gemini botga xush kelibsiz. Savolingizni yozing.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    # oddiy chaqiriq — kerak bo'lsa paramlarni o'zgartiring
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # resp tuzilishi SDK versiyasiga qarab farq qilishi mumkin — print qilib tekshiring
    answer = getattr(resp, "text", None) or str(resp)
    await update.message.reply_text(answer)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if __name__ == "__main__":
    main()
