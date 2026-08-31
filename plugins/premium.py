# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from helper.font_converter import to_small_caps as sc
from config import OWNER_ID
import re


# ===============================
#  PARSE DURATION HELPER
# ===============================
def parse_duration(duration_str: str):
    """Parse duration string and return (expire_date, readable_text)"""
    from datetime import datetime, timedelta
    
    # If '0' or 'lifetime' -> lifetime
    if duration_str == '0' or duration_str == 'lifetime':
        return None, "Lifetime"
    
    total_seconds = 0
    
    # Pattern: number followed by d (days), h (hours), m (minutes)
    pattern = r'(\d+)([dhm])'
    matches = re.findall(pattern, duration_str)
    
    if not matches:
        # Try parsing as plain number (assume days)
        try:
            days = int(duration_str)
            if days > 0:
                total_seconds = days * 24 * 3600
                return datetime.now() + timedelta(seconds=total_seconds), f"{days} day{'s' if days > 1 else ''}"
            return None, "Lifetime"
        except:
            return None, "Lifetime"
    
    days = 0
    hours = 0
    minutes = 0
    
    for value, unit in matches:
        num = int(value)
        if unit == 'd':
            days += num
        elif unit == 'h':
            hours += num
        elif unit == 'm':
            minutes += num
    
    # Build readable text
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    
    readable = " ".join(parts)
    
    # Calculate total seconds for expiry
    total_seconds = (days * 24 * 3600) + (hours * 3600) + (minutes * 60)
    
    if total_seconds <= 0:
        return None, "Lifetime"
    
    expire_date = datetime.now() + timedelta(seconds=total_seconds)
    return expire_date, readable


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
    
    msg = f"""<blockquote>**💎 {sc('premium membership')}:**</blockquote>

• {sc('which plan do you want to buy')}?

**📜 {sc('pricing')}:**
╭──────────
↻ ₹99 / $1 : 1 {sc('month')}
↻ ₹179 / $2 : 2 {sc('months')}
↻ ₹249 / $3 : 3 {sc('months')} ({sc('most bought')})
↻ ₹399 / $6 : 6 {sc('months')}
↻ ₹699 / $10 : 9 {sc('months')}
↻ ₹999 / $12 : 12 {sc('months')}
╰──────────

**✨ {sc('premium benefits')}:**
• {sc('no ads or verification')}
• {sc('unlimited downloads')}
• {sc('priority support')}
• {sc('early access to new features')}

{sc('contact here for further inquiry')}"""

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
        return await message.reply("❌ You are not authorized to use this command!")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply(
            "❌ Usage:\n"
            "`/addpremium <user_id> <duration>`\n\n"
            "**Examples:**\n"
            "`/addpremium 123456789 30d` - 30 days\n"
            "`/addpremium 123456789 12h` - 12 hours\n"
            "`/addpremium 123456789 45m` - 45 minutes\n"
            "`/addpremium 123456789 0` - Lifetime\n"
            "`/addpremium 123456789 7d12h` - 7 days 12 hours\n"
            "`/addpremium 123456789 2h30m` - 2 hours 30 minutes"
        )

    try:
        target_user_id = int(parts[1])
    except ValueError:
        return await message.reply("❌ Invalid USER ID")

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

    # ----- Admin confirmation message -----
    admin_reply = (
        f"🎉 Premium activated successfully! 🚀\n\n"
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
        admin_reply += f"⏱️ Expiry Time: {exp_time_str} (Kolkata)"
    else:
        admin_reply += "♾️ <b>Lifetime Premium</b>"

    await message.reply(admin_reply, disable_web_page_preview=True)

    # ----- User welcome message -----
    user_reply = (
        f"💎 PREMIUM ACTIVE\n"
        f"🎉 You are now a PREMIUM USER!\n"
        f"⏳ Duration: {duration_text}\n"
    )

    if expire_date:
        kolkata_time = expire_date + timedelta(hours=5, minutes=30)
        exp_date_str = kolkata_time.strftime("%d-%m-%Y")
        exp_time_str = kolkata_time.strftime("%I:%M:%S %p IST")
        user_reply += f"📅 Expiry: {exp_date_str} {exp_time_str} (Kolkata)\n"
    else:
        user_reply += "📅 Expiry: ♾️ Lifetime\n"

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
        return await message.reply("❌ You are not authorized")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("❌ Usage: `/removepremium <user_id>`")

    try:
        target_user_id = int(parts[1])
    except ValueError:
        return await message.reply("❌ Invalid USER ID")

    await client.mongodb.remove_premium(target_user_id)

    await message.reply(f"🗑 Premium removed for `{target_user_id}`")

    try:
        await client.send_message(
            target_user_id,
            "⚠️ **Your Premium Was Removed**\n"
            "Contact admin if this is a mistake."
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
            return await message.reply("❌ Invalid ID")
    else:
        target = message.from_user.id

    is_premium = await client.mongodb.is_premium(target)
    data = await client.mongodb.user_data.find_one({"_id": target})

    if not is_premium:
        return await message.reply(f"❌ `{target}` is NOT premium")

    expire = data.get("premium_expire")

    await message.reply(
        f"💎 **PREMIUM ACTIVE**\n"
        f"👤 `{target}`\n"
        f"⏳ Expiry: `{expire.strftime('%Y-%m-%d %H:%M:%S') if expire else '♾ Lifetime'}`"
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
        return await message.reply("❌ You are NOT premium.")

    expire = data.get("premium_expire")

    await message.reply(
        f"💎 **Your Premium Status**\n"
        f"⏳ Expiry: `{expire.strftime('%Y-%m-%d %H:%M:%S') if expire else '♾ Lifetime'}`"
    )


# ===============================
#  LIST PREMIUM USERS
# ===============================
@Client.on_message(filters.private & filters.command("premiumusers"))
async def premium_users(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply("❌ You are not authorized")

    users = await client.mongodb.get_premium_users()

    if not users:
        return await message.reply("📭 No premium users found")

    now = datetime.now()
    text = f"💎 **PREMIUM USERS ({len(users)})**\n\n"

    for i, uid in enumerate(users, 1):
        data = await client.mongodb.user_data.find_one({"_id": uid})
        exp = data.get("premium_expire")
        if exp:
            left = (exp - now).days
            left_text = f"{left} days left" if left > 0 else "Expired"
        else:
            left_text = "∞ Lifetime"
        text += f"**{i}.** `{uid}` — {left_text}\n"

    await message.reply(text)
