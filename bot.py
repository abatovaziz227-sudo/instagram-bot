import logging
import re
import os
import asyncio
import shutil
from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
import instaloader
from moviepy import VideoFileClip

# ENV
load_dotenv()
API_TOKEN = os.getenv("8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c")

if not API_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

L = instaloader.Instaloader()

# START
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🤖 Instagram bot\n\n"
        "📥 Link yubor → video/audio\n"
        "👤 Username yubor → story\n\n"
        "Misol:\n"
        "audio https://instagram.com/reel/...\n"
        "video https://instagram.com/reel/...\n"
        "cristiano"
    )

# ASOSIY HANDLER
@dp.message()
async def handler(message: Message):
    text = message.text.strip()

    if "instagram.com" in text:
        await handle_link(message, text)
    else:
        await handle_story(message, text)

# 🎥🎵 VIDEO / AUDIO
async def handle_link(message: Message, text: str):
    await message.answer("⏳ Yuklanmoqda...")

    try:
        mode = "video"

        if text.startswith("audio"):
            mode = "audio"
            url = text.replace("audio", "").strip()
        elif text.startswith("video"):
            mode = "video"
            url = text.replace("video", "").strip()
        else:
            url = text

        match = re.search(r"/(reel|p|tv)/([^/]+)/", url)
        if not match:
            await message.answer("❌ Noto‘g‘ri link")
            return

        shortcode = match.group(2)
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # temp tozalash
        if os.path.exists("temp"):
            shutil.rmtree("temp")

        os.makedirs("temp", exist_ok=True)

        L.download_post(post, target="temp")

        video_path = None
        for file in os.listdir("temp"):
            if file.endswith(".mp4"):
                video_path = os.path.join("temp", file)
                break

        if not video_path:
            await message.answer("❌ Video topilmadi")
            return

        # 🎵 AUDIO
        if mode == "audio":
            audio_path = video_path.replace(".mp4", ".mp3")

            with VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    await message.answer("❌ Audio yo‘q")
                    return
                clip.audio.write_audiofile(audio_path)

            await message.answer_audio(FSInputFile(audio_path))
            os.remove(audio_path)

        # 🎥 VIDEO
        else:
            await message.answer_video(FSInputFile(video_path))

        os.remove(video_path)
        await message.answer("✅ Tayyor!")

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# 📸 STORY
async def handle_story(message: Message, username: str):
    await message.answer("⏳ Story yuklanmoqda...")

    try:
        # eski papkani o‘chiramiz
        if os.path.exists(username):
            shutil.rmtree(username)

        os.makedirs(username, exist_ok=True)

        profile = instaloader.Profile.from_username(L.context, username)

        found = False

        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                found = True
                L.download_storyitem(item, target=username)

        if not found:
            await message.answer("❌ Story topilmadi")
            return

        # 🔥 REAL FAYLLARNI YUBORISH
        for file in os.listdir(username):
            path = os.path.join(username, file)

            if file.endswith(".mp4"):
                await message.answer_video(FSInputFile(path))
            elif file.endswith(".jpg"):
                await message.answer_photo(FSInputFile(path))

        await message.answer("✅ Storylar yuborildi")

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# RUN
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
