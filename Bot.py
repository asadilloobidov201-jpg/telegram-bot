
import telebot
import requests

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"
bot = telebot.TeleBot(TOKEN)

# --- Video yuklab olish ---
def yuklab_oling(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            file_name = "video.mp4"
            with open(file_name, "wb") as f:
                f.write(r.content)
            return file_name
        else:
            return None
    except:
        return None

# --- Foydalanuvchi yuborgan linkni qayta ishlash ---
@bot.message_handler(func=lambda m: True)
def get_video(xabar):
    url = xabar.text

    bot.reply_to(xabar, "⏳ Yuklab olinmoqda...")

    video = yuklab_oling(url)

    if video:
        with open(video, "rb") as f:
            bot.send_video(xabar.chat.id, f)
    else:
        bot.reply_to(xabar, "❌ Video topilmadi. Linkni to'g'ri kiriting.")

bot.polling()

bot.polling()
bot.polling()
bot.py      
main.py
app.py
