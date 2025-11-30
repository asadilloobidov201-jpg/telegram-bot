import telebot
import requests
import subprocess

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"
bot = telebot.TeleBot(TOKEN)

# --- Video yuklab olish ---
def yuklab_ol(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open("raw.mp4", "wb") as f:
                f.write(r.content)
            return "raw.mp4"
        else:
            return None
    except:
        return None

# --- Video formatini to‘g‘rilash (ffmpeg) ---
def convert_video(input_file, output_file="video.mp4"):
    try:
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vcodec", "libx264",
            "-acodec", "aac",
            "-strict", "experimental",
            output_file
        ]
        subprocess.run(cmd, check=True)
        return output_file
    except:
        return None


# --- Foydalanuvchi yuborgan linkni qayta ishlash ---
@bot.message_handler(func=lambda m: True)
def get_video(xabar):
    url = xabar.text

    bot.reply_to(xabar, "⏳ Yuklab olinmoqda...")

    raw = yuklab_ol(url)

    if not raw:
        bot.reply_to(xabar, "❌ Video yuklab bo‘lmadi. Link xato bo‘lishi mumkin.")
        return

    bot.send_message(xabar.chat.id, "♻️ Format o‘zgartirilmoqda...")

    video = convert_video(raw)

    if not video:
        bot.reply_to(xabar, "❌ Video formatini o‘zgartirishda xato.")
        return

    bot.send_message(xabar.chat.id, "📤 Yuborilmoqda...")

    # --- Video yuborish ---
    with open(video, "rb") as f:
        bot.send_video(xabar.chat.id, f)

    bot.send_message(xabar.chat.id, "✅ Tayyor!")


bot.polling()
bot.py      
main.py
app.py
