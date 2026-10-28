import os
import logging
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Token BotFather'dan olinadi. Tokenni kod ichiga yozmang.
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

BASE_DIR = Path.home() / "vizitka_bot"
BASE_DIR.mkdir(parents=True, exist_ok=True)

DESIGN_BUTTONS = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Qora-oltin"), KeyboardButton("Ko'k-oq")],
        [KeyboardButton("Yashil-oq"), KeyboardButton("Oq-qora")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

QUESTIONS = [
    ("name", "1/6. Ism-familiyangizni yozing:"),
    ("job", "2/6. Kasbingiz yoki kompaniyangiz nomini yozing:"),
    ("phone", "3/6. Telefon raqamingizni yozing:"),
    ("address", "4/6. Manzilni yozing. Bo'lmasa, SKIP yozing:"),
    ("telegram", "5/6. Telegram username yozing. Bo'lmasa, SKIP yozing:"),
]

PALETTES = {
    "Qora-oltin": ((22, 23, 29), (226, 187, 98), (255, 255, 255)),
    "Ko'k-oq": ((22, 62, 110), (91, 177, 239), (255, 255, 255)),
    "Yashil-oq": ((22, 83, 64), (107, 205, 151), (255, 255, 255)),
    "Oq-qora": ((248, 248, 248), (35, 35, 35), (35, 35, 35)),
}


def get_font(size: int, bold: bool = False):
    """Android/Termux va boshqa tizimlarda mavjud shriftni topishga urinadi."""
    candidates = [
        "/system/fonts/Roboto-Bold.ttf" if bold else "/system/fonts/Roboto-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for font_path in candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit_text(text: str, max_chars: int = 42) -> str:
    text = (text or "").strip()
    if len(text) > max_chars:
        return text[: max_chars - 1] + "…"
    return text


def create_business_card(data: dict, logo_bytes: bytes | None = None) -> BytesIO:
    width, height = 1200, 675
    design = data.get("design", "Qora-oltin")
    bg, accent, fg = PALETTES.get(design, PALETTES["Qora-oltin"])

    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)

    # Ramka va dekorativ elementlar
    draw.rounded_rectangle(
        (22, 22, width - 22, height - 22),
        radius=34,
        outline=accent,
        width=5,
    )
    draw.rounded_rectangle(
        (58, 72, 76, height - 72),
        radius=8,
        fill=accent,
    )

    text_x = 112
    content_right = width - 90

    # Ixtiyoriy logotip/rasm
    if logo_bytes:
        try:
            logo = Image.open(BytesIO(logo_bytes)).convert("RGB")
            logo = ImageOps.fit(logo, (170, 170))
            mask = Image.new("L", (170, 170), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, 169, 169), radius=24, fill=255
            )
            image.paste(logo, (width - 235, 70), mask)
            content_right = width - 275
        except Exception:
            logging.exception("Logotipni o'qishda xato")

    name = fit_text(data.get("name", "Ism Familiya"), 35)
    job = fit_text(data.get("job", "Kasb yoki kompaniya"), 42)

    draw.text((text_x, 92), name, font=get_font(48, True), fill=accent)
    draw.text((text_x, 174), job, font=get_font(30), fill=fg)
    draw.line((text_x, 245, width - 90, 245), fill=accent, width=3)

    rows = [
        ("TELEFON", data.get("phone", "")),
        ("MANZIL", data.get("address", "")),
        ("TELEGRAM", data.get("telegram", "")),
    ]
    y = 285
    for label, value in rows:
        value = (value or "").strip()
        if not value or value.upper() == "SKIP":
            continue
        draw.text((text_x, y), label, font=get_font(19, True), fill=accent)
        draw.text(
            (text_x + 170, y - 3),
            fit_text(value, 45),
            font=get_font(24),
            fill=fg,
        )
        y += 72

    draw.text(
        (text_x, height - 88),
        "SIZNING ISHINGIZ  |  SIZNING BRENDINGIZ",
        font=get_font(18, True),
        fill=accent,
    )

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    output.seek(0)
    output.name = "vizitka.png"
    return output


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["card"] = {}
    context.user_data["step"] = 0
    context.user_data["logo_bytes"] = None

    await update.effective_message.reply_text(
        "🎨 Vizitka yasash botiga xush kelibsiz!\n"
        "Savollarga navbat bilan javob bering.\n\n"
        + QUESTIONS[0][1],
        reply_markup=ReplyKeyboardRemove(),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.effective_message.reply_text(
        "Jarayon bekor qilindi. Qayta boshlash uchun /start yozing.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        card = context.user_data["card"]
        photo = create_business_card(card, context.user_data.get("logo_bytes"))
        await update.effective_message.reply_photo(
            photo=photo,
            caption=(
                "✅ Vizitkangiz tayyor!\n"
                "Yana vizitka yaratish uchun /start yozing."
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        logging.exception("Vizitka yaratishda xatolik")
        await update.effective_message.reply_text(
            "Vizitka yaratishda xatolik bo'ldi. /start bilan qayta urinib ko'ring."
        )
    finally:
        context.user_data.clear()


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") != 6:
        await update.effective_message.reply_text(
            "Avval /start yozib, savollarga javob bering. Rasmni oxirida yuborasiz."
        )
        return

    try:
        telegram_photo = update.effective_message.photo[-1]
        file_obj = await context.bot.get_file(telegram_photo.file_id)
        buffer = BytesIO()
        await file_obj.download_to_memory(out=buffer)
        context.user_data["logo_bytes"] = buffer.getvalue()
        await send_card(update, context)
    except Exception:
        logging.exception("Rasmni yuklashda xatolik")
        await update.effective_message.reply_text(
            "Rasmni olishda xatolik bo'ldi. Qayta yuboring yoki SKIP yozing."
        )


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    if "step" not in context.user_data:
        await message.reply_text("Boshlash uchun /start yozing.")
        return

    value = message.text.strip()
    step = context.user_data["step"]

    if step < 5:
        key = QUESTIONS[step][0]
        if step == 0 and not value:
            await message.reply_text("Ism-familiyangizni kiriting.")
            return
        context.user_data["card"][key] = "" if value.upper() == "SKIP" else value
        next_step = step + 1
        context.user_data["step"] = next_step

        if next_step < 5:
            await message.reply_text(QUESTIONS[next_step][1])
        else:
            await message.reply_text(
                "6/6. Dizayn turini tanlang:",
                reply_markup=DESIGN_BUTTONS,
            )
        return

    if step == 5:
        if value not in PALETTES:
            await message.reply_text(
                "Iltimos, pastdagi tugmalardan birini tanlang:",
                reply_markup=DESIGN_BUTTONS,
            )
            return
        context.user_data["card"]["design"] = value
        context.user_data["step"] = 6
        await message.reply_text(
            "Logotip yoki rasmingizni yuboring.\n"
            "Rasm qo'shmoqchi bo'lmasangiz, SKIP yozing.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("SKIP")]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
        return

    if step == 6:
        if value.upper() not in ("SKIP", "YO'Q", "YOQ"):
            await message.reply_text(
                "Iltimos, logotip/rasm yuboring yoki SKIP yozing."
            )
            return
        await send_card(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.exception("Botda kutilmagan xatolik", exc_info=context.error)


def main():
    if not TOKEN:
        raise SystemExit(
            "BOT_TOKEN topilmadi.\n"
            "Avval terminalda shuni yozing:\n"
            "export BOT_TOKEN='BOTFATHER_BERGAN_TOKEN'"
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))
    app.add_error_handler(error_handler)

    print("Vizitka bot ishga tushdi! Telegramda /start yuboring.")
    app.run_polling()


if __name__ == "__main__":
    main()
