import logging
import re
import os
import asyncio
from pathlib import Path

import instaloader
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

# ====================== SOZLAMALAR ======================
logging.basicConfig(level=logging.INFO)

# TOKENNI SHU YERGA YOZING
API_TOKEN = "8793753588:AAH18bYf6jLt8GiT1P3gBL_xTmIDRuUHU4c"   # ← o'zgartiring

# cookies.txt fayli joylashuvi (bot.py bilan bir papkada bo'lsa "cookies.txt")
COOKIES_FILE = "cookies.txt"

# Yuklab olingan fayllar saqlanadigan papka
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# ====================== INSTALOADER SOZLASH ======================
L = instaloader.Instaloader(
    dirname_pattern=str(DOWNLOAD_DIR / "{target}"),
    filename_pattern="{date_utc}_UTC_{shortcode}",
    download_pictures=True,
    download_videos=True,
    download_video_thumbnails=False,
    compress_json=False,
    save_metadata=False,
)

# Cookies yuklash
try:
    if os.path.exists(COOKIES_FILE):
        L.context.load_cookies(cookiefile=COOKIES_FILE)
        print("✅ Cookies muvaffaqiyatli yuklandi!")
    else:
        print("⚠️ cookies.txt topilmadi! Faqat public kontent ishlaydi.")
except Exception as e:
    print(f"❌ Cookies yuklashda xato: {e}")
    print("   cookies.txt faylidagi rur cookieni qo'shtirnoqlardan tozalang!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ====================== YORDAMCHI FUNKSIYALAR ======================
def extract_shortcode(url: str):
    """Instagram linkdan shortcode ni ajratib oladi"""
    patterns = [
        r"instagram\.com/(?:p|reel|tv|stories)/([A-Za-z0-9_-]+)",
        r"instagram\.com/[^/]+/([A-Za-z0-9_-]+)/?",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def clean_downloads():
    """Eski fayllarni tozalash (ixtiyoriy)"""
    for file in DOWNLOAD_DIR.glob("**/*"):
        if file.is_file() and file.suffix in [".mp4", ".jpg", ".jpeg", ".png"]:
            try:
                if os.path.getsize(file) > 0:
                    continue
                file.unlink()
            except:
                pass

# ====================== HANDLERLAR ======================
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Salom! Instagramdan yuklab beruvchi botga xush kelibsiz.\n\n"
        "Quyidagilarni yuboring:\n"
        "• Reels / Post / Video linki\n"
        "• Story uchun: @username\n\n"
        "Misollar:\n"
        "https://www.instagram.com/reel/C123abc/\n"
        "@sardor\n\n"
        "Bot faqat public kontentni yuklay oladi (cookies bilan yaxshiroq ishlaydi)."
    )

@dp.message(F.text)
async def handle_any_message(message: Message):
    text = message.text.strip()

    if "instagram.com" in text:
        await download_post_or_reel(message, text)
    elif text.startswith("@") or (len(text) > 3 and not text.startswith("http")):
        username = text.lstrip("@").strip()
        await download_story(message, username)
    else:
        await message.answer("❌ Instagram link yoki @username yuboring!")

async def download_post_or_reel(message: Message, url: str):
    await message.answer("🔄 Yuklab olinmoqda... Biroz kuting ⏳")

    shortcode = extract_shortcode(url)
    if not shortcode:
        await message.answer("❌ Linkni to'g'ri yuboring!")
        return

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Yuklab olish
        L.download_post(post, target=DOWNLOAD_DIR / "temp")

        # Video yoki rasm topish
        video_files = list(DOWNLOAD_DIR.glob("**/*.mp4"))
        photo_files = list(DOWNLOAD_DIR.glob("**/*.[jp][pn]g"))

        sent = False

        # Avval video yuborishga harakat qilamiz
        for file in video_files:
            if file.stat().st_size > 0:
                video = FSInputFile(file)
                await message.answer_video(video, caption=f"✅ Yuklandi: {post.caption[:200] if post.caption else ''}")
                sent = True
                break

        # Agar video bo'lmasa — rasm yuboramiz
        if not sent:
            for file in photo_files:
                if file.stat().st_size > 0:
                    photo = FSInputFile(file)
                    await message.answer_photo(photo, caption=f"✅ Yuklandi")
                    sent = True
                    break

        if not sent:
            await message.answer("⚠️ Media topilmadi, lekin yuklab olingan.")

    except instaloader.exceptions.InstaloaderException as e:
        await message.answer(f"❌ Instagram xatosi: {str(e)[:300]}")
    except Exception as e:
        await message.answer(f"❌ Umumiy xato: {str(e)[:300]}")
    finally:
        # Tozalash
        await asyncio.sleep(2)
        for f in DOWNLOAD_DIR.glob("**/*"):
            try:
                if f.is_file():
                    f.unlink()
            except:
                pass

async def download_story(message: Message, username: str):
    await message.answer(f"📖 @{username} ning storysi yuklanmoqda... ⏳")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        stories = L.get_stories(userids=[profile.userid])

        count = 0
        for story in stories:
            for item in story.get_items():
                L.download_storyitem(item, target=DOWNLOAD_DIR / "stories")
                count += 1

                # Har bir story ni yuborish
                for file in DOWNLOAD_DIR.glob("**/*.mp4"):
                    if file.stat().st_size > 0:
                        await message.answer_video(FSInputFile(file))
                        file.unlink()
                        break
                for file in DOWNLOAD_DIR.glob("**/*.[jp][pn]g"):
                    if file.stat().st_size > 0:
                        await message.answer_photo(FSInputFile(file))
                        file.unlink()
                        break

        if count == 0:
            await message.answer(f"@{username} da hozircha story yo'q.")
        else:
            await message.answer(f"✅ @{username} dan {count} ta story yuklandi va yuborildi.")

    except instaloader.exceptions.ProfileNotExistsException:
        await message.answer(f"❌ @{username} topilmadi.")
    except Exception as e:
        await message.answer(f"❌ Story yuklashda xato: {str(e)[:250]}")

# ====================== BOTNI ISHGA TUSHIRISH ======================
async def main():
    await clean_downloads()
    print("🚀 Instagram Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
