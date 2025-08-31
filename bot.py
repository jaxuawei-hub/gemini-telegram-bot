import os, sys, traceback
from google import genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# IMMEDIATE LOG
print("=== BOT STARTUP: begin ===", flush=True)
print("PWD:", os.getcwd(), flush=True)
print("PYTHON:", sys.executable, flush=True)
print("ENV keys present:", {k: (k in os.environ) for k in ['TELEGRAM_BOT_TOKEN','GEMINI_API_KEY','OPENAI_API_KEY']}, flush=True)

try:
    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
except Exception as e:
    print("ERROR: TELEGRAM_BOT_TOKEN missing!", flush=True)
    raise

# init client in try so errors show in logs
try:
    client = genai.Client()  # will use GEMINI_API_KEY from env
    print("GenAI client created.", flush=True)
except Exception as e:
    print("ERROR creating GenAI client:", e, flush=True)
    traceback.print_exc()
    raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /start from", update.effective_user.id, flush=True)
    await update.message.reply_text("Salom! Gemini botga xush kelibsiz.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prompt = update.message.text
        print("Incoming message:", prompt[:200], "from", update.effective_user.id, flush=True)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        answer = getattr(resp, "text", None) or str(resp)
        print("Replying:", (answer[:200] if answer else "<empty>"), flush=True)
        await update.message.reply_text(answer)
    except Exception as e:
        print("Handler error:", e, flush=True)
        traceback.print_exc()
        await update.message.reply_text("Xatolik yuz berdi, keyinroq urinib ko'ring.")

def main():
    try:
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
        print("Starting polling...", flush=True)
        app.run_polling()
    except Exception as e:
        print("FATAL ERROR in main:", e, flush=True)
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
