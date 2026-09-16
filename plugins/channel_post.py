# Made by @Awakeners_Bots
# channel_post.py

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper.helper_func import encode, shorten_url
from plugins.antibypass import create_masked_link


@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    main_channel = getattr(client, "db_channel_id", client.db)

    if await client.mongodb.is_multi_db_enabled():
        extra_channels = await client.mongodb.get_db_channels()
        all_channels = [main_channel] + extra_channels
    else:
        all_channels = [main_channel]

    if message.chat.id not in all_channels:
        return
    if client.disable_btn:
        return

    try:
        token = await client.mongodb.create_file_token(message.chat.id, message.id)
    except Exception:
        token = await encode(f"get-{message.id * abs(message.chat.id)}")

    bot_link = f"https://t.me/{client.username}?start={token}"
    shortener_url = await shorten_url(bot_link)

    masked = await create_masked_link(
        client=client,
        user_id=None,
        original_base64=token,
        shortener_url=shortener_url,
    )

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🔁 Share URL",
            url=f"https://telegram.me/share/url?url={masked['masked_url']}",
        )
    ]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
