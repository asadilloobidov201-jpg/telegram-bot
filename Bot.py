import telebot
import requests
import re

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"
bot = telebot.TeleBot(TOKEN)

def get_instagram_video(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers)

        # Video URL ni HTML ichidan qidiramiz
        video_url = re.search(r'"video_url":"(.*?)"', r.text)
        if video_url:
            real_url = video_url.group(1).replace("\\u0026", "&")
            return real_url
        else:
            return None

    except:
        return None


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text

    if "instagram.com" not in url:
        bot.reply_to(message, "❌ Iltimos Instagram link yuboring!")
        return

    bot.reply_to(message, "⏳ Video topilmoqda...")

    video_url = get_instagram_video(url)
    if not video_url:
        bot.reply_to(message, "❌ Video URL topilmadi. Linkni tekshiring.")
        return

    bot.reply_to(message, "⬇️ Yuklab olinmoqda...")

    video = requests.get(video_url)

    with open("video.mp4", "wb") as f:
        f.write(video.content)

    bot.send_video(message.chat.id, open("video.mp4", "rb"))


bot.polling()
bot.py      
main.py
app.py
