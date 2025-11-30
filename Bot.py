import telebot
import requests

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"
bot = telebot.TeleBot(TOKEN)


# --- Video yuklab olish funksiyasi ---
def yuklab_oling(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            filename = "video.mp4"
            with open(filename, "wb") as f:
                f.write(r.content)
            return filename
        else:
            return None
    except:
        return None


# --- Foydalanuvchi yuborgan linkni qayta ishlash ---
@bot.message_handler(func=lambda m: True)
def get_video(msg):
    url = msg.text

    bot.reply_to(msg, "⏳ Yuklab olinmoqda...")

    bot.reply_to(msg, ") Video topilmadi. Linkni tekshirib qayta yuboring.")

    if video:
        bot.send_video(msg.chat.id, open(video, "rb"))
    else:
        bot.reply_to(msg, "❌ Video topilmadi. Linkni to'g'ri kiriting.")


bot.polling()


bot.py      
main.py
app.py
