# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.helper_func import encode, get_message_id
from helper.font_converter import to_small_caps as sc

async def _genlink_common(client: Client, message: Message, restricted: bool):
    """Common logic for /genlink and /rgenlink"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")]])
        
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward message from the db channel (with quotes)')}..\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            channel_message = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except:
            return
            
        if isinstance(channel_message, CallbackQuery):
            if channel_message.data == 'cancel_batch_process':
                await channel_message.answer(sc("cancelled"), show_alert=True)
                await channel_message.message.delete()
                await message.reply(f"❌ **{sc('process cancelled.')}**")
                return
            else:
                await channel_message.answer(sc("wrong button"), show_alert=True)
                continue
            
        msg_id, channel_id = await get_message_id(client, channel_message)
        if msg_id:
            await ask_msg.delete() 
            break
        else:
            await channel_message.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is not taken from db channel')}", quote=True)
            continue

    file_name = ""
    try:
        f_msg = await client.get_messages(channel_id, msg_id)
        if f_msg:
            if f_msg.document:
                file_name = f_msg.document.file_name
            elif f_msg.caption:
                file_name = f_msg.caption.split("\n")[0][:50]
    except:
        pass
        
    token = await client.mongodb.create_file_token(channel_id, msg_id, restricted=restricted)
    link = f"https://t.me/{client.username}?start={token}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    
    text = ""
    if file_name:
        text += f"<blockquote><b>📂 {file_name}</b></blockquote>\n\n"
    text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"
    
    if restricted:
        text += "\n\n⚠️ **This file is RESTRICTED.**\nNon-premium users cannot forward or save it."
    
    await channel_message.reply_text(text, quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    await _genlink_common(client, message, restricted=False)


@Client.on_message(filters.private & filters.command('rgenlink'))
async def restricted_link_generator(client: Client, message: Message):
    await _genlink_common(client, message, restricted=True)


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.command(["start", "batch", "genlink", "rbatch", "rgenlink"]))
async def single_file_gen_handler(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return

    if message.text and message.text.startswith("/"):
        return

    try:
        msg = await message.reply(f"🔄 {sc('processing')}...", quote=True)
        
        main_channel = getattr(client, 'db_channel_id', client.db)
        
        channel_id = main_channel
        msg_id = None
        
        if hasattr(message, 'forward_origin') and message.forward_origin and message.forward_origin.type == "channel":
            forwarded_channel_id = message.forward_origin.chat.id
            extra_channels = await client.mongodb.get_db_channels()
            all_db_channels = [main_channel] + extra_channels
            
            if forwarded_channel_id in all_db_channels:
                msg_id = message.forward_origin.message_id
                channel_id = forwarded_channel_id
        
        elif message.forward_from_chat:
            forwarded_channel_id = message.forward_from_chat.id
            extra_channels = await client.mongodb.get_db_channels()
            all_db_channels = [main_channel] + extra_channels
            if forwarded_channel_id in all_db_channels:
                msg_id = message.forward_from_message_id
                channel_id = forwarded_channel_id
        
        if not msg_id:
            channel_id = await client.mongodb.get_next_db_channel(main_channel)
            post = await message.copy(chat_id=channel_id, caption=message.caption)
            msg_id = post.id
             
        file_name = message.document.file_name if message.document else ""
        if not file_name and message.caption:
            file_name = message.caption.split("\n")[0][:50]
            
        token = await client.mongodb.create_file_token(channel_id, msg_id)
        link = f"https://t.me/{client.username}?start={token}"
        
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
        
        text = ""
        if file_name:
            text += f"<blockquote><b>📂 {file_name}</b></blockquote>\n\n"
        text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"
        
        await msg.edit_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        print(f"Error in single_file_gen: {e}")
        await message.reply(f"❌ {sc('error')}: {e}")
