import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc")  # PythonAnywhere'ga qo'yasan

# --- Instagram API xizmatini shu yerga qo'yasan ---
API_URL = "https://your-instagram-downloader-api.com/download?url="


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Instagram link yuboring — videoni yuklab beraman 📥"
    )


async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        await update.message.reply_text("❌ Faqat Instagram link yuboring!")
        return

    await update.message.reply_text("⏳ Video yuklab olinmoqda...")

    try:
        # APIga so‘rov yuboramiz
        response = requests.get(API_URL + url)
        data = response.json()

        if not data.get("video_url"):
            await update.message.reply_text("❌ Videoni yuklashda xatolik!")
            return

        video_link = data["video_url"]

        # Videoni Telegramga yuboramiz
        await update.message.reply_video(video_link)

    except Exception as e:
        await update.message.reply_text("❌ Serverda xatolik!")
        print("Error:", e)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT, download_instagram))

    print("Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
bot.py      
main.py
app.py
