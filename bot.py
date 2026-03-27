import logging
import re
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
import instaloader
from moviepy import VideoFileClip

# ENV
load_dotenv()
API_TOKEN = os.getenv("8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

L = instaloader.Instaloader()

# START
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "📥 Instagram bot\n\n"
        "1. Link yubor → video/audio\n"
        "2. Username yubor → story\n\n"
        "Misol:\n"
        "audio https://instagram.com/reel/...\n"
        "video https://instagram.com/reel/...\n"
        "username"
    )

# ASOSIY HANDLER
@dp.message()
async def handler(message: Message):
    text = message.text.strip()

    # 🎥🎵 LINK BO'LSA
    if "instagram.com" in text:
        await handle_link(message, text)
    else:
        await handle_story(message, text)

# VIDEO / AUDIO
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

        os.makedirs("temp", exist_ok=True)
        L.download_post(post, target="temp")

        video_path = None
        for file in os.listdir("temp"):
            if file.endswith(".mp4"):
                video_path = f"temp/{file}"
                break

        if not video_path:
            await message.answer("❌ Video topilmadi")
            return

        # 🎵 AUDIO
        if mode == "audio":
            audio_path = video_path.replace(".mp4", ".mp3")

            with VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    await message.answer("❌ Audio topilmadi")
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
    await message.answer("⏳ Story tekshirilmoqda...")

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        found = False

        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                found = True
                L.download_storyitem(item, target=username)

                if item.is_video:
                    await message.answer_video(FSInputFile(f"{username}/{item.date_utc}.mp4"))
                else:
                    await message.answer_photo(FSInputFile(f"{username}/{item.date_utc}.jpg"))

        if not found:
            await message.answer("❌ Story topilmadi")
        else:
            await message.answer("✅ Storylar yuborildi")

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# RUN
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
