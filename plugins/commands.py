# commands.py – Handlers for /stats and /settings

import humanize
import psutil
import shutil
from datetime import datetime
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot  # if you use Bot class, otherwise use Client
from helper.font_converter import to_small_caps as sc

# ------------------- /stats command -------------------
@Bot.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Bot, message: Message):
    """Show bot statistics (admin only)"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    wait_msg = await message.reply("⏳ Gathering stats...")

    try:
        # Get counts from MongoDB
        total_users = await client.mongodb.user_data.count_documents({})
        total_files = await client.mongodb.file_tokens.count_documents({})
        total_batches = await client.mongodb.batch_groups.count_documents({})
        total_channels = await client.mongodb.total_channels()

        # System uptime
        uptime_seconds = (datetime.now() - client.uptime).total_seconds()
        uptime_str = humanize.precisedelta(uptime_seconds)

        # Disk usage
        total, used, free = shutil.disk_usage("/")
        disk_total = total / (1024**3)
        disk_used = used / (1024**3)
        disk_free = free / (1024**3)

        # RAM usage
        ram = psutil.virtual_memory()
        ram_used = ram.used / (1024**3)
        ram_total = ram.total / (1024**3)

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        msg = (
            f"<blockquote><b>📊 {sc('bot statistics')}</b></blockquote>\n\n"
            f"**👥 Users:** `{total_users}`\n"
            f"**📁 Files:** `{total_files}`\n"
            f"**📦 Batches:** `{total_batches}`\n"
            f"**📢 Channels:** `{total_channels}`\n"
            f"**⏱️ Uptime:** `{uptime_str}`\n\n"
            f"**💾 Disk:** {disk_used:.2f}GB / {disk_total:.2f}GB ({disk_free:.2f}GB free)\n"
            f"**🧠 RAM:** {ram_used:.2f}GB / {ram_total:.2f}GB ({ram.percent}%)\n"
            f"**⚙️ CPU:** {cpu_percent}%\n"
        )

        await wait_msg.edit_text(msg)

    except Exception as e:
        await wait_msg.edit_text(f"❌ Error: {e}")


# ------------------- /settings command -------------------
@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):
    """Open the settings panel (admin only)"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    # This is the same settings panel from settings.py
    msg = f"""<blockquote>**{sc(f'Settings of @{client.username}')}:**</blockquote>
**{sc('Force Sub Channels')}:** `{len(client.fsub_dict)}`
**{sc('Auto Delete Timer')}:** `{client.auto_del}`
**{sc('Protect Content')}:** `{"True" if client.protect else "False"}`
**{sc('Disable Button')}:** `{"True" if client.disable_btn else "False"}`
**{sc('Reply Text')}:** `{client.reply_text if client.reply_text else 'None'}`
**{sc('Admins')}:** `{len(client.admins)}`
**{sc('Start Message')}:**
<pre>{client.messages.get('START', 'Empty')}</pre>
**{sc('Start Image')}:** `{bool(client.messages.get('START_PHOTO', ''))}`
**{sc('Force Sub Message')}:**
<pre>{client.messages.get('FSUB', 'Empty')}</pre>
**{sc('Force Sub Image')}:** `{bool(client.messages.get('FSUB_PHOTO', ''))}`
**{sc('About Message')}:**
<pre>{client.messages.get('ABOUT', 'Empty')}</pre>
**{sc('Reply Message')}:**
<pre>{client.reply_text}</pre>
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

    await message.reply(msg, reply_markup=reply_markup)
