import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN_ID, FORCE_CHANNEL, API_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


# FORCE JOIN CHECK
async def check_join(user_id):
    try:
        member = await bot.get_chat_member(f"@{FORCE_CHANNEL}", user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False


# START COMMAND
@dp.message(CommandStart())
async def start_cmd(message: Message):
    joined = await check_join(message.from_user.id)

    if not joined:
        btn = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Join Channel",
                        url=f"https://t.me/{FORCE_CHANNEL}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Joined",
                        callback_data="check_join"
                    )
                ]
            ]
        )

        return await message.answer(
            """
<b>🚫 Access Denied</b>

🔔 Join our updates channel to use this bot.

After joining click <b>Joined</b> button.
            """,
            reply_markup=btn
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Updates",
                    url=f"https://t.me/{FORCE_CHANNEL}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 Bot Owner",
                    url="https://t.me/lII_KING_IIl"
                )
            ]
        ]
    )

    text = f"""
<b>✨ Welcome {message.from_user.first_name}</b>

🚀 <b>Advanced TeraBox Downloader Bot</b>

📥 Send any TeraBox link and I will instantly fetch:

• Video
• File Name
• Thumbnail
• Fast Download Link

⚡ Powered by NovaBotz
    """

    await message.answer_photo(
        photo="https://i.imgur.com/8Km9tLL.jpeg",
        caption=text,
        reply_markup=keyboard
    )


# CHECK JOIN BUTTON
@dp.callback_query(F.data == "check_join")
async def joined_checker(callback: CallbackQuery):
    joined = await check_join(callback.from_user.id)

    if joined:
        await callback.message.edit_text(
            "✅ Verification Successful\n\nNow send your TeraBox link."
        )
    else:
        await callback.answer(
            "❌ You have not joined channel yet.",
            show_alert=True
        )


# LINK HANDLER
@dp.message()
async def terabox_handler(message: Message):
    joined = await check_join(message.from_user.id)

    if not joined:
        return await message.answer(
            f"❌ Join @{FORCE_CHANNEL} first."
        )

    url = message.text.strip()

    if "terabox" not in url and "1024tera" not in url:
        return await message.answer(
            "❌ Please send valid TeraBox link."
        )

    wait = await message.reply(
        "⏳ Fetching TeraBox Data..."
    )

    try:
        api = API_URL + url
        response = requests.get(api, timeout=30)
        data = response.json()

        if not data.get("status"):
            return await wait.edit_text(
                "❌ Failed to fetch data."
            )

        result = data.get("data")

        title = result.get("title", "Unknown")
        thumbnail = result.get("thumbnail")
        download = result.get("download_link")
        size = result.get("size", "Unknown")

        caption = f"""
<b>✅ TeraBox File Found</b>

📁 <b>Name:</b> {title}
📦 <b>Size:</b> {size}

🚀 Fast Download Ready
        """

        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬇️ Download",
                        url=download
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📢 Updates",
                        url=f"https://t.me/{FORCE_CHANNEL}"
                    )
                ]
            ]
        )

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=thumbnail,
            caption=caption,
            reply_markup=buttons
        )

        await wait.delete()

        # ADMIN LOG
        try:
            await bot.send_message(
                ADMIN_ID,
                f"""
📥 New User Activity

👤 User: {message.from_user.full_name}
🆔 ID: {message.from_user.id}
🔗 Link: {url}
                """
            )
        except:
            pass

    except Exception as e:
        await wait.edit_text(
            f"❌ Error:\n<code>{e}</code>"
        )


# RUN BOT
async def main():
    print("Bot Started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
