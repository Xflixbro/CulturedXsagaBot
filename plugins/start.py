# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from helper.helper_func import *
from helper.credit_db import credit_db
from helper.enhanced_credit_db import EnhancedCreditDB
from helper.font_converter import to_small_caps as sc
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import humanize
import secrets
import json

# Import the new button functions from others.py
from plugins.others import home_buttons, home_buttons_admin

# Load credit configuration
try:
    with open("setup.json", "r") as f:
        setup_data = json.load(f)
        credit_config = setup_data[0].get("credit_config", {})
except:
    credit_config = {}


@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    present = await client.mongodb.present_user(user_id)
    if not present:
        try:
            await client.mongodb.add_user(user_id)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error adding a user:\n{e}")

    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return await message.reply(f"**{sc('You have been banned from using this bot!')}**")
    
    # Premium check
    is_premium_user = await client.mongodb.is_premium(user_id)

    # Enhanced credit system
    enhanced_db = EnhancedCreditDB(client.db_uri, client.db_name)
    credit_data = await enhanced_db.get_credits(user_id)
    user_credits = credit_data.get("balance", 0)
    
    # Check for expired credits
    await enhanced_db.check_and_remove_expired(user_id)

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1].strip()
        except IndexError:
            return

        # ============== REFERRAL SYSTEM ==============
        if base64_string.startswith("ref_"):
            referral_code = base64_string.replace("ref_", "")
            
            if not present:
                referrer_id = await enhanced_db.apply_referral(user_id, referral_code)
                if referrer_id:
                    await message.reply(
                        f"🎉 **{sc('Welcome!')}**\n\n"
                        f"{sc('You joined using a referral link!')}\n"
                        f"{sc('When you access your first file, your referrer will earn credits!')}"
                    )
            return
            
        access_token = None
        original_base64 = base64_string
        
        # ---------------- TOKEN VERIFIED / SHORTENER SOLVED ----------------
        if "_" in base64_string:
            parts = base64_string.split("_", 1)
            if base64_string.startswith("batch_"):
                parts = base64_string.split("_")
                if len(parts) >= 3:
                     original_base64 = f"{parts[0]}_{parts[1]}"
                     access_token = parts[2]
            elif len(parts) == 2:
                original_base64 = parts[0]
                access_token = parts[1]

            if access_token:
                token_verification_enabled = await client.mongodb.get_bot_config('token_verification_enabled', True)

                if token_verification_enabled:
                    await client.mongodb.increment_token_clicks(user_id, access_token)

                    verify_result = await client.mongodb.verify_access_token(
                        user_id, access_token, original_base64
                    )
    
                    # ======================= ANTI-BYPASS LOGIC ======================
                    if verify_result == "BYPASS":
                        if user_id not in client.admins:
                            was_banned = await client.mongodb.check_and_auto_ban(user_id, max_attempts=5)
                            
                            if was_banned:
                                await message.reply(
                                    f"<blockquote>🚫 <b>{sc('you have been banned')}</b></blockquote>\n"
                                    f"<blockquote><b>{sc('reason: multiple bypass attempts detected')}</b></blockquote>\n"
                                    f"<blockquote><b>{sc('contact admin if you think this is a mistake')}</b></blockquote>"
                                )
                                return
                        
                        await message.reply(
                            f"<blockquote>⚠️ <b>{sc('bypass detected')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('how many times have i told you, dont try to outsmart your dad')}🖕</b></blockquote>\n"
                            f"<blockquote><b>{sc('now be a good boy and solve it again, and this time dont get smart !!')}</b></blockquote>"
                        )
    
                        bypass_count = await client.mongodb.get_bypass_count(user_id)
                        await client.send_message(
                            client.owner,
                            f"🚨 <b>{sc('bypass detected')}</b>\n"
                            f"{sc('user')}: <code>{user_id}</code>\n"
                            f"{sc('attempts in 24h')}: <b>{bypass_count}</b>"
                        )
                        return
                    
                    if verify_result == "ALREADY_USED":
                        await message.reply(
                            f"<blockquote>❌ <b>{sc('token already used')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('this link can only be used once')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                        )
                        return
                    
                    if verify_result == "EXPIRED":
                        await message.reply(
                            f"<blockquote>⏰ <b>{sc('token expired')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('this link has expired')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                        )
                        return
    
                    if verify_result != "OK":
                        await message.reply(
                            f"<blockquote>❌ <b>{sc('invalid token')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                        )
                        return
    
                    # ---------------- GIVE 3 CREDITS (IF ENABLED) ----------------
                    credit_system_enabled = await client.mongodb.is_credit_system_enabled()
                    
                    if credit_system_enabled:
                        expiry_days = credit_config.get("expiry_days", 30)
                        verification_reward = await client.mongodb.get_bot_config('verification_reward', 3)
                        await enhanced_db.add_credits(user_id, verification_reward, expiry_days, reason="shortener_solved")

                        credit_data = await enhanced_db.get_credits(user_id)
                        user_credits = credit_data.get("balance", 0)
    
                        await message.reply(
                            f"<b>🎉 {sc('verification successful!')}</b>\n"
                            f"✅ <b>{sc(f'you earned {verification_reward} credits!')}</b>\n"
                            f"📂 <b>{sc('sending your file now...')}</b>"
                        )
                    else:
                        await message.reply(
                            f"<b>🎉 {sc('verification successful!')}</b>\n"
                            f"📂 <b>{sc('sending your file now...')}</b>"
                        )

                    is_premium_user = True
                    
                    if original_base64.startswith("batch_"):
                         batch_id = original_base64.replace("batch_", "").strip()
                         from plugins.batch_handler import process_batch
                         await process_batch(client, message, batch_id)
                         message.stop_propagation()
                         return

        # -------------------------- HYBRID TOKEN / BASE64 DECODE --------------------------
        from helper.helper_func import is_token_format
        
        is_batch = original_base64.startswith("batch_")
        
        # Initialize variables
        ids = []
        custom_chat_id = None
        
        if not is_batch and is_token_format(original_base64):
            # ----- HYBRID TOKEN -----
            if await client.mongodb.is_token_rate_limited(user_id):
                return await message.reply(
                    f"<blockquote>⏳ <b>{sc('too many invalid attempts')}</b></blockquote>\n"
                    f"<blockquote><b>{sc('please wait a minute and try again')}</b></blockquote>"
                )
            
            token_doc = await client.mongodb.resolve_file_token(original_base64)
            
            if not token_doc:
                await client.mongodb.record_invalid_token_attempt(user_id)
                return await message.reply(
                    f"<blockquote>❌ <b>{sc('invalid or expired link')}</b></blockquote>\n"
                    f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                )
            
            channel_id = token_doc["channel_id"]
            start_msg_id = token_doc["msg_id"]
            end_msg_id = token_doc.get("end_msg_id")
            
            if end_msg_id:
                ids = list(range(start_msg_id, end_msg_id + 1))
            else:
                ids = [start_msg_id]
                
            custom_chat_id = channel_id

            # --- NEW: Verify bot can access the channel ---
            try:
                await client.get_chat(custom_chat_id)
            except Exception as e:
                return await message.reply(
                    f"❌ **Bot cannot access the channel where this file is stored.**\n"
                    f"Make sure I am still an admin in that channel.\n"
                    f"Error: {e}"
                )
            # ---------------------------------------------
            
        elif not is_batch:
            # ----- OLD BASE64 PATH -----
            try:
                string = await decode(original_base64)
                argument = string.split("-")
            except Exception:
                return
        
            if len(argument) == 3:
                # New format: get-CHANNEL_ID-MSG_ID (channel_id without -100)
                try:
                    channel_id_part = int(argument[1])
                    msg_id_part = int(argument[2])
                    custom_chat_id = int(f"-100{channel_id_part}")
                    ids = [msg_id_part]
                except:
                    # Old range format: get-ID1-ID2
                    try:
                        start = int(int(argument[1]) / abs(client.db))
                        end = int(int(argument[2]) / abs(client.db))
                        ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
                    except:
                        return
            elif len(argument) == 2:
                # Old single file format: get-GENERATED_ID
                try:
                    msg_id = int(int(argument[1]) / abs(client.db))
                    ids = [msg_id]
                except:
                    return
            else:
                return

        # ------------------ USER TRYING TO GET FILE ------------------
        
        credit_system_enabled = await client.mongodb.is_credit_system_enabled()
        token_verification_enabled = await client.mongodb.get_bot_config('token_verification_enabled', True)
        
        is_first_file = credit_data.get("total_spent", 0) == 0 and not is_premium_user

        if credit_system_enabled and user_credits > 0 and not is_premium_user:
            await enhanced_db.use_credit(user_id)
            user_credits -= 1
            is_premium_user = True

            await message.reply(
                f"⚡ {sc('1 credit used')}!\n"
                f"{sc('remaining credits')}: {user_credits}"
            )
            
            if is_first_file and credit_data.get("referred_by"):
                # reward referrer (code omitted for brevity)
                pass

        # If not premium and token verification enabled, show shortener
        if not is_premium_user and token_verification_enabled:
            temp_msg = await message.reply(f"🔄 **{sc('generating your link')}...**")
            
            content_name = ""
            try:
                if original_base64.startswith("batch_"):
                    b_id = original_base64.replace("batch_", "").strip()
                    batch = await client.mongodb.get_batch(b_id)
                    if batch:
                        content_name = f"📦 <b>{batch.get('base_name', 'Batch Pack')}</b>\n\n"
                elif ids:
                    try:
                        t_msg_id = ids[0]
                        t_chat_id = custom_chat_id if custom_chat_id else client.db
                        
                        f_msg = await client.get_messages(t_chat_id, t_msg_id)
                        if f_msg:
                            if f_msg.document:
                                content_name = f"🎬 <b>{f_msg.document.file_name}</b>\n\n"
                    except:
                        pass
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Error fetching content name: {e}")
            
            access_token = secrets.token_hex(16)
            await client.mongodb.create_access_token(user_id, original_base64, access_token)
            
            file_link = f"https://t.me/{client.username}?start={original_base64}_{access_token}"
            shortened_url = await shorten_url(file_link)
            
            await temp_msg.delete()
            
            premium_text = (
                f"{content_name}"
                f"<b>🔗 {sc('your file link')}:</b>\n\n"
                f"<blockquote>👉 {sc('solve the shortener to unlock your file')}</blockquote>\n\n"
                f"<b>💎 {sc('want direct access')}?</b> {sc('buy premium')}!"
            )
            
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"⌜{sc('ᴏᴘᴇɴ ʟɪɴᴋ')}⌟", url=shortened_url)],
                [
                    InlineKeyboardButton(f"「{sc('ᴛᴜᴛᴏʀɪᴀʟ')}」", url="https://t.me/+rKJmAabX6MxmMjg9"),
                    InlineKeyboardButton(f"「{sc('ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ')}」", url="https://t.me/PremiumXeon/11")
                ]
            ])
            
            await client.send_photo(
                chat_id=message.chat.id,
                photo="https://files.catbox.moe/bktufd.jpg",
                caption=premium_text,
                reply_markup=buttons,
                protect_content=True
            )
            if original_base64.startswith("batch_"):
                message.stop_propagation()
            return
        
        # Handle batch links after verification (if user is premium or used credits)
        if original_base64.startswith("batch_"):
             batch_id = original_base64.replace("batch_", "").strip()
             from plugins.batch_handler import process_batch
             await process_batch(client, message, batch_id)
             message.stop_propagation()
             return

        # ------------------ FETCH AND SEND FILES ------------------
        temp_msg = await message.reply(f"{sc('wait a sec')}..")
        
        try:
            if custom_chat_id:
                messages = await get_messages(client, ids, custom_chat_id)
            else:
                messages = await get_messages(client, ids)
        except Exception as e:
            await temp_msg.edit_text(f"{sc('something went wrong')}..!")
            client.LOGGER(__name__, client.name).warning(f"Error fetching messages: {e}")
            return

        # Filter out None messages (invalid/deleted)
        valid_messages = [msg for msg in messages if msg and not getattr(msg, 'empty', True)]
        if not valid_messages:
            # Fallback: try main DB channel in case it's an old link
            if custom_chat_id and custom_chat_id != client.db:
                client.LOGGER(__name__, client.name).warning(f"No messages found in {custom_chat_id}, trying main DB")
                try:
                    messages = await get_messages(client, ids, client.db)
                    valid_messages = [msg for msg in messages if msg and not getattr(msg, 'empty', True)]
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"Fallback fetch error: {e}")
            
            if not valid_messages:
                await temp_msg.edit_text(f"{sc('couldnt find the files in database')}.")
                return
        await temp_msg.delete()

        yugen_msgs = []

        for msg in valid_messages:
            caption = (
                client.messages.get('CAPTION', '').format(
                    previouscaption=f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption else f"<blockquote>{msg.document.file_name}</blockquote>"
                )
                if client.messages.get('CAPTION', '') and msg.document
                else (msg.caption.html if msg.caption else "")
            )

            try:
                copied_msg = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    protect_content=client.protect
                )
                yugen_msgs.append(copied_msg)
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to copy message {msg.id}: {e}")

        if yugen_msgs and client.auto_del > 0:
            warning = await client.send_message(
                user_id,
                f"<b>⚠️ {sc('file will be deleted in')} {humanize.naturaldelta(client.auto_del)}.</b>"
            )
            asyncio.create_task(delete_files(yugen_msgs, client, warning, text))
        elif not yugen_msgs:
            # No files were sent – notify user
            await client.send_message(
                user_id,
                f"❌ {sc('failed to send files. please try again later.')}"
            )
        return

    # ---------------- NORMAL /start UI ----------------
    if user_id in client.admins:
        markup = home_buttons_admin()
    else:
        markup = home_buttons()
    
    photo = client.messages.get("START_PHOTO", "")
    if photo:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=client.messages.get('START', 'No Start Msg').format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=markup
        )
    else:
        await client.send_message(
            chat_id=message.chat.id,
            text=client.messages.get('START', 'No Start Message').format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=markup
        )
