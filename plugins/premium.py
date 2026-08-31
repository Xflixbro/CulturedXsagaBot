# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from helper.font_converter import to_small_caps as sc
from config import OWNER_ID


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


# ===============================
#  PREMIUM PRICING PANEL
# ===============================
@Client.on_message(filters.private & filters.command("premium"))
async def premium_command(client: Client, message: Message):
    """Show premium plans"""
    await show_premium_panel(client, message)


@Client.on_callback_query(filters.regex("^premium_panel$"))
async def premium_panel_callback(client: Client, query: CallbackQuery):
    """Show premium panel from callback"""
    await show_premium_panel(client, query.message, is_edit=True)


async def show_premium_panel(client: Client, message: Message, is_edit: bool = False):
    """Display premium pricing panel"""
    
    msg = f"""<b>💎 {sc('premium membership')}:

• {sc('which plan do you want to buy')}?

📜 {sc('pricing')}:
╭──────────
↻ ₹99 / $1 : 1 {sc('month')}
↻ ₹179 / $2 : 2 {sc('months')}
↻ ₹249 / $3 : 3 {sc('months')} ({sc('most bought')})
↻ ₹399 / $6 : 6 {sc('months')}
↻ ₹699 / $10 : 9 {sc('months')}
↻ ₹999 / $12 : 12 {sc('months')}
╰──────────

✨ {sc('premium benefits')}:
• {sc('no ads or verification')}
• {sc('unlimited downloads')}
• {sc('priority support')}
• {sc('early access to new features')}

{sc('contact here for further inquiry')}</b>"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💬 {sc('send hi/hello in chat')}", url=f"tg://user?id={OWNER_ID}")],
        [InlineKeyboardButton(f"🔙 {sc('back')}", callback_data="home")]
    ])
    
    if is_edit:
        await message.edit_text(msg, reply_markup=buttons)
    else:
        await message.reply(msg, reply_markup=buttons)


# ===============================
#  ADD PREMIUM (COMMAND)
# ===============================
@Client.on_message(filters.private & filters.command("addpremium"))
async def add_premium_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply("<b>❌ You are not authorized to use this command!</b>")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply(
            "<b>❌ Usage:\n"
            "/addpremium <user_id> <duration>\n\n"
            "Examples:\n"
            "/addpremium 123456789 30d - 30 days\n"
            "/addpremium 123456789 12h - 12 hours\n"
            "/addpremium 123456789 45m - 45 minutes\n"
            "/addpremium 123456789 0 - Lifetime</b>"
        )

    try:
        target_user_id = int(parts[1])
    except ValueError:
        return await message.reply("<b>❌ Invalid USER ID</b>")

    # Fetch user info for mention
    try:
        user = await client.get_users(target_user_id)
        user_mention = user.mention
    except Exception:
        user_mention = f"<a href='tg://user?id={target_user_id}'>{target_user_id}</a>"

    # Parse duration
    if len(parts) >= 3:
        duration_str = parts[2].lower()
        expire_date, duration_text = parse_duration(duration_str)
    else:
        expire_date = None
        duration_text = "Lifetime"

    # Save to DB
    await client.mongodb.add_premium(target_user_id, expire_date)

    # ----- Admin confirmation message (ALL BOLD) -----
    admin_reply = (
        f"<b>🎉 Premium activated successfully! 🚀\n\n"
        f"👤 User: {user_mention}\n"
        f"⚡ User ID: <code>{target_user_id}</code>\n"
        f"⏳ Premium Access Duration: {duration_text}\n"
    )

    if expire_date:
        # Convert to Kolkata Time (IST - UTC+5:30)
        kolkata_time = expire_date + timedelta(hours=5, minutes=30)
        exp_date_str = kolkata_time.strftime("%d-%m-%Y")
        exp_time_str = kolkata_time.strftime("%I:%M:%S %p IST")
        admin_reply += f"⌛️ Expiry Date: {exp_date_str}\n"
        admin_reply += f"⏱️ Expiry Time: {exp_time_str} (Kolkata)</b>"
    else:
        admin_reply += "♾️ <b>Lifetime Premium</b>"

    await message.reply(admin_reply, disable_web_page_preview=True)

    # ----- User welcome message (ALL BOLD) -----
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
        await client.send_message(target_user_id, user_reply)
    except Exception:
        pass


# ===============================
#  REMOVE PREMIUM
# ===============================
@Client.on_message(filters.private & filters.command("removepremium"))
async def remove_premium_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply("<b>❌ You are not authorized</b>")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("<b>❌ Usage: /removepremium <user_id></b>")

    try:
        target_user_id = int(parts[1])
    except ValueError:
        return await message.reply("<b>❌ Invalid USER ID</b>")

    await client.mongodb.remove_premium(target_user_id)

    await message.reply(f"<b>🗑 Premium removed for <code>{target_user_id}</code></b>")

    try:
        await client.send_message(
            target_user_id,
            "<b>⚠️ Your Premium Was Removed\n"
            "Contact admin if this is a mistake.</b>"
        )
    except:
        pass


# ===============================
#  CHECK ANY USER
# ===============================
@Client.on_message(filters.private & filters.command("checkpremium"))
async def check_premium(client: Client, message: Message):
    parts = message.text.split()

    if message.from_user.id in client.admins and len(parts) >= 2:
        try:
            target = int(parts[1])
        except ValueError:
            return await message.reply("<b>❌ Invalid ID</b>")
    else:
        target = message.from_user.id

    is_premium = await client.mongodb.is_premium(target)
    data = await client.mongodb.user_data.find_one({"_id": target})

    if not is_premium:
        return await message.reply(f"<b>❌ <code>{target}</code> is NOT premium</b>")

    expire = data.get("premium_expire")

    await message.reply(
        f"<b>💎 PREMIUM ACTIVE\n"
        f"👤 <code>{target}</code>\n"
        f"⏳ Expiry: <code>{expire.strftime('%Y-%m-%d %H:%M:%S') if expire else '♾ Lifetime'}</code></b>"
    )


# ===============================
#  CHECK SELF
# ===============================
@Client.on_message(filters.private & filters.command("mypremium"))
async def my_premium(client: Client, message: Message):
    uid = message.from_user.id

    is_premium = await client.mongodb.is_premium(uid)
    data = await client.mongodb.user_data.find_one({"_id": uid})

    if not is_premium:
        return await message.reply("<b>❌ You are NOT premium.</b>")

    expire = data.get("premium_expire")

    await message.reply(
        f"<b>💎 Your Premium Status\n"
        f"⏳ Expiry: <code>{expire.strftime('%Y-%m-%d %H:%M:%S') if expire else '♾ Lifetime'}</code></b>"
    )


# ===============================
#  LIST PREMIUM USERS
# ===============================
@Client.on_message(filters.private & filters.command("premiumusers"))
async def premium_users(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply("<b>❌ You are not authorized</b>")

    users = await client.mongodb.get_premium_users()

    if not users:
        return await message.reply("<b>📭 No premium users found</b>")

    now = datetime.now()
    text = f"<b>💎 PREMIUM USERS ({len(users)})\n\n"

    for i, uid in enumerate(users, 1):
        data = await client.mongodb.user_data.find_one({"_id": uid})
        exp = data.get("premium_expire")
        if exp:
            left = (exp - now).days
            left_text = f"{left} days left" if left > 0 else "Expired"
        else:
            left_text = "∞ Lifetime"
        text += f"{i}. <code>{uid}</code> — {left_text}\n"

    await message.reply(text + "</b>")
