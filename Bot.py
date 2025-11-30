import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram import F
import yt_dlp

TOKEN = "8292216685:AAHhGto9O_-oSBBe3bkKIe0Pyn7tzJFDPRc"

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# ==============================
# --- INSTAGRAM VIDEO PARSER ---
# ==============================
def get_instagram_video(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    html = requests.get(url, headers=headers).text
    mp4 = re.findall(r'"video_url":"(https://[^"]+\.mp4[^"]*)"', html)

    if mp4:
        return mp4[0].replace("\\u0026", "&")

    return None


# ============================
# --- TIKTOK VIDEO PARSER ---
# ============================
def get_tiktok_video(url: str):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        data = requests.get(api_url).json()
        return data["data"]["play"]
    except:
        return None


# ============================
# --- YOUTUBE VIDEO PARSER ---
# ============================
def get_youtube_video(url: str):
    try:
        ydl_opts = {
            "format": "mp4[height<=720]",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"]
    except:
        return None


# =============================
# --- FACEBOOK VIDEO PARSER ---
# =============================
def get_facebook_video(url: str):
    try:
        api = f"https://fbdownloader.online/api?url={url}"
        data = requests.get(api).json()
        return data["download"]["sd"]
    except:
        return None


# ==========================
# --- UNIVERSAL FUNKSIYA ---
# ==========================
def get_video_url(link: str):
    if "instagram.com" in link:
        return get_instagram_video(link), "Instagram"
    if "tiktok.com" in link:
        return get_tiktok_video(link), "TikTok"
    if "youtu" in link:
        return get_youtube_video(link), "YouTube"
    if "facebook.com" in link or "fb.watch" in link:
        return get_facebook_video(link), "Facebook"

    return None, None


# =====================
# --- /start COMMAND ---
# =====================
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "🎬 Super Video Downloader Bot!\n\n"
        "Menga quyidagilarni yuboring:\n"
        "• Instagram video\n"
        "• TikTok video\n"
        "• YouTube video\n"
        "• Facebook video\n\n"
        "Bot avtomatik yuklaydi!"
    )


# =============================
# --- ASOSIY QISM: VIDEO YUBORISH ---
# =============================
@dp.message(F.text)
async def download_any(msg: types.Message):
    link = msg.text.strip()

    await msg.answer("⏳ Video izlanmoqda, kuting...")

    video_url, source = get_video_url(link)

    if not video_url:
        await msg.answer("❌ Video topilmadi. Linkni tekshiring.")
        return

    await msg.answer(f"📥 {source} videoni yuklamoqdaman...")

    try:
        await msg.reply_video(
            video_url,
            caption=f"✔️ {source} video yuklandi!"
        )
    except Exception as e:
        await msg.answer(f"❌ Xato: {e}")


# =============================
# --- BOTNI ISHGA TUSHIRISH ---
# =============================
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
bot.py      
main.py
app.py
