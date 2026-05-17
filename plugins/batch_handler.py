# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

# Batch Link Handler
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.font_converter import to_small_caps as sc
from helper.quality_detector import get_quality_priority
from helper.helper_func import encode, decode, get_messages, delete_files
from collections import defaultdict
import asyncio
import humanize


async def process_batch(client: Client, message: Message, batch_id: str):
    """Process a batch (normal or restricted) and send files according to premium status."""
    user_id = message.from_user.id
    batch = await client.mongodb.get_batch(batch_id)
    
    if not batch:
        await message.reply(f"❌ {sc('batch not found or expired')}")
        return
    
    is_premium = await client.mongodb.is_premium(user_id)
    restricted = batch.get('restricted', False)
    
    # Get user credits
    from helper.enhanced_credit_db import EnhancedCreditDB
    enhanced_db = EnhancedCreditDB(client.db_uri, client.db_name)
    credit_data = await enhanced_db.get_credits(user_id)
    user_credits = credit_data.get("balance", 0)
    
    # Check if credit system is enabled
    credit_system_enabled = await client.mongodb.is_credit_system_enabled()
    if not credit_system_enabled:
        user_credits = 0
    
    # Determine batch type (Season vs Episode)
    qualities = set(f['quality'] for f in batch['files'])
    is_season_batch = len(qualities) <= 1
    
    # Import helpers needed for formatting
    from helper.quality_detector import parse_episode_info, get_series_name
    
    # Sort files
    if is_season_batch:
        files = sorted(batch['files'], key=lambda f: parse_episode_info(f['filename']).get('episode', 0) or 0)
    else:
        files = sorted(batch['files'], key=lambda f: get_quality_priority(f['quality']))
    
    # If Season Batch -> Send Files Directly
    if is_season_batch:
        file_ids = [int(f['file_id']) for f in files]
        
        msg_to_delete = await message.reply(f"{sc('processing')}.. ⏳")
        
        try:
            files_by_channel = defaultdict(list)
            for f in files:
                channel_id = f.get('channel_id', int(client.db))
                channel_id = int(str(channel_id).replace("-100", ""))
                files_by_channel[channel_id].append(int(f['file_id']))
            
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
        
        # Determine if protection should be applied
        use_protect = restricted and not is_premium
        
        sent_msgs = []
        for msg in messages:
            caption = (
                client.messages.get('CAPTION', '').format(
                    previouscaption=f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption else f"<blockquote>{msg.document.file_name}</blockquote>"
                )
                if client.messages.get('CAPTION', '') and msg.document
                else (msg.caption.html if msg.caption else "")
            )
            
            try:
                copied = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    protect_content=use_protect
                )
                sent_msgs.append(copied)
            except Exception as e:
                pass
        
        # Add warning message for restricted files
        if restricted and not is_premium and sent_msgs:
            await client.send_message(
                user_id,
                f"⚠️ **{sc('restricted file')}**\n\n{sc('you cannot forward or save this file because it is restricted. premium users can forward/save.')}"
            )
                
        # Auto-Delete Logic
        if sent_msgs and client.auto_del > 0:
            warning = await message.reply(
                f"<b>⚠️ {sc('files will be deleted in')} {humanize.naturaldelta(client.auto_del)}.</b>"
            )
            asyncio.create_task(delete_files(sent_msgs, client, warning, message.text))
            
        return

    # Else (Episode Pack) -> Show Menu
    msg = f"""**📦 {sc('batch download')}**

**{sc('title')}:** {batch['base_name']}
**{sc('type')}:** {sc('episode pack')}

"""
    
    buttons = []
    for file_data in files:
        quality = file_data['quality']
        filename = file_data['filename']
        file_id = file_data['file_id']
        
        button_text = f"📥 {quality}"
            
        if is_premium or (credit_system_enabled and user_credits > 0):
            button_text += " ✅"
        
        # Pass restricted info in callback data
        buttons.append([InlineKeyboardButton(
            button_text,
            callback_data=f"batchfile_{batch_id}_{file_id}_{restricted}"
        )])
    
    msg += f"\n{sc('select file to download')}"
    
    if restricted and not is_premium:
        msg += f"\n\n🔒 **{sc('restricted batch')}** - {sc('you cannot forward or save these files')}"
    
    if not is_premium and user_credits == 0 and credit_system_enabled:
        msg += f"\n\n⚠️ {sc('you need credits or premium to access files')}"
        
    if client.auto_del > 0:
        msg += f"\n\n⏳ {sc('files auto-delete in')} {humanize.naturaldelta(client.auto_del)}"
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(msg, reply_markup=keyboard)


@Client.on_message(filters.private & filters.text, group=1)
async def batch_link_handler(client: Client, message: Message):
    """Handle batch link access"""
    
    if not message.text or not message.text.startswith("/start "):
        return
    
    text = message.text
    param = text.replace("/start ", "").strip()
    
    # Handle normal batch (batch_ prefix)
    if param.startswith("batch_"):
        batch_id = param.replace("batch_", "").strip()
        await process_batch(client, message, batch_id)
        return
    
    # Handle restricted batch (rbatch_ prefix)
    if param.startswith("rbatch_"):
        batch_id = param.replace("rbatch_", "").strip()
        await process_batch(client, message, batch_id)
        return
    
    # Handle hybrid token (will be processed by start.py)
    # Don't process other start parameters here


@Client.on_callback_query(filters.regex(r"^batchfile_"))
async def batch_file_callback(client: Client, query: CallbackQuery):
    """Handle batch file selection"""
    
    data = query.data.split("_")
    batch_id = data[1]
    file_id = data[2]
    restricted = data[3] == "True" if len(data) > 3 else False
    
    user_id = query.from_user.id
    
    # Get the actual file message
    batch = await client.mongodb.get_batch(batch_id)
    if not batch:
        await query.answer("❌ Batch expired", show_alert=True)
        return
    
    # Find the file
    file_data = next((f for f in batch['files'] if f['file_id'] == file_id), None)
    if not file_data:
        await query.answer("❌ File not found", show_alert=True)
        return
    
    is_premium = await client.mongodb.is_premium(user_id)
    
    # Generate token for this specific file
    try:
        msg_id = int(file_id)
        channel_id = file_data.get('channel_id', client.db)
        channel_id = str(channel_id).replace("-100", "")
        
        # Create token with restricted flag
        token = await client.mongodb.create_file_token(
            int(f"-100{channel_id}"), 
            msg_id, 
            restricted=restricted
        )
        encoded_token = token  # Token is already the ID
        
        file_link = f"https://t.me/{client.username}?start={encoded_token}"
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Error generating link: {e}")
        # Fallback for restricted file
        token_string = f"rget-{channel_id}-{msg_id}"
        encoded_token = await encode(token_string)
        file_link = f"https://t.me/{client.username}?start={encoded_token}"
    
    timer_text = ""
    if client.auto_del > 0:
        timer_text = f"\n\n⏳ **{sc('warning')}:** {sc('file auto-deletes in')} {humanize.naturaldelta(client.auto_del)} {sc('after opening')}"
    
    restriction_text = ""
    if restricted and not is_premium:
        restriction_text = f"\n\n🔒 **{sc('restricted file')}** - {sc('you cannot forward or save this file')}"
    elif restricted and is_premium:
        restriction_text = f"\n\n✅ **{sc('premium user')}** - {sc('you can forward and save this file')}"
    
    await query.message.reply(
        f"**📥 {file_data['quality']}**\n"
        f"📄 {file_data['filename']}"
        f"{timer_text}"
        f"{restriction_text}\n\n"
        f"{sc('click below to access')}:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"📥 {sc('get file')}", url=file_link)]
        ])
    )
    await query.answer()
