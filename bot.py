import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
import instaloader

API_TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

L = instaloader.Instaloader()

# AGAR HOHLASANGIZ LOGIN QILING (tavsiya qilinadi)
# L.login("username", "password")

@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.reply(
        "Salom!\n\n"
        "📥 Instagram yuklovchi bot\n\n"
        "1. Username yuboring → Story yuklayman\n"
        "2. Instagram link yuboring → Video yuklayman"
    )

# LINK ORQALI VIDEO YUKLASH
@dp.message_handler(lambda message: "instagram.com" in message.text)
async def download_video(message: Message):
    url = message.text.strip()

    await message.reply("⏳ Video yuklanmoqda...")

    try:
        shortcode = re.search(r"/(reel|p|tv)/([^/]+)/", url).group(2)
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        L.download_post(post, target="video")

        for file in post.get_sidecar_nodes() if post.typename == "GraphSidecar" else [post]:
            if file.is_video:
                video_path = f"video/{post.shortcode}.mp4"
                await message.reply_video(open(video_path, "rb"))

        await message.reply("✅ Video tayyor!")

    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")

# USERNAME ORQALI STORY YUKLASH
@dp.message_handler()
async def download_story(message: Message):
    username = message.text.strip()

    await message.reply("⏳ Story tekshirilmoqda...")

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        found = False

        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                found = True
                L.download_storyitem(item, target=username)

                if item.is_video:
                    await message.reply_video(open(f"{username}/{item.date_utc}.mp4", "rb"))
                else:
                    await message.reply_photo(open(f"{username}/{item.date_utc}.jpg", "rb"))

        if not found:
            await message.reply("❌ Story topilmadi")

        else:
            await message.reply("✅ Storylar yuborildi")

    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
