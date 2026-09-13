import base64
import re
import asyncio
import aiohttp
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired, FloodWait
from datetime import datetime, timedelta
from pyrogram import errors
from config import PERMANENT_LINKS, WEBSITE_URL, WEBSITE_PARAM
from helper.font_converter import to_small_caps as sc


async def shorten_url(long_url: str, client=None) -> str:
    """Shorten URL using the configured single shortener (client.short_url + client.short_api)."""
    if client is None:
        return long_url

    if not getattr(client, 'shortner_enabled', False):
        return long_url

    short_domain = getattr(client, 'short_url', None)
    api_key = getattr(client, 'short_api', None)
    if not short_domain or not api_key:
        return long_url

    try:
        import secrets as _s
        alias = _s.token_urlsafe(6).replace('-', '').replace('_', '')[:8]
        api_url = f"https://{short_domain}/api?api={api_key}&url={long_url}&alias={alias}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if isinstance(data, dict) and data.get("status") == "success":
                            return data.get("shortenedUrl", long_url)
                    except Exception:
                        text = (await response.text()).strip()
                        if text.startswith('http'):
                            return text
    except Exception as e:
        print(f"[Shortener Error] {e}")

    return long_url


async def encode(string):
    string_bytes = string.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string


async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("utf-8")
    return string


import secrets as _secrets
import string as _string


def generate_token(length: int = 14) -> str:
    """Generate a cryptographically secure random token (URL-safe, alphanumeric only)."""
    alphabet = _string.ascii_letters + _string.digits
    return ''.join(_secrets.choice(alphabet) for _ in range(length))


def is_token_format(s: str) -> bool:
    """Check if string looks like a new-style token (alphanumeric, 12-16 chars, no special chars)."""
    return s.isalnum() and 12 <= len(s) <= 16


def generate_links(param: str, bot_username: str):
    """Generate both Telegram and permanent (website) links for a given parameter."""
    telegram_link = f"https://t.me/{bot_username}?start={param}"
    permanent_link = None
    if PERMANENT_LINKS and WEBSITE_URL:
        permanent_link = f"{WEBSITE_URL}?{WEBSITE_PARAM}={param}"
    return telegram_link, permanent_link


async def get_messages(client, message_ids, chat_id=None):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages + 200]
        msgs = []
        try:
            msgs = await client.get_messages(
                chat_id=chat_id if chat_id else int(client.db),
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=chat_id if chat_id else int(client.db),
                message_ids=temb_ids
            )

        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(client, message):
    main_channel = getattr(client, 'db_channel_id', client.db)
    extra_channels = await client.mongodb.get_db_channels() if hasattr(client, 'mongodb') else []
    all_db_channels = [main_channel] + extra_channels

    if hasattr(message, 'forward_origin') and message.forward_origin:
        if message.forward_origin.type == "channel":
            fwd_chat_id = message.forward_origin.chat.id
            fwd_msg_id = message.forward_origin.message_id
            if fwd_chat_id in all_db_channels:
                return fwd_msg_id, fwd_chat_id
            else:
                return 0, None

    if message.forward_from_chat:
        if message.forward_from_chat.id in all_db_channels:
            return message.forward_from_message_id, message.forward_from_chat.id
        else:
            return 0, None
    elif message.forward_sender_name:
        return 0, None
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0, None
        channel_identifier = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_identifier.isdigit():
            channel_id = int(f"-100{channel_identifier}")
            if channel_id in all_db_channels:
                return msg_id, channel_id
        else:
            if hasattr(client, 'db_channel') and client.db_channel.username and channel_identifier == client.db_channel.username:
                return msg_id, client.db_channel.id
    else:
        return 0, None
    return 0, None


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time


async def is_bot_admin(client, channel_id):
    try:
        bot = await client.get_chat_member(channel_id, "me")
        if bot.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return True, None
        return False, "Bot is not an admin in the channel."
    except UserNotParticipant:
        return False, "Bot is not in the channel."
    except errors.ChatAdminRequired:
        return False, "Bot lacks permission to access admin information in this channel."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


async def check_subscription(client, user_id):
    """Check if a user is subscribed to all required channels."""
    statuses = {}

    for channel_id, (channel_name, channel_link, request, timer) in client.fsub_dict.items():
        if request:
            send_req = await client.mongodb.is_user_in_channel(channel_id, user_id)
            if send_req:
                statuses[channel_id] = ChatMemberStatus.MEMBER
                continue
        try:
            user = await client.get_chat_member(channel_id, user_id)
            statuses[channel_id] = user.status
        except UserNotParticipant:
            statuses[channel_id] = ChatMemberStatus.BANNED
        except Forbidden:
            client.LOGGER(__name__, client.name).warning(f"Bot lacks permission for {channel_name}.")
            statuses[channel_id] = None
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error checking {channel_name}: {e}")
            statuses[channel_id] = None

    return statuses


def is_user_subscribed(statuses):
    """Check if user is subscribed to all channels."""
    return all(
        status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        for status in statuses.values() if status is not None
    ) and bool(statuses)


def force_sub(func):
    """Decorator to enforce force subscription before executing a command."""
    async def wrapper(client: Client, message: Message):
        if not client.fsub_dict:
            return await func(client, message)
        photo = client.messages.get('FSUB_PHOTO', '')
        if photo:
            msg = await message.reply_photo(
                caption="<code>Checking subscription...</code>",
                photo=photo
            )
        else:
            msg = await message.reply(
                "<code>Checking subscription...</code>"
            )
        user_id = message.from_user.id
        statuses = await check_subscription(client, user_id)

        if is_user_subscribed(statuses):
            await msg.delete()
            return await func(client, message)

        buttons = []
        channels_message = f"{client.messages.get('FSUB', '')}\n\n<b>ᴄʜᴀɴɴᴇʟ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ꜱᴛᴀᴛᴜꜱ:</b>\n\n"

        status_emojis = {
            ChatMemberStatus.MEMBER: "✅",
            ChatMemberStatus.ADMINISTRATOR: "🛡️",
            ChatMemberStatus.OWNER: "👑",
            ChatMemberStatus.BANNED: "❌",
            None: "⚠️"
        }
        c = 0
        for channel_id, (channel_name, channel_link, request, timer) in client.fsub_dict.items():
            status = statuses.get(channel_id, None)
            emoji = status_emojis.get(status, "❓")
            is_joined = status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
            status_text = f"<b>{sc('Joined')}</b>" if is_joined else f"<b>{sc('Not Joined')}</b>"
            c += 1
            channels_message += f"<b>{c}.</b> <b>{channel_name}</b> - {status_text} {emoji}\n"
            if timer > 0:
                expire_time = datetime.now() + timedelta(minutes=timer)
                invite = await client.create_chat_invite_link(
                    chat_id=channel_id,
                    expire_date=expire_time,
                    creates_join_request=request
                )
                channel_link = invite.invite_link
            if not is_joined:
                buttons.append(InlineKeyboardButton(channel_name, url=channel_link))

        from_link = message.text.split(" ")
        if len(from_link) > 1:
            try_again_link = f"https://t.me/{client.username}/?start={from_link[1]}"
            buttons.append(InlineKeyboardButton("🔄 Try Again!", url=try_again_link))

        buttons_markup = InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)])
        buttons_markup = None if not buttons else buttons_markup
        try:
            await msg.edit_text(text=channels_message, reply_markup=buttons_markup)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error updating message: {e}")

    return wrapper


async def delete_files(messages, client, k, enter):
    auto_del = client.auto_del
    if auto_del > 0:
        await asyncio.sleep(auto_del)

        for msg in messages:
            if msg and msg.chat:
                try:
                    await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"The attempt to delete the media {getattr(msg, 'id', 'Unknown')} was unsuccessful: {e}")
            else:
                client.LOGGER(__name__, client.name).warning("Encountered an empty or deleted message.")

        try:
            await k.edit_text(
                "<b><i>⏰ Time is over\nYour files has been deleted ✅</i></b>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to edit completion message: {e}")
