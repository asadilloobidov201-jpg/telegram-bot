import telebot
from telebot import types
from deep_translator import GoogleTranslator
import os

TOKEN = os.getenv("TOKEN")  # Token GitHub'da emas, Railway'da saqlanadi
bot = telebot.TeleBot(TOKEN)

premium_users = set()
selected_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🌍 Til tanlash"),
        types.KeyboardButton("✍️ Matn tarjima"),
        types.KeyboardButton("⭐ Premium menyu")
    )

    bot.send_message(
        message.chat.id,
        "👋 Assalomu alaykum!\n"
        "Men Premium Tarjima Botman.\n"
        "Quyidagilardan birini tanlang:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🌍 Til tanlash")
def choose_language(message):
    markup = types.InlineKeyboardMarkup()

    langs = [
        ("🇬🇧 English", "en"),
        ("🇷🇺 Russian", "ru"),
        ("🇺🇿 Uzbek", "uz"),
        ("🇹🇷 Turkish", "tr"),
        ("🇪🇸 Spanish", "es"),
        ("🇨🇳 Chinese", "zh-cn")
    ]

    for name, code in langs:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"lang_{code}"))

    bot.send_message(message.chat.id, "Tarjima tilini tanlang:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang = call.data.replace("lang_", "")
    user_id = call.from_user.id

    selected_lang[user_id] = lang

    bot.answer_callback_query(call.id, "Til o‘rnatildi!")
    bot.send_message(call.message.chat.id, f"✔ Til tanlandi: {lang.upper()}.\nEndi matn yuboring.")


@bot.message_handler(func=lambda m: m.text == "✍️ Matn tarjima")
def ask_text(message):
    bot.send_message(message.chat.id, "Tarjima qilinadigan matnni yuboring.")


@bot.message_handler(func=lambda m: m.text not in
                     ["🌍 Til tanlash", "✍️ Matn tarjima", "⭐ Premium menyu"])
def translate_text(message):
    user_id = message.from_user.id

    if user_id not in selected_lang:
        bot.send_message(message.chat.id, "❗ Avval til tanlang: 🌍 Til tanlash")
        return

    lang = selected_lang[user_id]

    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.text)

        bot.send_message(
            message.chat.id,
            f"📥 Kirish: {message.text}\n\n"
            f"📤 Tarjima: {translated}"
        )

    except:
        bot.send_message(message.chat.id, "❌ Xatolik yuz berdi. Keyinroq urinib ko‘ring.")


@bot.message_handler(func=lambda m: m.text == "⭐ Premium menyu")
def premium_menu(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()

    if user_id in premium_users:
        markup.add(types.InlineKeyboardButton("🔊 Ovozni tarjima", callback_data="prem_audio"))
        markup.add(types.InlineKeyboardButton("📄 Rasm tarjima (OCR)", callback_data="prem_ocr"))
        markup.add(types.InlineKeyboardButton("🌐 Avto-detektsiya", callback_data="prem_auto"))

        bot.send_message(message.chat.id, "⭐ PREMIUM FUNKSIYALAR:", reply_markup=markup)

    else:
        markup.add(types.InlineKeyboardButton("🔓 Premium olish (20 000 so‘m)", callback_data="buy_prem"))
        bot.send_message(message.chat.id, "Bu bo‘lim faqat PREMIUM uchun!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "buy_prem")
def buy_premium(call):
    user_id = call.from_user.id
    premium_users.add(user_id)

    bot.answer_callback_query(call.id, "Premium faollashtirildi!")
    bot.send_message(call.message.chat.id, "🎉 Endi siz PREMIUM foydalanuvchisiz!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("prem_"))
def premium_features(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "⚙️ Bu funksiya tez orada qo‘shiladi!")


print("Bot ishga tushdi...")
bot.infinity_polling()
