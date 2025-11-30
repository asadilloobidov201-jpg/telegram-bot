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
    bot.javob_berish(msg, "⏳ Yuklab olinmoqda...")

    video = yuklab_oling(url)

    if video:
        bot.yuborish_video(msg.suhbat.id, video)
else:
    bot.javob_berish(msg, "❌ Video topilmadi. Linkni to'g'ri kiriting.")

        
main.py
app.py
