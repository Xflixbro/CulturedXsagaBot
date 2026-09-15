# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from helper.helper_func import encode, shorten_url
from config import SUPREME_ENABLED
from antiguard import generate_supreme_url


@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    main_channel = getattr(client, 'db_channel_id', client.db)

    if await client.mongodb.is_multi_db_enabled():
        extra_channels = await client.mongodb.get_db_channels()
        all_channels = [main_channel] + extra_channels
    else:
        all_channels = [main_channel]

    if message.chat.id not in all_channels:
        return

    if client.disable_btn:
        return

    channel_id = message.chat.id
    msg_id = message.id

    # 🔐 Generate hybrid token (stored in MongoDB)
    try:
        token = await client.mongodb.create_file_token(channel_id, msg_id)
        telegram_link = f"https://t.me/{client.username}?start={token}"
    except Exception:
        converted_id = msg_id * abs(channel_id)
        base64_string = await encode(f"get-{converted_id}")
        telegram_link = f"https://t.me/{client.username}?start={base64_string}"

    # 🌐 Apply shortener (existing behavior)
    shortener_url = await shorten_url(telegram_link)

    # 🛡️ Wrap the FINAL destination (shortener or fallback) in Supreme Gateway
    final_link = generate_supreme_url(shortener_url)

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={final_link}')
    ]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
