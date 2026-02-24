# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters, enums
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import MSG_EFFECT
from helper.font_converter import to_small_caps as sc

# ==================== CONFIGURABLE LINKS ====================
CHANNEL_MAIN = "https://t.me/YourMainChannel"          # Replace with your main channel URL
CHANNEL_MOVIES = "http://t.me/Cineflix_Saga"
CHANNEL_SERIES = "http://t.me/seriesflix_Saga"
CHANNEL_ANIMES = "http://t.me/anime_Saga"              # ANIMES button
CHANNEL_ADULT = "http://t.me/culturedxsaga"            # ADULT button – replace with actual link
# ============================================================

# Credit info text with HTML links – bold small caps
CREDIT_TEXT = """
<b>⍟───[ ᴍʏ ᴄʀᴇᴅɪᴛꜱ & ɪɴꜰᴏ ]───⍟

➥ ᴏᴡɴᴇʀ : <a href='t.me/Xeonflixadmin'>xᴇᴏɴ</a>
➥ ʙᴀꜱᴇ ᴄᴏᴅᴇ : <a href='t.me/cosmic_freak'>ʏᴀᴛᴏ</a>
➥ ᴇxᴛʀᴀ ꜰᴇᴀᴛᴜʀᴇꜱ : <a href='t.me/MrXeonTG'>ɢᴏᴊᴏ ꜱᴀᴛᴏʀᴜ</a>
➥ ᴛʜᴀɴᴋꜱ ᴛᴏ : <a href='t.me/codexbotz'>ᴄᴏᴅᴇx ʙᴏᴛ</a>
➥ ᴛʜᴀɴᴋꜱ ᴛᴏ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a>
➥ ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : <a href='https://youtu.be/uf8F97ONQbc?si=6icZPNIvFEf-bXeU'>ʜᴇʀᴇ</a>
➥ ᴛʜɪꜱ ɪꜱ ᴀ ᴘʀɪᴠᴀᴛᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴘʀᴏᴊᴇᴄᴛ</b>
"""

# Disclaimer text – exact copy with small caps, wrapped in bold
DISCLAIMER_TEXT = """
<b>ᴀʟʟ ᴛʜᴇ ꜰɪʟᴇꜱ ɪɴ ᴛʜɪꜱ ʙᴏᴛ ᴀʀᴇ ꜰʀᴇᴇʟʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴛʜᴇ ɪɴᴛᴇʀɴᴇᴛ ᴏʀ ᴘᴏꜱᴛᴇᴅ ʙʏ ꜱᴏᴍᴇʙᴏᴅʏ ᴇʟꜱᴇ. ᴊᴜꜱᴛ ꜰᴏʀ ᴇᴀꜱʏ ꜱᴇᴀʀᴄʜɪɴɢ ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ɪɴᴅᴇxɪɴɢ ꜰɪʟᴇꜱ ᴡʜɪᴄʜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴜᴘʟᴏᴀᴅᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ. ᴡᴇ ʀᴇꜱᴘᴇᴄᴛ ᴀʟʟ ᴛʜᴇ ᴄᴏᴘʏʀɪɢʜᴛ ʟᴀᴡꜱ ᴀɴᴅ ᴡᴏʀᴋꜱ ɪɴ ᴄᴏᴍᴘʟɪᴀɴᴄᴇ ᴡɪᴛʜ ᴅᴍᴄᴀ ᴀɴᴅ ᴇᴜᴄᴅ. ɪꜰ ᴀɴʏᴛʜɪɴɢ ɪꜱ ᴀɢᴀɪɴꜱᴛ ʟᴀᴡ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ꜱᴏ ᴛʜᴀᴛ ɪᴛ ᴄᴀɴ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ ᴀꜱᴀᴘ. ɪᴛ ɪꜱ ꜰᴏʀʙɪʙʙᴇɴ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ, ꜱᴛʀᴇᴀᴍ, ʀᴇᴘʀᴏᴅᴜᴄᴇ, ꜱʜᴀʀᴇ ᴏʀ ᴄᴏɴꜱᴜᴍᴇ ᴄᴏɴᴛᴇɴᴛ ᴡɪᴛʜᴏᴜᴛ ᴇxᴘʟɪᴄɪᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ᴄʀᴇᴀᴛᴏʀ ᴏʀ ʟᴇɢᴀʟ ᴄᴏᴘʏʀɪɢʜᴛ ʜᴏʟᴅᴇʀ. ɪꜰ ʏᴏᴜ ʙᴇʟɪᴇᴠᴇ ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴠɪᴏʟᴀᴛɪɴɢ ʏᴏᴜʀ ɪɴᴛᴇʟʟᴇᴄᴛᴜᴀʟ ᴘʀᴏᴘᴇʀᴛʏ, ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʀᴇꜱᴘᴇᴄᴛɪᴠᴇ ᴄʜᴀɴɴᴇʟꜱ ꜰᴏʀ ʀᴇᴍᴏᴠᴀʟ. ᴛʜᴇ ʙᴏᴛ ᴅᴏᴇꜱ ɴᴏᴛ ᴏᴡɴ ᴀɴʏ ᴏꜰ ᴛʜᴇꜱᴇ ᴄᴏɴᴛᴇɴᴛꜱ, ɪᴛ ᴏɴʟʏ ɪɴᴅᴇx ᴛʜᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴛᴇʟᴇɢʀᴀᴍ.</b>
"""

# ==================== BUTTON LAYOUT FUNCTIONS ====================

def home_buttons():
    """Home page buttons (normal user) – no Next button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴅɪꜱᴄʟᴀɪᴍᴇʀ •", callback_data="disclaimer"),
         InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about")],
        [InlineKeyboardButton("• ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium_plans"),
         InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url=CHANNEL_MAIN)]
    ])

def home_buttons_admin():
    """Home page with Settings button for admins – no Next button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢꜱ •", callback_data="settings")],
        [InlineKeyboardButton("• ᴅɪꜱᴄʟᴀɪᴍᴇʀ •", callback_data="disclaimer"),
         InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about")],
        [InlineKeyboardButton("• ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium_plans"),
         InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url=CHANNEL_MAIN)]
    ])

def about_submenu_buttons():
    """Buttons shown inside About – Channels, Credit, Settings, Back"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟꜱ •", callback_data="channels_menu"),
         InlineKeyboardButton("• ᴄʀᴇᴅɪᴛꜱ •", callback_data="credit_info")],
        [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢꜱ •", callback_data="settings"),
         InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="home")]
    ])

def channels_menu_buttons():
    """Channels submenu – 3 rows of 2 buttons each (as requested)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴍᴏᴠɪᴇꜱ •", url=CHANNEL_MOVIES),
         InlineKeyboardButton("• ꜱᴇʀɪᴇꜱ •", url=CHANNEL_SERIES)],
        [InlineKeyboardButton("• ᴀɴɪᴍᴇꜱ •", url=CHANNEL_ANIMES),
         InlineKeyboardButton("• ᴀᴅᴜʟᴛ •", url=CHANNEL_ADULT)],
        [InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="home"),
         InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]
    ])

# ==================== CALLBACK HANDLERS ====================

@Client.on_callback_query(filters.regex('^home$'))
async def home_callback(client: Client, query: CallbackQuery):
    """Home page – with admin check"""
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
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^about$'))
async def about_callback(client: Client, query: CallbackQuery):
    """About page – now shows Channels, Credit, and Settings submenu (no extra text)"""
    about_text = client.messages.get('ABOUT', 'About this bot').format(
        owner_id=client.owner,
        bot_username=client.username,
        first=query.from_user.first_name,
        last=query.from_user.last_name,
        username=None if not query.from_user.username else '@' + query.from_user.username,
        mention=query.from_user.mention,
        id=query.from_user.id
    )
    await query.message.edit_text(
        text=about_text,  # Removed the extra line
        reply_markup=about_submenu_buttons(),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^channels_menu$'))
async def channels_menu_callback(client: Client, query: CallbackQuery):
    """Channels submenu – Updated with text to prevent API error"""
    await query.message.edit_text(
        text="<b>ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟs:</b>",  # Text cannot be empty
        reply_markup=channels_menu_buttons(),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^credit_info$'))
async def credit_info_callback(client: Client, query: CallbackQuery):
    """Credit info panel with HTML links – bold small caps"""
    await query.message.edit_text(
        text=CREDIT_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Home", callback_data="home"),
             InlineKeyboardButton("Close", callback_data="close")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^disclaimer$'))
async def disclaimer_callback(client: Client, query: CallbackQuery):
    """Disclaimer panel – bold small caps"""
    await query.message.edit_text(
        text=DISCLAIMER_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data="home")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^close$'))
async def close_callback(client: Client, query: CallbackQuery):
    """Delete the message"""
    await query.message.delete()

# -------------------- Premium plans callback (unchanged) --------------------

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
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
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
