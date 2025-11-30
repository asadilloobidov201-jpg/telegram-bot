import telebot
import requests

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"  # Bu yerga tokenni yozasiz
bot = telebot.TeleBot(TOKEN)

API = "https://api.sssgram.com/st/instagram"

# Instagramdan haqiqiy video URL olish
def insta_video_link(url):
    try:
        r = requests.post(API, json={"url": url})
        data = r.json()

        # Video URL ni olish
        video_url = data["links"][0]["url"]
        return video_url
    except Exception as e:
        print("Xato:", e)
        return None

# Bot barcha xabarlarni qabul qiladi
@bot.message_handler(func=lambda m: True)
def get_video(msg):
    url = msg.text

    bot.reply_to(msg, "⏳ Video yuklab olinmoqda...")

    real_video = insta_video_link(url)

    if real_video:
        bot.send_video(msg.chat.id, real_video)
    else:
        bot.reply_to(msg, "❌ Videoni yuklab bo‘lmadi! Linkni tekshiring.")

bot.polling()
