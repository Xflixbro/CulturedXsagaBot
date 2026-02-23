# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import MSG_EFFECT
from helper.font_converter import to_small_caps as sc

# ==================== CONFIGURABLE LINKS ====================
CHANNEL_MAIN = "https://t.me/YourMainChannel"          # Replace with your main channel URL
CHANNEL_MOVIES = "http://t.me/Cineflix_Saga"
CHANNEL_SERIES = "http://t.me/seriesflix_Saga"
CHANNEL_ANIME = "http://t.me/anime_Saga"
CHANNEL_DRAMA = "http://t.me/drama_Saga"
# ============================================================

# Credit info text (as you requested)
CREDIT_TEXT = """
⍟───[ ᴍʏ ᴄʀᴇᴅɪᴛꜱ & ɪɴꜰᴏ ]───⍟

➥ ᴏᴡɴᴇʀ : xᴇᴏɴ
➥ ʙᴀꜱᴇ ᴄᴏᴅᴇ : ʏᴀᴛᴏ
➥ ᴇxᴛʀᴀ ꜰᴇᴀᴛᴜʀᴇꜱ : ɢᴏᴊᴏ ꜱᴀᴛᴏʀᴜ
➥ ᴛʜᴀɴᴋꜱ ᴛᴏ : ᴛʜɪs ᴘᴇʀsᴏɴ
➥ ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : ʜᴇʀᴇ
➥ ᴛʜɪꜱ ɪꜱ ᴀ ᴘʀɪᴠᴀᴛᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴘʀᴏᴊᴇᴄᴛ
"""

# Disclaimer text (you can change this)
DISCLAIMER_TEXT = (
    "**Disclaimer:**\n\n"
    "This bot is for educational purposes only. "
    "All content shared is the responsibility of the user. "
    "We do not host any files on our servers."
)

# ==================== BUTTON LAYOUT FUNCTIONS ====================

def home_buttons(user_id=None):
    """Page 1 buttons – adds Settings button if user is admin"""
    buttons = [
        [InlineKeyboardButton("Disclaimer", callback_data="disclaimer"),
         InlineKeyboardButton("About", callback_data="about")],
        [InlineKeyboardButton("Premium", callback_data="premium_plans"),
         InlineKeyboardButton("Channel URL", url=CHANNEL_MAIN)],
        [InlineKeyboardButton("Next ➡️", callback_data="page_two")]
    ]
    # If admin, insert Settings button at the top
    if user_id and user_id in client.admins:  # Note: client is not available here; we'll handle in start.py
        # Actually we cannot access client here. Better to handle admin check in start.py and pass a flag.
        # We'll modify to accept an `is_admin` boolean.
        pass
    # For simplicity, we'll handle admin check in start.py and call a separate function for admin keyboard.
    return InlineKeyboardMarkup(buttons)

def home_buttons_admin():
    """Home page with Settings button for admins"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌜ꜱᴇᴛᴛɪɴɢꜱ⌟", callback_data="settings")],
        [InlineKeyboardButton("Disclaimer", callback_data="disclaimer"),
         InlineKeyboardButton("About", callback_data="about")],
        [InlineKeyboardButton("Premium", callback_data="premium_plans"),
         InlineKeyboardButton("Channel URL", url=CHANNEL_MAIN)],
        [InlineKeyboardButton("Next ➡️", callback_data="page_two")]
    ])

def page_two_buttons():
    """Page 2 buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Disclaimer", callback_data="disclaimer"),
         InlineKeyboardButton("About", callback_data="about")],
        [InlineKeyboardButton("Premium", callback_data="premium_plans"),
         InlineKeyboardButton("Channels", callback_data="channels_menu")],
        [InlineKeyboardButton("⬅️ Previous", callback_data="home"),
         InlineKeyboardButton("Credit", callback_data="credit_info")]
    ])

def channels_menu_buttons():
    """Channels submenu"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Movies", url=CHANNEL_MOVIES)],
        [InlineKeyboardButton("Series", url=CHANNEL_SERIES)],
        [InlineKeyboardButton("Anime", url=CHANNEL_ANIME)],
        [InlineKeyboardButton("Drama", url=CHANNEL_DRAMA)],
        [InlineKeyboardButton("Home", callback_data="home"),
         InlineKeyboardButton("Close", callback_data="close")]
    ])

# ==================== CALLBACK HANDLERS ====================

@Client.on_callback_query(filters.regex('^home$'))
async def home_callback(client: Client, query: CallbackQuery):
    """New home menu (Page 1) – with admin check"""
    user_id = query.from_user.id
    if user_id in client.admins:
        markup = home_buttons_admin()
    else:
        markup = home_buttons()
    await query.message.edit_text(
        text=client.messages.get('START', 'Welcome!').format(
            first=query.from_user.first_name,
            mention=query.from_user.mention
        ),
        reply_markup=markup
    )

@Client.on_callback_query(filters.regex('^page_two$'))
async def page_two_callback(client: Client, query: CallbackQuery):
    """Page 2"""
    await query.message.edit_text(
        text="**Page 2**",   # You can replace this text
        reply_markup=page_two_buttons()
    )

@Client.on_callback_query(filters.regex('^channels_menu$'))
async def channels_menu_callback(client: Client, query: CallbackQuery):
    """Channels submenu"""
    await query.message.edit_text(
        text="**Our Channels**\n\nClick below to join:",
        reply_markup=channels_menu_buttons()
    )

@Client.on_callback_query(filters.regex('^credit_info$'))
async def credit_info_callback(client: Client, query: CallbackQuery):
    """Credit info panel"""
    await query.message.edit_text(
        text=CREDIT_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Home", callback_data="home"),
             InlineKeyboardButton("Close", callback_data="close")]
        ])
    )

@Client.on_callback_query(filters.regex('^disclaimer$'))
async def disclaimer_callback(client: Client, query: CallbackQuery):
    """Disclaimer panel"""
    await query.message.edit_text(
        text=DISCLAIMER_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data="home")]
        ])
    )

@Client.on_callback_query(filters.regex('^close$'))
async def close_callback(client: Client, query: CallbackQuery):
    """Delete the message"""
    await query.message.delete()

# -------------------- Existing about and premium_plans callbacks (keep) --------------------

@Client.on_callback_query(filters.regex('^about$'))
async def about(client: Client, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("🏠 Home", callback_data="home")]]
    await query.message.edit_text(
        text=client.messages.get('ABOUT', 'No Start Message').format(
            owner_id=client.owner,
            bot_username=client.username,
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return

@Client.on_callback_query(filters.regex('^premium_plans$'))
async def premium_plans_callback(client: Client, query: CallbackQuery):
    premium_text = (
        "Hello <b>{}</b>, \n\n"
        "• Why Pay For Your Waifu?\n"
        "📜 <b>Pricing:</b>\n"
        "╭──────────\n"
        "↻ ₹99 / $1 : 1 Month\n"
        "↻ ₹179 / $2 : 2 Months\n"
        "↻ ₹249/ $2.5: 3 Months (Most Bought)\n"
        "↻ ₹399 / $6 : 6 Months\n"
        "↻ ₹699/ $10 : 9 Months\n"
        "↻ ₹999 / $12 : 12 Months\n"
        "╰──────────\n\n"
        "<b>💎 Premium Benefits:</b>\n"
        "✓ Direct File Access\n"
        "✓ No Ads or URL Shorteners\n"
        "✓ Priority Support\n"
        "✓ Fast Downloads\n\n"
        "Contact here for further inquiry - @Cultured_Support_bot"
    ).format(query.from_user.first_name)
    
    buttons = [
        [InlineKeyboardButton("💰 Buy Now", url="https://t.me/Cultured_Support_bot?start=0")],
        [InlineKeyboardButton("🔙 Back", callback_data="home")]
    ]
    
    await query.message.edit_text(
        text=premium_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return

# -------------------- Ban/Unban commands (keep) --------------------

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
                continue
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} users have been banned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
                continue
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} users have been unbanned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")
