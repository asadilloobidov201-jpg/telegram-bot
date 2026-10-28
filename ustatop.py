import json
import os
import tempfile
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import os
TOKEN = os.getenv("TOKEN", "")
DATA_FILE = "ustatop_data.json"

MAIN_MENU = [
    ["🔧 Usta topish", "📝 Usta bo‘lib qo‘shilish"],
    ["💰 Hisobchi", "👤 Profilim"],
    ["📊 Hisobot", "ℹ️ Yordam"],
]

ACCOUNT_MENU = [
    ["➕ Xarajat", "➕ Daromad"],
    ["🧾 Tarix", "🎯 Budjet"],
    ["🗑 Oxirgi xarajatni o‘chirish"],
    ["📊 Hisobot", "🏠 Bosh menyu"],
]

CATEGORIES = [
    "🔌 Elektrik",
    "🚿 Santexnik",
    "❄️ Konditsioner ustasi",
    "🧱 Quruvchi",
    "🎨 Bo‘yoqchi",
    "🪚 Duradgor",
    "🧹 Tozalash xizmati",
    "🧰 Boshqa usta",
]


# ---------- MA'LUMOTLARNI SAQLASH ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"masters": [], "users": {}}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.setdefault("masters", [])
        data.setdefault("users", {})

        for user in data["users"].values():
            user.setdefault("income", 0)
            user.setdefault("expenses", [])
            user.setdefault("budget", 0)

        return data

    except (json.JSONDecodeError, OSError):
        print("DIQQAT: Ma'lumot faylini o‘qib bo‘lmadi.")
        return {"masters": [], "users": {}}


def save_data(data):
    folder = os.path.dirname(os.path.abspath(DATA_FILE))

    fd, temp_path = tempfile.mkstemp(
        dir=folder,
        prefix="ustatop_",
        suffix=".tmp",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, DATA_FILE)

    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise


def get_user(data, user_id):
    key = str(user_id)

    if key not in data["users"]:
        data["users"][key] = {
            "income": 0,
            "expenses": [],
            "budget": 0,
        }

    user = data["users"][key]
    user.setdefault("income", 0)
    user.setdefault("expenses", [])
    user.setdefault("budget", 0)

    return user


def keyboard(rows):
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def money(amount):
    return f"{amount:,}".replace(",", " ") + " so‘m"


def normalize(text):
    return " ".join(text.casefold().strip().split())


def find_master(data, user_id):
    for master in data["masters"]:
        if str(master.get("user_id")) == str(user_id):
            return master
    return None


# ---------- BOSHLASH VA YORDAM ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "UstaTop Hisobchi botiga xush kelibsiz!\n\n"
        "🔧 Ishonchli usta qidiring.\n"
        "📝 O‘z xizmatlaringizni ro‘yxatdan o‘tkazing.\n"
        "💰 Daromad va xarajatlaringizni hisoblang.\n"
        "🎯 Oylik budjetingizni nazorat qiling.\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard(MAIN_MENU),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 BOTDAN FOYDALANISH\n\n"
        "🔧 Usta topish — hudud va xizmatni tanlang.\n"
        "📝 Usta bo‘lib qo‘shilish — profilingizni yarating.\n"
        "👤 Profilim — usta ma’lumotlarini ko‘ring.\n"
        "💰 Hisobchi — daromad va xarajatlarni yozing.\n\n"
        "Xarajat misoli:\n"
        "50000 oziq-ovqat\n\n"
        "Daromad misoli:\n"
        "daromad 1000000\n\n"
        "Istalgan jarayonni bekor qilish: /cancel",
        reply_markup=keyboard(MAIN_MENU),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Amal bekor qilindi.",
        reply_markup=keyboard(MAIN_MENU),
    )


# ---------- USTA RO‘YXATDAN O‘TISH ----------

async def register_master(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()
    context.user_data["state"] = "master_region"

    await update.message.reply_text(
        "📝 USTA RO‘YXATI\n\n"
        "Qaysi viloyat yoki shaharda ishlaysiz?\n"
        "Masalan: Toshkent shahri, Samarqand, Andijon.",
    )


async def show_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = load_data()
    master = find_master(data, update.effective_user.id)

    if not master:
        await update.message.reply_text(
            "Siz hali usta sifatida ro‘yxatdan o‘tmagansiz.\n"
            "📝 Usta bo‘lib qo‘shilish tugmasini bosing.",
            reply_markup=keyboard(MAIN_MENU),
        )
        return

    await update.message.reply_text(
        "👤 SIZNING USTA PROFILINGIZ\n\n"
        f"Ism: {master['name']}\n"
        f"Hudud: {master['region']}\n"
        f"Xizmat: {master['category']}\n"
        f"Telefon: {master['phone']}\n"
        f"Tavsif: {master['description']}\n\n"
        "Profilni yangilash uchun 📝 Usta bo‘lib qo‘shilish "
        "tugmasini bosing.\n"
        "Profilni o‘chirish uchun /deleteprofile yuboring.",
        reply_markup=keyboard(MAIN_MENU),
    )


async def delete_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = load_data()
    user_id = update.effective_user.id
    master = find_master(data, user_id)

    if not master:
        await update.message.reply_text(
            "Sizda o‘chiriladigan usta profili yo‘q.",
            reply_markup=keyboard(MAIN_MENU),
        )
        return

    data["masters"] = [
        item for item in data["masters"]
        if str(item.get("user_id")) != str(user_id)
    ]
    save_data(data)

    await update.message.reply_text(
        "✅ Usta profilingiz o‘chirildi.",
        reply_markup=keyboard(MAIN_MENU),
    )


# ---------- USTA QIDIRISH ----------

async def search_master(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()
    context.user_data["state"] = "search_region"

    await update.message.reply_text(
        "🔎 USTA QIDIRISH\n\n"
        "Qaysi viloyat yoki shahardan usta kerak?\n"
        "Masalan: Toshkent, Buxoro, Farg‘ona.",
    )


# ---------- HISOBCHI ----------

async def open_accounting(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "💰 HISOBCHI BO‘LIMI\n\n"
        "Quyidagi xizmatlardan birini tanlang:",
        reply_markup=keyboard(ACCOUNT_MENU),
    )


async def show_report(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = load_data()
    user = get_user(data, update.effective_user.id)
    save_data(data)

    total_expenses = sum(
        item["amount"] for item in user["expenses"]
    )
    balance = user["income"] - total_expenses

    now = datetime.now()
    month_expenses = sum(
        item["amount"]
        for item in user["expenses"]
        if item.get("date", "").startswith(now.strftime("%Y-%m"))
    )

    await update.message.reply_text(
        "📊 MOLIYAVIY HISOBOT\n\n"
        f"💵 Jami daromad: {money(user['income'])}\n"
        f"🛒 Jami xarajat: {money(total_expenses)}\n"
        f"⚖️ Daromad minus xarajat: {money(balance)}\n\n"
        f"📅 Shu oydagi xarajat: {money(month_expenses)}\n"
        f"🎯 Oylik budjet: "
        f"{money(user['budget']) if user['budget'] else 'Belgilanmagan'}",
        reply_markup=keyboard(ACCOUNT_MENU),
    )


async def show_history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = load_data()
    user = get_user(data, update.effective_user.id)
    save_data(data)

    expenses = user["expenses"][-10:]

    if not expenses:
        await update.message.reply_text(
            "Hozircha xarajatlar tarixi bo‘sh.",
            reply_markup=keyboard(ACCOUNT_MENU),
        )
        return

    lines = ["🧾 OXIRGI XARAJATLAR\n"]

    for item in reversed(expenses):
        lines.append(
            f"• {item.get('date', '-')}: "
            f"{money(item['amount'])} — {item['category']}"
        )

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=keyboard(ACCOUNT_MENU),
    )


async def delete_last_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = load_data()
    user = get_user(data, update.effective_user.id)

    if not user["expenses"]:
        await update.message.reply_text(
            "O‘chiriladigan xarajat yo‘q.",
            reply_markup=keyboard(ACCOUNT_MENU),
        )
        return

    removed = user["expenses"].pop()
    save_data(data)

    await update.message.reply_text(
        "🗑 Oxirgi xarajat o‘chirildi.\n\n"
        f"Summa: {money(removed['amount'])}\n"
        f"Sabab: {removed['category']}",
        reply_markup=keyboard(ACCOUNT_MENU),
    )


# ---------- ASOSIY XABARLAR ----------

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    uid = update.effective_user.id
    state = context.user_data.get("state")

    # Menyu tugmalari
    if text == "🏠 Bosh menyu":
        context.user_data.clear()
        await update.message.reply_text(
            "Asosiy menyu:",
            reply_markup=keyboard(MAIN_MENU),
        )
        return

    if text == "🔧 Usta topish":
        await search_master(update, context)
        return

    if text == "📝 Usta bo‘lib qo‘shilish":
        await register_master(update, context)
        return

    if text == "👤 Profilim":
        context.user_data.clear()
        await show_profile(update, context)
        return

    if text == "💰 Hisobchi":
        await open_accounting(update, context)
        return

    if text == "📊 Hisobot":
        context.user_data.clear()
        await show_report(update, context)
        return

    if text == "ℹ️ Yordam":
        context.user_data.clear()
        await help_command(update, context)
        return

    if text == "➕ Xarajat":
        context.user_data.clear()
        context.user_data["state"] = "expense"
        await update.message.reply_text(
            "Xarajat summasi va sababini yozing.\n"
            "Masalan: 50000 oziq-ovqat"
        )
        return

    if text == "➕ Daromad":
        context.user_data.clear()
        context.user_data["state"] = "income"
        await update.message.reply_text(
            "Daromad summasini yozing.\n"
            "Masalan: 1000000 yoki 1000000 ish haqi"
        )
        return

    if text == "🧾 Tarix":
        context.user_data.clear()
        await show_history(update, context)
        return

    if text == "🗑 Oxirgi xarajatni o‘chirish":
        context.user_data.clear()
        await delete_last_expense(update, context)
        return

    if text == "🎯 Budjet":
        context.user_data.clear()
        context.user_data["state"] = "budget"
        await update.message.reply_text(
            "Oylik xarajat budjetingizni so‘mda yozing.\n"
            "Masalan: 3000000\n"
            "Budjetni o‘chirish uchun 0 yozing."
        )
        return

    # Usta ro‘yxatidan o‘tish jarayoni
    if state == "master_region":
        context.user_data["master_region"] = text
        context.user_data["state"] = "master_category"

        rows = [CATEGORIES[i:i + 2] for i in range(0, len(CATEGORIES), 2)]

        await update.message.reply_text(
            "Qaysi xizmatni ko‘rsatasiz?",
            reply_markup=keyboard(rows),
        )
        return

    if state == "master_category":
        if text not in CATEGORIES:
            await update.message.reply_text(
                "Iltimos, pastdagi ro‘yxatdan xizmat turini tanlang."
            )
            return

        context.user_data["master_category"] = text
        context.user_data["state"] = "master_name"

        await update.message.reply_text(
            "Ism yoki ism-familiyangizni yozing:",
        )
        return

    if state == "master_name":
        if len(text) < 2:
            await update.message.reply_text("Ismingizni to‘liqroq yozing.")
            return

        context.user_data["master_name"] = text
        context.user_data["state"] = "master_phone"

        await update.message.reply_text(
            "Telefon raqamingizni xalqaro formatda yozing.\n"
            "Masalan: +998901234567"
        )
        return

    if state == "master_phone":
        phone = text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if not phone.startswith("+") or not phone[1:].isdigit():
            await update.message.reply_text(
                "Telefon raqami noto‘g‘ri.\n"
                "Masalan: +998901234567"
            )
            return

        context.user_data["master_phone"] = phone
        context.user_data["state"] = "master_description"

        await update.message.reply_text(
            "Xizmatingiz haqida qisqacha ma’lumot yozing.\n"
            "Masalan: uy va ofislarda elektr ta’mirlash ishlari."
        )
        return

    if state == "master_description":
        if len(text) < 5:
            await update.message.reply_text(
                "Iltimos, xizmat haqida biroz batafsilroq yozing."
            )
            return

        context.user_data["master_description"] = text
        context.user_data["state"] = "master_consent"

        await update.message.reply_text(
            "📋 MA’LUMOTLARINGIZ\n\n"
            f"Ism: {context.user_data['master_name']}\n"
            f"Hudud: {context.user_data['master_region']}\n"
            f"Xizmat: {context.user_data['master_category']}\n"
            f"Telefon: {context.user_data['master_phone']}\n"
            f"Tavsif: {text}\n\n"
            "Ushbu ma’lumotlar usta qidirayotgan odamlarga "
            "ko‘rsatilishiga rozimisiz?\n\n"
            "Saqlash uchun ROZIMAN deb yozing.\n"
            "Bekor qilish uchun /cancel yuboring."
        )
        return

    if state == "master_consent":
        if text.upper() != "ROZIMAN":
            await update.message.reply_text(
                "Ma’lumotlarni saqlash uchun ROZIMAN deb yozing "
                "yoki /cancel yuboring."
            )
            return

        data = load_data()

        master = {
            "user_id": uid,
            "name": context.user_data["master_name"],
            "region": context.user_data["master_region"],
            "category": context.user_data["master_category"],
            "phone": context.user_data["master_phone"],
            "description": context.user_data["master_description"],
        }

        data["masters"] = [
            item for item in data["masters"]
            if str(item.get("user_id")) != str(uid)
        ]
        data["masters"].append(master)
        save_data(data)

        context.user_data.clear()

        await update.message.reply_text(
            "✅ Usta profilingiz saqlandi!\n"
            "Profilingizni keyinchalik yangilashingiz mumkin.",
            reply_markup=keyboard(MAIN_MENU),
        )
        return

    # Usta qidirish jarayoni
    if state == "search_region":
        context.user_data["search_region"] = text
        context.user_data["state"] = "search_category"

        rows = [CATEGORIES[i:i + 2] for i in range(0, len(CATEGORIES), 2)]

        await update.message.reply_text(
            "Qaysi xizmat kerak?",
            reply_markup=keyboard(rows),
        )
        return

    if state == "search_category":
        if text not in CATEGORIES:
            await update.message.reply_text(
                "Iltimos, xizmat turini ro‘yxatdan tanlang."
            )
            return

        data = load_data()
        region = normalize(context.user_data["search_region"])

        matches = [
            master for master in data["masters"]
            if master.get("category") == text
            and region in normalize(master.get("region", ""))
        ]

        context.user_data.clear()

        if not matches:
            await update.message.reply_text(
                "😕 Bu hududda hozircha mos usta topilmadi.\n\n"
                "Boshqa hududni qidirib ko‘ring yoki ustalarga "
                "bot orqali ro‘yxatdan o‘tishni tavsiya qiling.",
                reply_markup=keyboard(MAIN_MENU),
            )
            return

        await update.message.reply_text(
            f"✅ {len(matches)} ta usta topildi:",
            reply_markup=keyboard(MAIN_MENU),
        )

        for master in matches[:10]:
            await update.message.reply_text(
                "🔧 USTA MA’LUMOTI\n\n"
                f"👤 Ism: {master['name']}\n"
                f"📍 Hudud: {master['region']}\n"
                f"🛠 Xizmat: {master['category']}\n"
                f"📞 Telefon: {master['phone']}\n"
                f"ℹ️ Tavsif: {master['description']}"
            )
        return

    # Hisobchi jarayonlari
    data = load_data()
    user = get_user(data, uid)

    if state == "budget":
        try:
            amount = int(text.replace(" ", ""))

            if amount < 0:
                raise ValueError

            user["budget"] = amount
            save_data(data)
            context.user_data.clear()

            await update.message.reply_text(
                "✅ Budjet saqlandi: "
                + ("O‘chirilgan" if amount == 0 else money(amount)),
                reply_markup=keyboard(ACCOUNT_MENU),
            )
        except ValueError:
            await update.message.reply_text(
                "Faqat musbat son yozing. Masalan: 3000000"
            )
        return

    if state == "income":
        parts = text.split(maxsplit=1)

        try:
            amount = int(parts[0].replace(" ", ""))

            if amount <= 0:
                raise ValueError

            user["income"] += amount
            save_data(data)
            context.user_data.clear()

            await update.message.reply_text(
                "✅ Daromad saqlandi: " + money(amount),
                reply_markup=keyboard(ACCOUNT_MENU),
            )
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Summani raqam bilan yozing. Masalan: 1000000"
            )
        return

    if state == "expense":
        parts = text.split(maxsplit=1)

        try:
            amount = int(parts[0].replace(" ", ""))

            if amount <= 0 or len(parts) < 2:
                raise ValueError

            category = parts[1].strip()

            user["expenses"].append({
                "amount": amount,
                "category": category,
                "date": datetime.now().strftime("%Y-%m-%d"),
            })

            save_data(data)
            context.user_data.clear()

            reply = (
                "✅ Xarajat saqlandi!\n\n"
                f"💸 Summa: {money(amount)}\n"
                f"🧾 Sabab: {category}"
            )

            if user["budget"] > 0:
                month = datetime.now().strftime("%Y-%m")
                month_total = sum(
                    item["amount"]
                    for item in user["expenses"]
                    if item.get("date", "").startswith(month)
                )

                reply += (
                    f"\n\n📅 Shu oydagi xarajat: {money(month_total)}"
                )

                if month_total >= user["budget"]:
                    reply += "\n⚠️ Diqqat! Oylik budjetingizga yetdingiz."

            await update.message.reply_text(
                reply,
                reply_markup=keyboard(ACCOUNT_MENU),
            )

        except (ValueError, IndexError):
            await update.message.reply_text(
                "Xarajatni quyidagicha yozing:\n"
                "50000 oziq-ovqat"
            )
        return

    await update.message.reply_text(
        "Kerakli bo‘limni menyudan tanlang.\n"
        "Boshlash uchun /start yuboring.",
        reply_markup=keyboard(MAIN_MENU),
    )


# ---------- DASTURNI ISHGA TUSHIRISH ----------

def main():
    if TOKEN == "BU_YERGA_BOT_TOKENINGIZNI_QOY":
        print("XATO: TOKEN joyiga BotFather tokenini kiriting.")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hisobot", show_report))
    app.add_handler(CommandHandler("deleteprofile", delete_profile))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("UstaTop Hisobchi ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
