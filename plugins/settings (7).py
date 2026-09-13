# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.pyromod import ListenerTimeout
from pyrogram.enums import ChatMemberStatus
from config import OWNER_ID, URL_SHORTENERS
import humanize
from helper.font_converter import to_small_caps as sc
from helper.helper_func import is_bot_admin
from datetime import datetime, timedelta


# ===============================
#  PARSE DURATION HELPER
# ===============================
def parse_duration(duration_str: str):
    """Parse duration string and return (expire_date, readable_text)"""
    from datetime import datetime, timedelta
    
    # If '0' or 'lifetime' -> lifetime
    if duration_str == '0' or duration_str == 'lifetime':
        return None, "Lifetime"
    
    # Check if it ends with d, h, or m
    if duration_str.endswith('d'):
        try:
            days = int(duration_str[:-1])
            if days > 0:
                expire_date = datetime.now() + timedelta(days=days)
                return expire_date, f"{days} day{'s' if days > 1 else ''}"
        except:
            pass
    
    elif duration_str.endswith('h'):
        try:
            hours = int(duration_str[:-1])
            if hours > 0:
                expire_date = datetime.now() + timedelta(hours=hours)
                return expire_date, f"{hours} hour{'s' if hours > 1 else ''}"
        except:
            pass
    
    elif duration_str.endswith('m'):
        try:
            minutes = int(duration_str[:-1])
            if minutes > 0:
                expire_date = datetime.now() + timedelta(minutes=minutes)
                return expire_date, f"{minutes} minute{'s' if minutes > 1 else ''}"
        except:
            pass
    
    # Try parsing as plain number (assume days)
    try:
        days = int(duration_str)
        if days > 0:
            expire_date = datetime.now() + timedelta(days=days)
            return expire_date, f"{days} day{'s' if days > 1 else ''}"
        return None, "Lifetime"
    except:
        return None, "Lifetime"


@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>{sc(f'Settings of @{client.username}')}:
{sc('Force Sub Channels')}: <code>{len(client.fsub_dict)}</code>
{sc('Auto Delete Timer')}: <code>{client.auto_del}</code>
{sc('Protect Content')}: <code>{"True" if client.protect else "False"}</code>
{sc('Disable Button')}: <code>{"True" if client.disable_btn else "False"}</code>
{sc('Reply Text')}: <code>{client.reply_text if client.reply_text else 'None'}</code>
{sc('Admins')}: <code>{len(client.admins)}</code>
{sc('Start Message')}:
<pre>{client.messages.get('START', 'Empty')}</pre>
{sc('Start Image')}: <code>{bool(client.messages.get('START_PHOTO', ''))}</code>
{sc('Force Sub Message')}:
<pre>{client.messages.get('FSUB', 'Empty')}</pre>
{sc('Force Sub Image')}: <code>{bool(client.messages.get('FSUB_PHOTO', ''))}</code>
{sc('About Message')}:
<pre>{client.messages.get('ABOUT', 'Empty')}</pre>
{sc('Reply Message')}:
<pre>{client.reply_text}</pre></b>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ', 'fsub'), InlineKeyboardButton('ᴀᴅᴍɪɴꜱ', 'admins')],
        [InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del'), InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect')],
        [InlineKeyboardButton('ᴜʀʟ ꜱʜᴏʀᴛᴇɴᴇʀꜱ', 'url_shorteners'), InlineKeyboardButton('ᴘʜᴏᴛᴏꜱ', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛꜱ', 'texts'), InlineKeyboardButton('💳 ᴄʀᴇᴅɪᴛ ꜱʏꜱᴛᴇᴍ', 'credit_system')],
        [InlineKeyboardButton('🗄️ ᴅʙ ᴄʜᴀɴɴᴇʟꜱ', 'db_channels'), InlineKeyboardButton('🔒 ꜱᴇᴄᴜʀɪᴛʏ (Tokens)', 'security_panel')],
        [InlineKeyboardButton('🤖 ᴀᴜᴛᴏ ʙᴀᴛᴄʜ', 'auto_batch_settings'), InlineKeyboardButton('💎 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ', 'premium_users_settings')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return


@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Force Subscription Settings:
Force Subscribe Channel IDs: <code>{ {a for a in client.fsub_dict.keys()} }</code>

Use the appropriate button below to add or remove a force subscription channel based on your needs!</b>
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return


@Client.on_callback_query(filters.regex("^add_fsub$"))
async def add_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    ask_channel_info = await client.ask(query.from_user.id, "<b>Send channel id(negative integer value), request boolean(yes/no/true/false), timers(integer without decimal)(to enable it keep it greator than 0 otherwise the invite link will not have any timer to invalidate it) seperated by a space in the next 60 seconds!\n<blockquote expandable>Eg: <code>-10089479289 yes 5</code>\n\nIt means <code>-10089479289</code> is the force sub channel id, <code>yes</code> means to enable request it means the link will be request link and only after user sends request to the channel bot will work for that user even if you do not accept his request or user is not a member, <code>5</code> means timer in minutes aftetr 5 minutes the invite link will be expired.</blockquote></b>", filters=filters.text, timeout=60)
    try:
        channel_info = ask_channel_info.text.split()
        channel_id, request, timer = channel_info
        channel_id = int(channel_id)
        if channel_id in client.fsub_dict.keys():
            return await ask_channel_info.reply("<b>This channel id already exists in force sub list, remove it to change it's configuration!!</b>")
        val, res = await is_bot_admin(client, channel_id)
        if not val:
            return await ask_channel_info.reply(f"<b>Error: <code>{res}</code></b>")
        if request.lower() in ('true', 'on', 'yes'):
            request = True
        elif request.lower() in ('false', 'off', 'no'):
            request = False
        else:
            raise Exception("Invalid request value or type.")
        if timer.isdigit():
            timer = int(timer)
        else:
            raise Exception("Timer is not a valid integer.")
        chat = await client.get_chat(channel_id)
        name = chat.title
        if timer > 0:
            client.fsub_dict[channel_id] = [name, None, request, timer]
        else:
            chat_link = await client.create_chat_invite_link(channel_id, creates_join_request=request)
            link = chat_link.invite_link
            client.fsub_dict[channel_id] = [name, link, request, timer]
        await fsub(client, query)
        return await ask_channel_info.reply(f"<b>Channel with name: <code>{name.strip()}</code> is added as a force sub channel!!</b>")
    except Exception as e:
        return await ask_channel_info.reply(f"<b>Error: <code>{e}</code></b>")
    

@Client.on_callback_query(filters.regex('^rm_fsub$'))
async def rm_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    ask_channel_info = await client.ask(query.from_user.id, "<b>Send channel id(negative integer value) in the next 60 seconds!</b>", filters=filters.text, timeout=60)
    try:
        channel_id = int(ask_channel_info.text)
        if channel_id not in client.fsub_dict.keys():
            return await ask_channel_info.reply("<b>This channel id is not in force sub list!</b>")
        
        client.fsub_dict.pop(channel_id)
        await fsub(client, query)
        return await ask_channel_info.reply(f"<b>Channel with id: <code>{channel_id}</code> has been removed as a force sub channel!!</b>")
    except Exception as e:
        return await ask_channel_info.reply(f"<b>Error: <code>{e}</code></b>")


@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    channels = await client.mongodb.get_db_channels()
    multi_db_enabled = await client.mongodb.is_multi_db_enabled()
    
    status = f"✅ {sc('enabled')}" if multi_db_enabled else f"❌ {sc('disabled')}"
    
    msg = f"""<b>🗄️ {sc('multi-db channel settings')}:

{sc('system status')}: {status}
{sc('primary main db')}: <code>{client.db.id if hasattr(client.db, 'id') else client.db}</code>
{sc('extra db channels')}:
"""
    if channels:
        for ch in channels:
            msg += f"• <code>{ch}</code>\n"
    else:
        msg += f"• _{sc('none')}_\n"

    msg += f"\n{sc('add extra channels to store files in multiple places')}!</b>"
    
    toggle_text = f"🔴 {sc('disable multi-db')}" if multi_db_enabled else f"🟢 {sc('enable multi-db')}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, 'toggle_multi_db')],
        [InlineKeyboardButton(f'➕ {sc("add db")}', 'add_db_channel'), InlineKeyboardButton(f'➖ {sc("remove db")}', 'rm_db_channel')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^add_db_channel$"))
async def add_db_channel_cb(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return

    await query.message.edit_text(
        "<b>➕ Add DB Channel</b>\n\n"
        "<b>Forward a message from the channel OR send the Channel ID.\n"
        "Make sure the bot is ADMIN in that channel!\n\n"
        "Timeout: 60s</b>"
    )

    try:
        res = await client.listen(
            user_id=query.from_user.id,
            filters=filters.text | filters.forwarded,
            timeout=60
        )
    except ListenerTimeout:
        return await query.message.edit_text(
            "<b>⌚ Timeout!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
        )

    # Extract channel ID - FIXED for older Pyrogram version
    channel_id = None
    if res.forward_from_chat:  # Changed from forward_origin
        channel_id = res.forward_from_chat.id
    elif res.text:
        try:
            channel_id = int(res.text.strip())
        except ValueError:
            pass

    if not channel_id:
        return await query.message.edit_text(
            "<b>❌ Invalid Channel ID!\n"
            "Make sure you forwarded a message from the channel or sent a valid numeric ID.</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
        )

    # Verify the bot is an admin in the channel
    try:
        chat = await client.get_chat(channel_id)
        bot_member = await chat.get_member("me")
        if bot_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return await query.message.edit_text(
                f"<b>❌ Bot is not an admin in {chat.title}\n"
                f"Please add the bot as an administrator and try again.</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
            )
    except Exception as e:
        error_msg = str(e)
        if "CHANNEL_INVALID" in error_msg or "PEER_ID_INVALID" in error_msg:
            return await query.message.edit_text(
                "<b>❌ Channel not found!\n"
                "Make sure the bot is added to the channel and the ID is correct.</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
            )
        else:
            return await query.message.edit_text(
                f"<b>❌ Error accessing channel:\n<code>{error_msg}</code></b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
            )

    # Add to database
    try:
        await client.mongodb.add_db_channel(channel_id)
        await query.message.edit_text(
            f"<b>✅ Channel added successfully!\n"
            f"ID: <code>{channel_id}</code>\n"
            f"Name: {chat.title}</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
        )
    except Exception as e:
        await query.message.edit_text(
            f"<b>❌ Database error:\n<code>{e}</code></b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'db_channels')]])
        )


@Client.on_callback_query(filters.regex("^rm_db_channel$"))
async def rm_db_channel_cb(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>➖ Remove DB Channel:
    
Send the Channel ID to remove.

Timeout: 60s</b>
"""
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        try:
             channel_id = int(res.text.strip())
        except:
             return await query.message.edit_text("<b>❌ Invalid ID!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

        await client.mongodb.remove_db_channel(channel_id)
        await query.message.edit_text(f"<b>✅ Channel <code>{channel_id}</code> removed!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

    except ListenerTimeout:
        await query.message.edit_text("<b>⌚ Timeout!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))


@Client.on_callback_query(filters.regex("^toggle_multi_db$"))
async def toggle_multi_db_cb(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    new_status = await client.mongodb.toggle_multi_db()
    status_text = sc('enabled') if new_status else sc('disabled')
    await query.answer(f"✅ {sc('multi-db system')} {status_text}!", show_alert=True)
    return await db_channels(client, query)


@Client.on_callback_query(filters.regex("^premium_users_settings$"))
async def premium_users_settings(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    users = await client.mongodb.get_premium_users()
    
    msg = f"""<b>💎 {sc('premium users management')}:

{sc('total premium users')}: <code>{len(users)}</code>

"""
    
    if users:
        from datetime import datetime
        now = datetime.now()
        
        msg += f"{sc('active premium users')}:\n"
        for i, uid in enumerate(users[:10], 1):
            data = await client.mongodb.user_data.find_one({"_id": uid})
            exp = data.get("premium_expire") if data else None
            
            if exp:
                left = (exp - now).days
                status = f"{left} {sc('days left')}" if left > 0 else sc('expired')
            else:
                status = "∞ " + sc('lifetime')
            
            msg += f"{i}. <code>{uid}</code> — {status}\n"
        
        if len(users) > 10:
            msg += f"\n+{len(users) - 10} {sc('more users')}"
    else:
        msg += f"_{sc('no premium users found')}_"
    
    msg += f"\n\n{sc('use buttons below to manage premium users')}</b>"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'➕ {sc("add premium")}', 'add_premium_user'), InlineKeyboardButton(f'➖ {sc("remove premium")}', 'remove_premium_user')],
        [InlineKeyboardButton(f'📋 {sc("view all")}', 'view_all_premium')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'settings')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^view_all_premium$"))
async def view_all_premium(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    users = await client.mongodb.get_premium_users()
    
    if not users:
        await query.answer(f"📭 {sc('no premium users found')}", show_alert=True)
        return
    
    from datetime import datetime
    now = datetime.now()
    
    msg = f"""<b>💎 {sc('all premium users')} ({len(users)}):

"""
    
    for i, uid in enumerate(users, 1):
        data = await client.mongodb.user_data.find_one({"_id": uid})
        exp = data.get("premium_expire") if data else None
        
        if exp:
            left = (exp - now).days
            status = f"{left}d" if left > 0 else sc('exp')
        else:
            status = "∞"
        
        msg += f"{i}. <code>{uid}</code> — {status}\n"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]
    ])
    
    await query.message.edit_text(msg + "</b>", reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^add_premium_user$"))
async def add_premium_user_cb(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return

    msg = f"""<b>➕ {sc('add premium user')}:

{sc('send user id and duration')}

{sc('format')}: user_id duration
{sc('examples')}:
123456789 30d - 30 {sc('days')}
123456789 12h - 12 {sc('hours')}
123456789 45m - 45 {sc('minutes')}
123456789 0 - {sc('lifetime')}

{sc('timeout')}: 60s</b>"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("cancel")}', 'premium_users_settings')]]))

    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        parts = res.text.strip().split()
        if len(parts) < 2:
            await query.message.edit_text(f"<b>❌ {sc('invalid format')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))
            return

        try:
            user_id = int(parts[0])
        except ValueError:
            await query.message.edit_text(f"<b>❌ {sc('invalid user id')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))
            return

        duration_str = parts[1].lower()
        
        # Fetch user info for mention
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except Exception:
            user_mention = f"<a href='tg://user?id={user_id}'>{user_id}</a>"

        # Parse duration
        expire_date, duration_text = parse_duration(duration_str)
        
        await client.mongodb.add_premium(user_id, expire_date)

        # Admin confirmation (ALL BOLD)
        admin_reply = (
            f"<b>🎉 Premium activated successfully! 🚀\n\n"
            f"👤 User: {user_mention}\n"
            f"⚡ User ID: <code>{user_id}</code>\n"
            f"⏳ Premium Access Duration: {duration_text}\n"
        )
        if expire_date:
            kolkata_time = expire_date + timedelta(hours=5, minutes=30)
            exp_date_str = kolkata_time.strftime("%d-%m-%Y")
            exp_time_str = kolkata_time.strftime("%I:%M:%S %p IST")
            admin_reply += f"⌛️ Expiry Date: {exp_date_str}\n"
            admin_reply += f"⏱️ Expiry Time: {exp_time_str} (Kolkata)</b>"
        else:
            admin_reply += "♾️ <b>Lifetime Premium</b>"

        await query.message.edit_text(
            admin_reply,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]),
            disable_web_page_preview=True
        )

        # User welcome message (ALL BOLD)
        user_reply = (
            f"<b>💎 PREMIUM ACTIVE\n"
            f"🎉 You are now a PREMIUM USER!\n"
            f"⏳ Duration: {duration_text}\n"
        )
        if expire_date:
            kolkata_time = expire_date + timedelta(hours=5, minutes=30)
            exp_date_str = kolkata_time.strftime("%d-%m-%Y")
            exp_time_str = kolkata_time.strftime("%I:%M:%S %p IST")
            user_reply += f"📅 Expiry: {exp_date_str} {exp_time_str} (Kolkata)</b>"
        else:
            user_reply += "📅 Expiry: ♾️ Lifetime</b>"

        try:
            await client.send_message(user_id, user_reply)
        except:
            pass

    except ListenerTimeout:
        await query.message.edit_text(f"<b>⌚ {sc('timeout')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))


@Client.on_callback_query(filters.regex("^remove_premium_user$"))
async def remove_premium_user_cb(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>➖ {sc('remove premium user')}:

{sc('send user id to remove premium')}

{sc('format')}: user_id
{sc('example')}: 123456789

{sc('timeout')}: 60s</b>
"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("cancel")}', 'premium_users_settings')]]))

    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        
        try:
            user_id = int(res.text.strip())
        except:
            await query.message.edit_text(f"<b>❌ {sc('invalid user id')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))
            return
        
        await client.mongodb.remove_premium(user_id)
        
        await query.message.edit_text(
            f"<b>✅ {sc('premium removed')}!\n\n"
            f"{sc('user id')}: <code>{user_id}</code></b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]])
        )
        
        try:
            await client.send_message(
                user_id,
                f"<b>⚠️ {sc('your premium was removed')}</b>"
            )
        except:
            pass
            
    except ListenerTimeout:
        await query.message.edit_text(f"<b>⌚ {sc('timeout')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))


@Client.on_callback_query(filters.regex("^auto_batch_settings$"))
async def auto_batch_settings(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    enabled = await client.mongodb.get_bot_config('auto_batch_enabled', False)
    mode = await client.mongodb.get_bot_config('auto_batch_mode', 'episode')
    window = await client.mongodb.get_bot_config('auto_batch_time_window', 30)

    status = f"✅ {sc('Enabled')}" if enabled else f"❌ {sc('Disabled')}"
    mode_text = "📺 Episodes (S01 E01)" if mode == 'episode' else "🎬 Series/Movie (Name [Quality])"
    
    msg = f"""<b>🤖 {sc('Auto-Batch Settings')}:
Status: {status}
Mode: <code>{mode_text}</code>
Time Window: <code>{window}s</code>

{sc('Automatically groups files sent to the channel into batches.')}
{sc('Turning this OFF will stop those annoying messages!')}</b>
"""
    toggle_text = f"🔴 {sc('Disable')}" if enabled else f"🟢 {sc('Enable')}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, 'toggle_auto_batch')],
        [InlineKeyboardButton(f'🔄 {sc("switch mode")}', 'toggle_batch_mode')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^toggle_auto_batch$"))
async def toggle_auto_batch(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    current = await client.mongodb.get_bot_config('auto_batch_enabled', False)
    await client.mongodb.set_bot_config('auto_batch_enabled', not current)
    await query.answer(f"Auto-Batch {'Disabled' if current else 'Enabled'}!")
    return await auto_batch_settings(client, query)


@Client.on_callback_query(filters.regex("^toggle_batch_mode$"))
async def toggle_batch_mode(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    current = await client.mongodb.get_bot_config('auto_batch_mode', 'episode')
    new_mode = 'season' if current == 'episode' else 'episode'
    await client.mongodb.set_bot_config('auto_batch_mode', new_mode)
    await query.answer(f"Switched to {new_mode.title()} Mode!")
    return await auto_batch_settings(client, query)


@Client.on_callback_query(filters.regex("^admins$"))
async def admins(client, query):
    if not (query.from_user.id == OWNER_ID):
        return await query.answer('Only the owner can access this!', show_alert=True)
    msg = f"""<b>Admin Settings:
Admin User IDs: {", ".join(f"<code>{a}</code>" for a in client.admins)}

Use the appropriate button below to add or remove an admin based on your needs!</b>
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return


@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_new_admins(client, query):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    ids_msg = await client.ask(query.from_user.id, "<b>Send user ids seperated by a space in the next 60 seconds!\nEg: <code>838278682 83622928 82789928</code></b>", filters=filters.text, timeout=60)
    ids = ids_msg.text.split()
    
    try:
        for identifier in ids:
            if int(identifier) not in client.admins:
                client.admins.append(int(identifier))
            
    except Exception as e:
        return await ids_msg.reply(f"<b>Error: <code>{e}</code></b>")
    await admins(client, query)
    return await ids_msg.reply(f"<b>{len(ids)} admin {'id' if len(ids)==1 else 'ids'} have been promoted!!</b>")
    

@Client.on_callback_query(filters.regex("^rm_admin$"))
async def remove_admins(client, query):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    ids_msg = await client.ask(query.from_user.id, "<b>Send user ids seperated by a space in the next 60 seconds!\nEg: <code>838278682 83622928 82789928</code></b>", filters=filters.text, timeout=60)
    ids = ids_msg.text.split()
    
    try:
        for identifier in ids:
            if int(identifier) == client.owner:
                await client.send_message(query.from_user.id, "<b>Nigga i can never remove the owner from the admin list!!</b>")
                continue
            if int(identifier) in client.admins:
                client.admins.remove(int(identifier))
    except Exception as e:
        return await ids_msg.reply(f"<b>Error: <code>{e}</code></b>")
    await admins(client, query)
    return await ids_msg.reply(f"<b>{len(ids)} admin {'id' if len(ids)==1 else 'ids'} have been removed!!</b>")


@Client.on_callback_query(filters.regex("^photos$"))
async def photos(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Force Subscription Settings:
Start Photo: <code>{client.messages.get("START_PHOTO", "None")}</code>
Force Sub Photo: <code>{client.messages.get('FSUB_PHOTO', 'None')}</code>

Use the appropriate button below to add or remove any admin based on your needs!</b>
"""
    reply_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if client.messages.get("START_PHOTO", "") == "" else 'ᴄʜᴀɴɢᴇ') + '\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', 
            callback_data='add_start_photo'
        ),
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if client.messages.get("FSUB_PHOTO", "") == "" else 'ᴄʜᴀɴɢᴇ') + '\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', 
            callback_data='add_fsub_photo'
        )
    ],
    [
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', callback_data='rm_start_photo'),
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', callback_data='rm_fsub_photo')
    ],
    [InlineKeyboardButton('◂ ʙᴀᴄᴋ', callback_data='settings')]

    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return


@Client.on_callback_query(filters.regex("^protect$"))
async def protect(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    client.protect = False if client.protect else True
    return await settings(client, query)


@Client.on_callback_query(filters.regex("^url_shorteners$"))
async def url_shorteners(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>URL Shortener Settings:
Configured Providers: <code>{len(URL_SHORTENERS)}</code>
Active Providers: <code>{len([k for k, v in URL_SHORTENERS.items() if v.get('active', False)])}</code>

"""
    token_verification_enabled = await client.mongodb.get_bot_config('token_verification_enabled', True)
    system_status = "✅ Enabled" if token_verification_enabled else "❌ Disabled"
    msg += f"Global Verification System: {system_status}\n\n"

    for key, provider in URL_SHORTENERS.items():
        status = "✅ Active" if provider.get('active', False) else "❌ Inactive"
        msg += f"{provider['name']}: {status}\n"
        msg += f"  • API URL: <code>{provider['api_url']}</code>\n"
        msg += f"  • Token: <code>{provider.get('api_token', 'Not set')[:10]}...</code>\n\n"

    toggle_btn_text = "🔴 Disable System" if token_verification_enabled else "🟢 Enable System"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_btn_text, 'global_token_toggle')],
        [InlineKeyboardButton('⚠️ ᴀɴᴛɪ-ʙʏᴘᴀꜱꜱ ꜱᴇᴛᴛɪɴɢꜱ', 'anti_bypass_settings')],
        [InlineKeyboardButton('ᴀᴅᴅ ᴘʀᴏᴠɪᴅᴇʀ', 'add_shortener'), InlineKeyboardButton('ᴇᴅɪᴛ ᴘʀᴏᴠɪᴅᴇʀ', 'edit_shortener')],
        [InlineKeyboardButton('ᴛᴏɢɢʟᴇ ᴘʀᴏᴠɪᴅᴇʀ', 'toggle_shortener'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴘʀᴏᴠɪᴅᴇʀ', 'rm_shortener')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg + "</b>", reply_markup=reply_markup)
    return


@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Change Auto Delete Time:
Current Timer: <code>{client.auto_del}</code>

Enter new integer value of auto delete timer, keep 0 to disable auto delete and -1 to as it was, or wait for 60 second timeout to be comoleted!</b>
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        timer = res.text.strip()
        if timer.isdigit() or (timer.startswith('+' or '-') and timer[1:].isdigit()):
            timer = int(timer)
            if timer >= 0:
                client.auto_del = timer
                await client.mongodb.set_bot_config('auto_del', timer)
                return await query.message.edit_text(f'<b>Auto Delete timer value changed to {timer} seconds!</b>', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
            else:
                return await query.message.edit_text("<b>There is no change done in auto delete timer!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
        else:
            return await query.message.edit_text("<b>This is not an integer value!!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))


@Client.on_callback_query(filters.regex("^texts$"))
async def texts(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Text Configuration:
Start Message:
<pre>{client.messages.get('START', 'Empty')}</pre>
Force Sub Message:
<pre>{client.messages.get('FSUB', 'Empty')}</pre>
About Message:
<pre>{client.messages.get('ABOUT', 'Empty')}</pre>
Reply Message:
<pre>{client.reply_text}</pre></b>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'ꜱᴛᴀʀᴛ ᴛᴇxᴛ', 'start_txt'), InlineKeyboardButton(f'ꜰꜱᴜʙ ᴛᴇxᴛ', 'fsub_txt')],
        [InlineKeyboardButton('ʀᴇᴘʟʏ ᴛᴇxᴛ', 'reply_txt'), InlineKeyboardButton('ᴀʙᴏᴜᴛ ᴛᴇxᴛ', 'about_txt')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return


@Client.on_callback_query(filters.regex('^rm_start_photo$'))
async def rm_start_photo(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    client.messages['START_PHOTO'] = ''
    await query.answer()
    await photos(client, query)


@Client.on_callback_query(filters.regex('^rm_fsub_photo$'))
async def rm_fsub_photo(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    client.messages['FSUB_PHOTO'] = ''
    await query.answer()
    await photos(client, query)


@Client.on_callback_query(filters.regex("^add_start_photo$"))
async def add_start_photo(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Change Start Image:
Current Start Image: <code>{client.messages.get('START_PHOTO', '')}</code>

Enter new link of start image or send the photo, or wait for 60 second timeout to be comoleted!</b>
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=(filters.text|filters.photo), timeout=60)
        if res.text and res.text.startswith('https://' or 'http://'):
            client.messages['START_PHOTO'] = res.text
            return await query.message.edit_text("<b>This link has been set at the place of start photo!!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        elif res.photo:
            loc = await res.download()
            client.messages['START_PHOTO'] = loc
            return await query.message.edit_text("<b>This image has been set as the starting image!!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        else:
            return await query.message.edit_text("<b>Invalid Photo or Link format!!\nIf you're sending the link of any image it must starts with either 'http' or 'https'!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))


@Client.on_callback_query(filters.regex("^add_fsub_photo$"))
async def add_fsub_photo(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Change Force Sub Image:
Current Force Sub Image: <code>{client.messages.get('FSUB_PHOTO', '')}</code>

Enter new link of fsub image or send the photo, or wait for 60 second timeout to be comoleted!</b>
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=(filters.text|filters.photo), timeout=60)
        if res.text and res.text.startswith('https://' or 'http://'):
            client.messages['FSUB_PHOTO'] = res.text
            return await query.message.edit_text("<b>This link has been set at the place of fsub photo!!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        elif res.photo:
            loc = await res.download()
            client.messages['FSUB_PHOTO'] = loc
            return await query.message.edit_text("<b>This image has been set as the force sub image!!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        else:
            return await query.message.edit_text("<b>Invalid Photo or Link format!!\nIf you're sending the link of any image it must starts with either 'http' or 'https'!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))


@Client.on_callback_query(filters.regex("^add_shortener$"))
async def add_shortener(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>Add New URL Shortener Provider:

Send the provider details in this format:

Supported Formats:
• text - Returns plain text URL
• json - Returns JSON response

Send the details or wait for 60 second timeout to be completed!</b>
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        details = res.text.strip().split('|')
        
        if len(details) != 5:
            return await query.message.edit_text("<b>Invalid format! Please use: provider_key|Name|API_URL|Token|Format</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider_key, name, api_url, api_token, format_type = details
        
        if provider_key in URL_SHORTENERS:
            return await query.message.edit_text(f"<b>Provider '{provider_key}' already exists!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        URL_SHORTENERS[provider_key] = {
            'name': name,
            'api_url': api_url,
            'api_token': api_token,
            'format': format_type,
            'active': True
        }
        
        return await query.message.edit_text(f"<b>✅ Provider '{name}' added successfully!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^edit_shortener$"))
async def edit_shortener(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    if not URL_SHORTENERS:
        return await query.answer("No providers configured!")
    
    msg = f"""<b>Edit URL Shortener Provider:

Available Providers:
"""
    for key, provider in URL_SHORTENERS.items():
        status = "✅" if provider.get('active', False) else "❌"
        msg += f"{status} <code>{key}</code> - {provider['name']}\n"
    
    msg += f"\nSend the provider key to edit or wait for 60 second timeout to be completed!</b>"
    
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        provider_key = res.text.strip()
        
        if provider_key not in URL_SHORTENERS:
            return await query.message.edit_text(f"<b>Provider '{provider_key}' not found!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider = URL_SHORTENERS[provider_key]
        msg = f"""<b>Edit Provider: {provider['name']}

Current Settings:
• Name: <code>{provider['name']}</code>
• API URL: <code>{provider['api_url']}</code>
• Token: <code>{provider.get('api_token', 'Not set')[:15]}...</code>
• Format: <code>{provider.get('format', 'text')}</code>
• Active: {"Yes" if provider.get('active', False) else "No"}

Send new details in format:

Example:</b>
"""
        await query.message.edit_text(msg)
        try:
            res2 = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
            details = res2.text.strip().split('|')
            
            if len(details) != 5:
                return await query.message.edit_text("<b>Invalid format! Use: Name|API_URL|Token|Format|Active(1/0)</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
            
            name, api_url, api_token, format_type, active = details
            
            URL_SHORTENERS[provider_key] = {
                'name': name,
                'api_url': api_url,
                'api_token': api_token,
                'format': format_type,
                'active': active == '1'
            }
            
            return await query.message.edit_text(f"<b>✅ Provider '{name}' updated successfully!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
            
        except ListenerTimeout:
            return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^toggle_shortener$"))
async def toggle_shortener(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    if not URL_SHORTENERS:
        return await query.answer("No providers configured!")
    
    msg = f"""<b>Toggle URL Shortener Active Status:

Available Providers:
"""
    for key, provider in URL_SHORTENERS.items():
        status = "✅ Active" if provider.get('active', False) else "❌ Inactive"
        msg += f"• <code>{key}</code> - {provider['name']} ({status})\n"
    
    msg += f"\nSend the provider key to toggle or wait for 60 second timeout to be completed!</b>"
    
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        provider_key = res.text.strip()
        
        if provider_key not in URL_SHORTENERS:
            return await query.message.edit_text(f"<b>Provider '{provider_key}' not found!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider = URL_SHORTENERS[provider_key]
        current_status = provider.get('active', False)
        provider['active'] = not current_status
        
        status_text = "activated" if provider['active'] else "deactivated"
        return await query.message.edit_text(f"<b>✅ Provider '{provider['name']}' {status_text} successfully!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^rm_shortener$"))
async def rm_shortener(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    if not URL_SHORTENERS:
        return await query.answer("No providers configured!")
    
    msg = f"""<b>Remove URL Shortener Provider:

Available Providers:
"""
    for key, provider in URL_SHORTENERS.items():
        status = "✅ Active" if provider.get('active', False) else "❌ Inactive"
        msg += f"• <code>{key}</code> - {provider['name']} ({status})\n"
    
    msg += f"\nSend the provider key to remove or wait for 60 second timeout to be completed!\n"
    msg += f"⚠️ Warning: This action cannot be undone!</b>"
    
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        provider_key = res.text.strip()
        
        if provider_key not in URL_SHORTENERS:
            return await query.message.edit_text(f"<b>Provider '{provider_key}' not found!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider_name = URL_SHORTENERS[provider_key]['name']
        del URL_SHORTENERS[provider_key]
        
        return await query.message.edit_text(f"<b>✅ Provider '{provider_name}' removed successfully!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("<b>Timeout, try again!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^global_token_toggle$"))
async def global_token_toggle(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    current_status = await client.mongodb.get_bot_config('token_verification_enabled', True)
    new_status = not current_status
    await client.mongodb.set_bot_config('token_verification_enabled', new_status)
    await query.answer(f"System {'Enabled' if new_status else 'Disabled'}!")
    return await url_shorteners(client, query)


@Client.on_callback_query(filters.regex("^anti_bypass_settings$"))
async def anti_bypass_settings(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    bypass_check_enabled = await client.mongodb.get_bot_config('bypass_check_enabled', True)
    bypass_timer = await client.mongodb.get_bot_config('bypass_timer', 60)
    
    status = f"✅ {sc('Enabled')}" if bypass_check_enabled else f"❌ {sc('Disabled')}"
    
    msg = f"""<b>⚠️ {sc('Anti-Bypass System Configuration')}:

{sc('System Status')}: {status}
{sc('Minimum Wait Time')}: <code>{bypass_timer} {sc('seconds')}</code>

{sc('This system prevents users from solving the shortener too quickly (skipping ads)')}.</b>
"""
    toggle_text = f"🔴 {sc('Disable')}" if bypass_check_enabled else f"🟢 {sc('Enable')}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, 'toggle_bypass_check'), InlineKeyboardButton(f'⏰ {sc("change timer")}', 'set_bypass_timer')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'url_shorteners')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^toggle_bypass_check$"))
async def toggle_bypass_check(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    current = await client.mongodb.get_bot_config('bypass_check_enabled', True)
    await client.mongodb.set_bot_config('bypass_check_enabled', not current)
    await query.answer(f"{sc('Anti-Bypass System')} {'Disabled' if current else 'Enabled'}!")
    return await anti_bypass_settings(client, query)


@Client.on_callback_query(filters.regex("^set_bypass_timer$"))
async def set_bypass_timer(client, query):
    if query.from_user.id not in client.admins:
        await query.answer("Only Admins Can Access This", show_alert=True)
        return
    msg = f"""<b>{sc('change anti-bypass timer')}:
    
{sc('enter the minimum time (in seconds) a user must take to solve the shortener')}.
{sc('default is 60 seconds')}.

{sc('send the number or wait for timeout')}!</b>
"""
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        if res.text.isdigit():
            timer = int(res.text)
            await client.mongodb.set_bot_config('bypass_timer', timer)
            await query.message.edit_text(f"<b>{sc('timer updated to')} {timer} {sc('seconds')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'anti_bypass_settings')]]))
        else:
            await query.message.edit_text(f"<b>{sc('invalid number')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'anti_bypass_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text(f"<b>{sc('timeout')}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'anti_bypass_settings')]]))
