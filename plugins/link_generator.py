# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.helper_func import encode, get_message_id
from helper.font_converter import to_small_caps as sc

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")]])
    
    # Step 1: First Message
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward the')} **{sc('first message')}** {sc('from db channel (with quotes)')}..\n\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            first_response = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
            
        if isinstance(first_response, CallbackQuery):
            if first_response.data == 'cancel_batch_process':
                await first_response.answer(sc("cancelled"), show_alert=True)
                await first_response.message.delete()
                await message.reply(f"❌ **{sc('batch process cancelled.')}**")
                return
            else:
                await first_response.answer(sc("wrong button"), show_alert=True)
                continue
            
        f_msg_id, f_channel_id = await get_message_id(client, first_response)
        if f_msg_id:
            await ask_msg.delete() 
            break
        else:
            await first_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote = True)
            continue

    # Step 2: Last Message
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward the')} **{sc('last message')}** {sc('from db channel (with quotes)')}..\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            second_response = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        
        if isinstance(second_response, CallbackQuery):
            if second_response.data == 'cancel_batch_process':
                await second_response.answer(sc("cancelled"), show_alert=True)
                await second_response.message.delete()
                await message.reply(f"❌ **{sc('batch process cancelled.')}**")
                return
            else:
                await second_response.answer(sc("wrong button"), show_alert=True)
                continue

        s_msg_id, s_channel_id = await get_message_id(client, second_response)
        if s_msg_id:
            await ask_msg.delete()
            break
        else:
            await second_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote = True)
            continue

    # Fetch first message to get a name
    try:
        first_msg = await client.get_messages(f_channel_id, f_msg_id)
        batch_name = ""
        if first_msg:
             if first_msg.document:
                 batch_name = first_msg.document.file_name
             elif first_msg.caption:
                 batch_name = first_msg.caption.split("\n")[0][:50] + "..."
        
        info_text = f"<blockquote><b>📦 {sc('batch create')}</b>\n"
        if batch_name:
             info_text += f"📄 {batch_name}\n"
        info_text += f"🔢 {sc('range')}: {f_msg_id} - {s_msg_id}</blockquote>\n\n"
        
    except:
        info_text = ""

    # Hybrid Token for Batch Range
    try:
        token = await client.mongodb.create_file_token(f_channel_id, f_msg_id, is_batch=True, end_msg_id=s_msg_id)
        link = f"https://t.me/{client.username}?start={token}"
    except Exception as e:
        print(f"Token creation failed for batch: {e}")
        string = f"get-{f_msg_id * abs(f_channel_id)}-{s_msg_id * abs(f_channel_id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    await second_response.reply_text(f"{info_text}<b>{sc('here is your link')}</b>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command('rbatch'))
async def restricted_batch(client: Client, message: Message):
    """Create a restricted batch link - non-premium users cannot forward/save files"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")]])
    
    # Step 1: First Message
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward the')} **{sc('first message')}** {sc('from db channel (with quotes)')}..\n\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            first_response = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
            
        if isinstance(first_response, CallbackQuery):
            if first_response.data == 'cancel_batch_process':
                await first_response.answer(sc("cancelled"), show_alert=True)
                await first_response.message.delete()
                await message.reply(f"❌ **{sc('batch process cancelled.')}**")
                return
            else:
                await first_response.answer(sc("wrong button"), show_alert=True)
                continue
            
        f_msg_id, f_channel_id = await get_message_id(client, first_response)
        if f_msg_id:
            await ask_msg.delete() 
            break
        else:
            await first_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote = True)
            continue

    # Step 2: Last Message
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward the')} **{sc('last message')}** {sc('from db channel (with quotes)')}..\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            second_response = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        
        if isinstance(second_response, CallbackQuery):
            if second_response.data == 'cancel_batch_process':
                await second_response.answer(sc("cancelled"), show_alert=True)
                await second_response.message.delete()
                await message.reply(f"❌ **{sc('batch process cancelled.')}**")
                return
            else:
                await second_response.answer(sc("wrong button"), show_alert=True)
                continue

        s_msg_id, s_channel_id = await get_message_id(client, second_response)
        if s_msg_id:
            await ask_msg.delete()
            break
        else:
            await second_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote = True)
            continue

    # Fetch first message to get a name
    try:
        first_msg = await client.get_messages(f_channel_id, f_msg_id)
        batch_name = ""
        if first_msg:
             if first_msg.document:
                 batch_name = first_msg.document.file_name
             elif first_msg.caption:
                 batch_name = first_msg.caption.split("\n")[0][:50] + "..."
        
        info_text = f"<blockquote><b>🔒 {sc('restricted batch create')}</b>\n"
        if batch_name:
             info_text += f"📄 {batch_name}\n"
        info_text += f"🔢 {sc('range')}: {f_msg_id} - {s_msg_id}</blockquote>\n\n"
        
    except:
        info_text = ""

    # Hybrid Token for Restricted Batch Range
    try:
        token = await client.mongodb.create_file_token(f_channel_id, f_msg_id, is_batch=True, end_msg_id=s_msg_id, restricted=True)
        link = f"https://t.me/{client.username}?start={token}"
    except Exception as e:
        print(f"Token creation failed for restricted batch: {e}")
        # Fallback: use rbatch_ prefix
        batch_id = f"rbatch_{f_msg_id}_{s_msg_id}_{abs(f_channel_id)}"
        link = f"https://t.me/{client.username}?start={batch_id}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    reply_text = f"{info_text}<b>{sc('here is your restricted batch link')}</b>\n\n<code>{link}</code>\n\n<i>{sc('non-premium users cannot forward or save files from this batch')}</i>"
    await second_response.reply_text(reply_text, quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")]])
        
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward message from the db channel (with quotes)')}..\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            channel_message = await client.listen(chat_id = message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
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
            await channel_message.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is not taken from db channel')}", quote = True)
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
        
    try:
        token = await client.mongodb.create_file_token(channel_id, msg_id)
        link = f"https://t.me/{client.username}?start={token}"
    except:
        base64_string = await encode(f"get-{msg_id * abs(channel_id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    
    text = ""
    if file_name:
        text += f"<blockquote><b>📂 {file_name}</b></blockquote>\n\n"
    text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"
    
    await channel_message.reply_text(text, quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command('rgenlink'))
async def restricted_link_generator(client: Client, message: Message):
    """Generate a restricted link - non-premium users cannot forward/save"""
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
            await channel_message.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is not taken from db channel')}", quote = True)
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
        
    # Generate restricted token
    try:
        token = await client.mongodb.create_file_token(channel_id, msg_id, restricted=True)
        link = f"https://t.me/{client.username}?start={token}"
    except:
        # Fallback: use rget- prefix in base64
        channel_id_clean = str(channel_id).replace("-100", "")
        base64_string = await encode(f"rget-{channel_id_clean}-{msg_id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    
    text = ""
    if file_name:
        text += f"<blockquote><b>🔒 {sc('restricted')} - {file_name}</b></blockquote>\n\n"
    text += f"<b>{sc('here is your restricted link')}</b>\n\n<code>{link}</code>\n\n"
    text += f"<i>{sc('non-premium users cannot forward or save this file')}</i>"
    
    await channel_message.reply_text(text, quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.command(["start", "batch", "rbatch", "genlink", "rgenlink"]))
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
            
        try:
            token = await client.mongodb.create_file_token(channel_id, msg_id)
            link = f"https://t.me/{client.username}?start={token}"
        except Exception as e:
            print(f"Token creation failed: {e}")
            base64_string = await encode(f"get-{msg_id * abs(channel_id)}")
            link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
        
        text = ""
        if file_name:
             text += f"<blockquote><b>📂 {file_name}</b></blockquote>\n\n"
        text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"
        
        await msg.edit_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        print(f"Error in single_file_gen: {e}")
        await message.reply(f"❌ {sc('error')}: {e}")
