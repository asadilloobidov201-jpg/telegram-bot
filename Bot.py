import telebot
import yt_dlp
import os

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Video yuklab beruvchi funksiya
def download_video(url):
    output = "video.mp4"
    ydl_opts = {
        'format': 'mp4/best',
        'outtmpl': output,
        'quiet': True,
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output
    except Exception as e:
        print("Xato:", e)
        return None

# Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Assalomu alaykum!\nVideo link yuboring — men sizga yuklab beraman.")

# Link qabul qilish
@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()

    if not url.startswith("http"):
        return bot.reply_to(message, "❌ Iltimos to‘g‘ri link yuboring.")

    sent = bot.reply_to(message, "⏳ Video yuklanmoqda...")

    file = download_video(url)

    if file:
        try:
            bot.send_video(message.chat.id, open(file, "rb"))
            os.remove(file)
            bot.delete_message(message.chat.id, sent.id)
        except:
            bot.edit_message_text("❌ Videoni yuborib bo‘lmadi!", message.chat.id, sent.id)
    else:
        bot.edit_message_text("❌ Videoni yuklab bo‘lmadi! Linkni tekshiring.", message.chat.id, sent.id)

print("Bot ishga tushdi...")
bot.infinity_polling()
bot.py      
main.py
app.py
