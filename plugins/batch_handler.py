# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.font_converter import to_small_caps as sc
from helper.quality_detector import get_quality_priority
import asyncio
import humanize
from collections import defaultdict

async def _batch_common(client: Client, message: Message, restricted: bool):
    """Common logic for /batch and /rbatch"""
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
            
        from helper.helper_func import get_message_id
        f_msg_id, f_channel_id = await get_message_id(client, first_response)
        if f_msg_id:
            await ask_msg.delete() 
            break
        else:
            await first_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote=True)
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
            await second_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote=True)
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

    # Create batch token (range token) with restricted flag
    token = await client.mongodb.create_file_token(f_channel_id, f_msg_id,
                                                   end_msg_id=s_msg_id,
                                                   is_batch=True,
                                                   restricted=restricted)
    link = f"https://t.me/{client.username}?start={token}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    reply_text = f"{info_text}<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"
    if restricted:
        reply_text += "\n\n⚠️ **This batch is RESTRICTED.**\nEach file will be sent with forwarding protection for non-premium users."
    await second_response.reply_text(reply_text, quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    await _batch_common(client, message, restricted=False)


@Client.on_message(filters.private & filters.command('rbatch'))
async def restricted_batch(client: Client, message: Message):
    await _batch_common(client, message, restricted=True)


async def process_batch(client: Client, message: Message, batch_id: str, restricted: bool = False):
    """Process batch download - with restricted flag support"""
    
    user_id = message.from_user.id
    
    # Get batch from database
    batch = await client.mongodb.get_batch(batch_id)
    if not batch:
        await message.reply(f"❌ {sc('batch not found or expired')}")
        return
    
    # Check if batch is restricted (token flag overrides batch flag)
    is_restricted = restricted or batch.get('restricted', False)
    
    # Check premium status
    is_premium = await client.mongodb.is_premium(user_id)
    
    # Get files
    files = batch.get('files', [])
    if not files:
        await message.reply(f"❌ {sc('no files in this batch')}")
        return
    
    # Sort files appropriately
    from helper.quality_detector import parse_episode_info, get_quality_priority
    qualities = set(f.get('quality', 'Unknown') for f in files)
    is_season_batch = len(qualities) <= 1
    
    if is_season_batch:
        files = sorted(files, key=lambda f: parse_episode_info(f.get('filename', '')).get('episode', 0) or 0)
    else:
        files = sorted(files, key=lambda f: get_quality_priority(f.get('quality', 'Unknown')))
    
    # Fetch messages from DB channels
    from helper.helper_func import get_messages, delete_files
    
    msg_to_delete = await message.reply(f"{sc('processing batch')}.. ⏳")
    
    try:
        files_by_channel = defaultdict(list)
        for f in files:
            channel_id = f.get('channel_id', client.db)
            channel_id = int(str(channel_id).replace("-100", ""))
            files_by_channel[channel_id].append(int(f.get('file_id')))
        
        messages = []
        for chat_id, msg_ids in files_by_channel.items():
            full_chat_id = int(f"-100{chat_id}")
            msgs = await get_messages(client, msg_ids, full_chat_id)
            messages.extend(msgs)
    except Exception as e:
        await msg_to_delete.edit(f"❌ Error fetching messages: {e}")
        return
    
    if not messages:
        await msg_to_delete.edit("❌ Files not found in DB channel.")
        return
    
    await msg_to_delete.delete()
    
    sent_msgs = []
    
    for idx, msg in enumerate(messages):
        caption = (
            client.messages.get('CAPTION', '').format(
                previouscaption=f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption else f"<blockquote>{msg.document.file_name}</blockquote>"
            )
            if client.messages.get('CAPTION', '') and msg.document
            else (msg.caption.html if msg.caption else "")
        )
        
        # CORRECTED PROTECT_CONTENT LOGIC FOR BATCH
        if is_restricted:
            # Premium user? Allow forwarding (protect=False)
            # Non-premium? Block forwarding (protect=True)
            protect = not is_premium
            
            # Add warning for first file only to avoid spam
            if idx == 0:
                warning_text = (
                    f"\n\n⚠️ **⏰ FILES WILL BE DELETED IN {humanize.naturaldelta(client.auto_del)}**\n"
                    f"🚫 **🔒 NON-PREMIUM USERS CANNOT FORWARD OR SAVE THESE FILES**\n"
                    f"💎 **PREMIUM USERS:** Forwarding & saving available"
                )
                if caption:
                    caption += warning_text
                else:
                    caption = warning_text
        else:
            protect = client.protect
        
        try:
            copied = await msg.copy(
                chat_id=user_id,
                caption=caption,
                protect_content=protect
            )
            sent_msgs.append(copied)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to copy message {msg.id}: {e}")
    
    # Auto-Delete Logic
    if sent_msgs and client.auto_del > 0:
        warning = await message.reply(
            f"<b>⚠️ {sc('files will be deleted in')} {humanize.naturaldelta(client.auto_del)}.</b>"
        )
        asyncio.create_task(delete_files(sent_msgs, client, warning, message.text))


# Use group=1 to give this handler lower priority than /start
@Client.on_message(filters.private & filters.text, group=1)
async def batch_link_handler(client: Client, message: Message):
    """Handle batch link access"""
    
    if not message.text or not message.text.startswith("/start "):
        return
    
    text = message.text
    param = text.replace("/start ", "").strip()
    
    # Check if it's a token (alphanumeric, 12-16 chars)
    from helper.helper_func import is_token_format
    if is_token_format(param):
        token_doc = await client.mongodb.resolve_file_token(param)
        if token_doc and token_doc.get("is_batch"):
            batch_id = param
            is_restricted = token_doc.get("restricted", False)
            await process_batch(client, message, batch_id, restricted=is_restricted)
            return


@Client.on_callback_query(filters.regex(r"^batchfile_"))
async def batch_file_callback(client: Client, query):
    """Handle batch file selection"""
    
    data = query.data.split("_")
    batch_id = data[1]
    file_id = data[2]
    
    user_id = query.from_user.id
    
    batch = await client.mongodb.get_batch(batch_id)
    if not batch:
        await query.answer("❌ Batch expired", show_alert=True)
        return
    
    file_data = next((f for f in batch['files'] if f['file_id'] == file_id), None)
    if not file_data:
        await query.answer("❌ File not found", show_alert=True)
        return
    
    msg_id = int(file_data['file_id'])
    channel_id = file_data.get('channel_id', client.db)
    
    # Check if batch is restricted
    is_restricted = batch.get('restricted', False)
    
    # Check premium status
    is_premium = await client.mongodb.is_premium(user_id)
    
    # Generate token with restricted flag
    token = await client.mongodb.create_file_token(channel_id, msg_id, restricted=is_restricted)
    file_link = f"https://t.me/{client.username}?start={token}"
    
    timer_text = ""
    if client.auto_del > 0:
        timer_text = f"\n\n⏳ **{sc('warning')}:** {sc('file auto-deletes in')} {humanize.naturaldelta(client.auto_del)} {sc('after opening')}"
    
    # Build reply text with appropriate warnings
    reply_text = f"**📥 {file_data['quality']}**\n📄 {file_data['filename']}{timer_text}\n\n{sc('click below to access')}:"
    
    if is_restricted:
        if is_premium:
            reply_text += "\n\n✅ **PREMIUM USER:** You can forward & save this file"
        else:
            reply_text += "\n\n⚠️ **RESTRICTED FILE:** You cannot forward or save this file (premium only)"
    
    await query.message.reply(
        reply_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"📥 {sc('get file')}", url=file_link)]
        ])
    )
