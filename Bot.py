import telebot
import instaloader
import requests
import os

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"
bot = telebot.TeleBot(TOKEN)

L = instaloader.Instaloader(download_videos=True, save_metadata=False)


def insta_download(url):
    try:
        shortcode = url.split("/reel/")[1].split("/")[0]
    except:
        return None

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        video_url = post.video_url
        return video_url
    except:
        return None


@bot.message_handler(func=lambda m: True)
def get_video(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklab olinmoqda...")

    video_url = insta_download(url)

    if not video_url:
        bot.reply_to(message, "❌ Video topilmadi yoki maxfiy akkaunt.")
        return

    bot.reply_to(message, "⬇️ Video yuklanmoqda...")

    # Video faylni yuklab olish
    r = requests.get(video_url)
    file_name = "video.mp4"
    with open(file_name, "wb") as f:
        f.write(r.content)

    # Telegramga yuborish
    with open(file_name, "rb") as v:
        bot.send_video(message.chat.id, v)

    os.remove(file_name)


bot.polling()
bot.py      
main.py
app.py
