import telebot
import requests
BOT_TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPrc"
bot = telebot.TeleBot(BOT_TOKEN)

def download(url):
    api = "https://api.savein.io/download?url=" + url
    r = requests.get(api).json()

    try:
        video = r["result"]["adaptive"][0]["url"]
        return video
    except:
        return None

@bot.message_handler(commands=['start'])
def start(msg):
    
bot.javob_berish(msg, "🎬 Menga Instagram, YouTube yoki boshqa platformadan video havolasini yuboring!")
@bot.message_handler(content_types=['text'])
def get_video(msg):
    url = msg.text
    bot.reply_to(msg, "⏳ Yuklab olinmoqda...")

    video = download(url)

    if video:
        bot.send_video(msg.chat.id, video)
    
bot.javob_berish(msg, "❌ Video topilmadi. Linkni to'g'ri kiriting.")
bot.polling()

bot.py
main.py
app.py
