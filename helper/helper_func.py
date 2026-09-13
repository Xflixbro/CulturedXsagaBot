import base64
import re
import asyncio
import aiohttp
from urllib.parse import quote

from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    UserNotParticipant,
    Forbidden,
    PeerIdInvalid,
    ChatAdminRequired,
    FloodWait
)
from datetime import datetime, timedelta
from pyrogram import errors

from config import URL_SHORTENERS, PERMANENT_LINKS, WEBSITE_URL, WEBSITE_PARAM
from helper.font_converter import to_small_caps as sc


# ============================================================
# URL SHORTENER
# ============================================================

async def shorten_url(long_url: str) -> str:
    """
    Shorten URL using configured URL shortener services.

    Supports API URLs containing:
        {api}
        {url}
        {format}

    If a provider does not use placeholders, normal query
    parameters are used.

    Returns:
        Shortened URL if successful.
        Original URL if all providers fail.
    """

    for provider_key, provider_config in URL_SHORTENERS.items():

        # Check provider active status
        if not provider_config.get("active", False):
            print(f"[SHORTENER] {provider_key}: inactive")
            continue

        try:
            api_url = str(
                provider_config.get("api_url", "")
            ).strip()

            api_token = str(
                provider_config.get("api_token", "")
            ).strip()

            format_param = str(
                provider_config.get("format", "text")
            ).strip()

            # Validate API URL
            if not api_url:
                print(
                    f"[SHORTENER] {provider_key}: "
                    f"API URL missing"
                )
                continue

            # Validate API token
            if not api_token:
                print(
                    f"[SHORTENER] {provider_key}: "
                    f"API token missing"
                )
                continue

            # Add HTTPS if missing
            if not api_url.startswith(
                ("http://", "https://")
            ):
                api_url = "https://" + api_url

            # ------------------------------------------------
            # Placeholder based API
            # ------------------------------------------------
            if (
                "{api}" in api_url
                or "{url}" in api_url
                or "{format}" in api_url
            ):

                request_url = api_url.replace(
                    "{api}",
                    quote(api_token, safe="")
                )

                request_url = request_url.replace(
                    "{url}",
                    quote(long_url, safe="")
                )

                request_url = request_url.replace(
                    "{format}",
                    quote(format_param, safe="")
                )

                params = None

            # ------------------------------------------------
            # Normal API URL
            # ------------------------------------------------
            else:

                request_url = api_url

                params = {
                    "api": api_token,
                    "url": long_url
                }

                if format_param:
                    params["format"] = format_param

            print(
                f"[SHORTENER] Trying provider: "
                f"{provider_key}"
            )

            # Do NOT print API token or complete URL
            # to avoid exposing credentials in logs.
            print(
                f"[SHORTENER] API request prepared for "
                f"{provider_key}"
            )

            timeout = aiohttp.ClientTimeout(
                total=15
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    request_url,
                    params=params,
                    allow_redirects=True
                ) as response:

                    response_text = await response.text()

                    response_text = response_text.strip()

                    print(
                        f"[SHORTENER] {provider_key} "
                        f"HTTP {response.status}"
                    )

                    print(
                        f"[SHORTENER] Response: "
                        f"{response_text[:500]}"
                    )

                    # Provider returned an error
                    if response.status != 200:
                        continue

                    short_url = None

                    # ------------------------------------------------
                    # JSON response support
                    # ------------------------------------------------
                    if response_text.startswith("{"):

                        try:

                            data = await response.json(
                                content_type=None
                            )

                            possible_fields = (
                                "shortenedUrl",
                                "short_url",
                                "shorturl",
                                "url",
                                "link",
                                "short"
                            )

                            for field in possible_fields:

                                value = data.get(field)

                                if (
                                    isinstance(value, str)
                                    and value.startswith(
                                        (
                                            "http://",
                                            "https://"
                                        )
                                    )
                                ):

                                    short_url = value
                                    break

                        except Exception as json_error:

                            print(
                                f"[SHORTENER] "
                                f"{provider_key} "
                                f"JSON parse error: "
                                f"{json_error}"
                            )

                    # ------------------------------------------------
                    # Plain text response support
                    # ------------------------------------------------
                    if not short_url:

                        for line in response_text.splitlines():

                            line = line.strip()

                            if line.startswith(
                                (
                                    "http://",
                                    "https://"
                                )
                            ):

                                short_url = line
                                break

                    # ------------------------------------------------
                    # Successful shortening
                    # ------------------------------------------------
                    if short_url:

                        print(
                            f"[SHORTENER] SUCCESS "
                            f"{provider_key}: "
                            f"{short_url}"
                        )

                        return short_url

                    print(
                        f"[SHORTENER] {provider_key}: "
                        f"No valid short URL found "
                        f"in response"
                    )

        except asyncio.TimeoutError:

            print(
                f"[SHORTENER] TIMEOUT "
                f"{provider_key}"
            )

            continue

        except aiohttp.ClientError as e:

            print(
                f"[SHORTENER] NETWORK ERROR "
                f"{provider_key}: {e}"
            )

            continue

        except Exception as e:

            print(
                f"[SHORTENER] ERROR "
                f"{provider_key}: "
                f"{type(e).__name__}: {e}"
            )

            continue

    # ------------------------------------------------------------
    # All providers failed
    # ------------------------------------------------------------

    print(
        "[SHORTENER] ALL PROVIDERS FAILED - "
        "using original URL"
    )

    return long_url


# ============================================================
# BASE64 ENCODE / DECODE
# ============================================================

async def encode(string):

    string_bytes = string.encode("utf-8")

    base64_bytes = base64.urlsafe_b64encode(
        string_bytes
    )

    base64_string = (
        base64_bytes.decode("ascii")
    ).strip("=")

    return base64_string


async def decode(base64_string):

    base64_string = base64_string.strip("=")

    base64_bytes = (
        base64_string
        + "=" * (-len(base64_string) % 4)
    ).encode("ascii")

    string_bytes = base64.urlsafe_b64decode(
        base64_bytes
    )

    string = string_bytes.decode("utf-8")

    return string


# ============================================================
# TOKEN FUNCTIONS
# ============================================================

import secrets as _secrets
import string as _string


def generate_token(length: int = 14) -> str:
    """
    Generate a cryptographically secure random token.
    URL-safe, alphanumeric only.
    """

    alphabet = (
        _string.ascii_letters
        + _string.digits
    )

    return "".join(
        _secrets.choice(alphabet)
        for _ in range(length)
    )


def is_token_format(s: str) -> bool:
    """
    Check if string looks like a new-style token.

    Alphanumeric, 12-16 characters.
    """

    return (
        s.isalnum()
        and 12 <= len(s) <= 16
    )


# ============================================================
# LINK GENERATION
# ============================================================

def generate_links(
    param: str,
    bot_username: str
):
    """
    Generate both Telegram and permanent
    website links for a given parameter.

    Returns:
        (telegram_link, permanent_link or None)
    """

    telegram_link = (
        f"https://t.me/"
        f"{bot_username}?start={param}"
    )

    permanent_link = None

    if PERMANENT_LINKS and WEBSITE_URL:

        permanent_link = (
            f"{WEBSITE_URL}?"
            f"{WEBSITE_PARAM}={param}"
        )

    return (
        telegram_link,
        permanent_link
    )


# ============================================================
# GET MESSAGES
# ============================================================

async def get_messages(
    client,
    message_ids,
    chat_id=None
):

    messages = []

    total_messages = 0

    while total_messages != len(message_ids):

        temb_ids = message_ids[
            total_messages:
            total_messages + 200
        ]

        msgs = []

        try:

            msgs = await client.get_messages(
                chat_id=(
                    chat_id
                    if chat_id
                    else int(client.db)
                ),
                message_ids=temb_ids
            )

        except FloodWait as e:

            await asyncio.sleep(e.x)

            msgs = await client.get_messages(
                chat_id=(
                    chat_id
                    if chat_id
                    else int(client.db)
                ),
                message_ids=temb_ids
            )

        total_messages += len(temb_ids)

        messages.extend(msgs)

    return messages


# ============================================================
# GET MESSAGE ID
# ============================================================

async def get_message_id(
    client,
    message
):

    # Get main DB channel ID
    main_channel = getattr(
        client,
        "db_channel_id",
        client.db
    )

    # Get extra DB channels from MongoDB
    extra_channels = (
        await client.mongodb.get_db_channels()
        if hasattr(client, "mongodb")
        else []
    )

    # Combine all valid DB channels
    all_db_channels = (
        [main_channel]
        + extra_channels
    )

    # --------------------------------------------------------
    # Support for Pyrogram v2
    # --------------------------------------------------------

    if (
        hasattr(message, "forward_origin")
        and message.forward_origin
    ):

        if (
            message.forward_origin.type
            == "channel"
        ):

            fwd_chat_id = (
                message.forward_origin.chat.id
            )

            fwd_msg_id = (
                message.forward_origin.message_id
            )

            if fwd_chat_id in all_db_channels:

                return (
                    fwd_msg_id,
                    fwd_chat_id
                )

            else:

                return 0, None

    # --------------------------------------------------------
    # Support for Pyrogram v1
    # --------------------------------------------------------

    if message.forward_from_chat:

        if (
            message.forward_from_chat.id
            in all_db_channels
        ):

            return (
                message.forward_from_message_id,
                message.forward_from_chat.id
            )

        else:

            return 0, None

    elif message.forward_sender_name:

        return 0, None

    elif message.text:

        pattern = (
            r"https://t.me/(?:c/)?(.*)/(\d+)"
        )

        matches = re.match(
            pattern,
            message.text
        )

        if not matches:

            return 0, None

        channel_identifier = matches.group(1)

        msg_id = int(
            matches.group(2)
        )

        # Private channel
        if channel_identifier.isdigit():

            channel_id = int(
                f"-100{channel_identifier}"
            )

            if channel_id in all_db_channels:

                return (
                    msg_id,
                    channel_id
                )

        # Public channel
        else:

            if (
                hasattr(client, "db_channel")
                and client.db_channel.username
                and channel_identifier
                == client.db_channel.username
            ):

                return (
                    msg_id,
                    client.db_channel.id
                )

    else:

        return 0, None

    return 0, None


# ============================================================
# READABLE TIME
# ============================================================

def get_readable_time(
    seconds: int
) -> str:

    count = 0

    up_time = ""

    time_list = []

    time_suffix_list = [
        "s",
        "m",
        "h",
        "days"
    ]

    while count < 4:

        count += 1

        remainder, result = (
            divmod(seconds, 60)
            if count < 3
            else divmod(seconds, 24)
        )

        if (
            seconds == 0
            and remainder == 0
        ):

            break

        time_list.append(
            int(result)
        )

        seconds = int(remainder)

    hmm = len(time_list)

    for x in range(hmm):

        time_list[x] = (
            str(time_list[x])
            + time_suffix_list[x]
        )

    if len(time_list) == 4:

        up_time += (
            f"{time_list.pop()}, "
        )

    time_list.reverse()

    up_time += ":".join(
        time_list
    )

    return up_time


# ============================================================
# CHECK BOT ADMIN
# ============================================================

async def is_bot_admin(
    client,
    channel_id
):

    try:

        bot = await client.get_chat_member(
            channel_id,
            "me"
        )

        if bot.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ):

            return True, None

        return (
            False,
            "Bot is not an admin in the channel."
        )

    except UserNotParticipant:

        return (
            False,
            "Bot is not in the channel."
        )

    except errors.ChatAdminRequired:

        return (
            False,
            "Bot lacks permission to access "
            "admin information in this channel."
        )

    except Exception as e:

        return (
            False,
            f"Unexpected error: {str(e)}"
        )


# ============================================================
# CHECK SUBSCRIPTION
# ============================================================

async def check_subscription(
    client,
    user_id
):

    """
    Check if a user is subscribed
    to all required channels.
    """

    statuses = {}

    for (
        channel_id,
        (
            channel_name,
            channel_link,
            request,
            timer
        )
    ) in client.fsub_dict.items():

        # Join request check
        if request:

            send_req = (
                await client.mongodb
                .is_user_in_channel(
                    channel_id,
                    user_id
                )
            )

            if send_req:

                statuses[channel_id] = (
                    ChatMemberStatus.MEMBER
                )

                continue

        try:

            user = await client.get_chat_member(
                channel_id,
                user_id
            )

            statuses[channel_id] = (
                user.status
            )

        except UserNotParticipant:

            statuses[channel_id] = (
                ChatMemberStatus.BANNED
            )

        except Forbidden:

            client.LOGGER(
                __name__,
                client.name
            ).warning(
                f"Bot lacks permission "
                f"for {channel_name}."
            )

            statuses[channel_id] = None

        except Exception as e:

            client.LOGGER(
                __name__,
                client.name
            ).warning(
                f"Error checking "
                f"{channel_name}: {e}"
            )

            statuses[channel_id] = None

    return statuses


# ============================================================
# CHECK USER SUBSCRIBED
# ============================================================

def is_user_subscribed(
    statuses
):

    """
    Check if user is subscribed
    to all channels.
    """

    return (
        all(
            status in {
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            }
            for status in statuses.values()
            if status is not None
        )
        and bool(statuses)
    )


# ============================================================
# FORCE SUBSCRIPTION
# ============================================================

def force_sub(func):

    """
    Decorator to enforce force subscription
    before executing a command.
    """

    async def wrapper(
        client: Client,
        message: Message
    ):

        # No force-sub channels
        if not client.fsub_dict:

            return await func(
                client,
                message
            )

        photo = client.messages.get(
            "FSUB_PHOTO",
            ""
        )

        # Checking subscription message
        if photo:

            msg = await message.reply_photo(
                caption=(
                    "<code>"
                    "Checking subscription..."
                    "</code>"
                ),
                photo=photo
            )

        else:

            msg = await message.reply(
                "<code>"
                "Checking subscription..."
                "</code>"
            )

        user_id = message.from_user.id

        statuses = await check_subscription(
            client,
            user_id
        )

        # ----------------------------------------------------
        # User subscribed
        # ----------------------------------------------------

        if is_user_subscribed(statuses):

            await msg.delete()

            return await func(
                client,
                message
            )

        # ----------------------------------------------------
        # User is not subscribed
        # ----------------------------------------------------

        buttons = []

        channels_message = (
            f"{client.messages.get('FSUB', '')}"
            "\n\n"
            "<b>"
            "ᴄʜᴀɴɴᴇʟ  "
            "ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ  "
            "ꜱᴛᴀᴛᴜꜱ:"
            "</b>"
            "\n\n"
        )

        status_emojis = {

            ChatMemberStatus.MEMBER:
                "✅",

            ChatMemberStatus.ADMINISTRATOR:
                "🛡️",

            ChatMemberStatus.OWNER:
                "👑",

            ChatMemberStatus.BANNED:
                "❌",

            None:
                "⚠️"
        }

        c = 0

        for (
            channel_id,
            (
                channel_name,
                channel_link,
                request,
                timer
            )
        ) in client.fsub_dict.items():

            status = statuses.get(
                channel_id,
                None
            )

            emoji = status_emojis.get(
                status,
                "❓"
            )

            # Check if user is joined
            is_joined = status in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            )

            # Status text
            status_text = (
                f"<b>{sc('Joined')}</b>"
                if is_joined
                else
                f"<b>{sc('Not Joined')}</b>"
            )

            c += 1

            channels_message += (
                f"<b>{c}.</b> "
                f"<b>{channel_name}</b> - "
                f"{status_text} "
                f"{emoji}\n"
            )

            # Temporary invite link
            if timer > 0:

                expire_time = (
                    datetime.now()
                    + timedelta(
                        minutes=timer
                    )
                )

                invite = (
                    await client
                    .create_chat_invite_link(
                        chat_id=channel_id,
                        expire_date=expire_time,
                        creates_join_request=request
                    )
                )

                channel_link = (
                    invite.invite_link
                )

            # Add channel button
            if not is_joined:

                buttons.append(
                    InlineKeyboardButton(
                        channel_name,
                        url=channel_link
                    )
                )

        # ----------------------------------------------------
        # Try Again button
        # ----------------------------------------------------

        from_link = message.text.split(" ")

        if len(from_link) > 1:

            try_again_link = (
                f"https://t.me/"
                f"{client.username}/"
                f"?start={from_link[1]}"
            )

            buttons.append(
                InlineKeyboardButton(
                    "🔄 Try Again!",
                    url=try_again_link
                )
            )

        # ----------------------------------------------------
        # Organize buttons in rows of 2
        # ----------------------------------------------------

        buttons_markup = InlineKeyboardMarkup(
            [
                buttons[i:i + 2]
                for i in range(
                    0,
                    len(buttons),
                    2
                )
            ]
        )

        buttons_markup = (
            None
            if not buttons
            else buttons_markup
        )

        # ----------------------------------------------------
        # Update subscription message
        # ----------------------------------------------------

        try:

            await msg.edit_text(
                text=channels_message,
                reply_markup=buttons_markup
            )

        except Exception as e:

            client.LOGGER(
                __name__,
                client.name
            ).warning(
                f"Error updating message: {e}"
            )

    return wrapper


# ============================================================
# DELETE FILES
# ============================================================

async def delete_files(
    messages,
    client,
    k,
    enter
):

    auto_del = client.auto_del

    if auto_del > 0:

        await asyncio.sleep(
            auto_del
        )

        # Delete all messages
        # in the list
        for msg in messages:

            if msg and msg.chat:

                try:

                    await client.delete_messages(
                        chat_id=msg.chat.id,
                        message_ids=[msg.id]
                    )

                except Exception as e:

                    client.LOGGER(
                        __name__,
                        client.name
                    ).warning(
                        "The attempt to delete "
                        f"the media "
                        f"{getattr(msg, 'id', 'Unknown')} "
                        f"was unsuccessful: {e}"
                    )

            else:

                client.LOGGER(
                    __name__,
                    client.name
                ).warning(
                    "Encountered an empty "
                    "or deleted message."
                )

        # Edit warning message
        # Don't delete it
        try:

            await k.edit_text(
                "<b><i>"
                "⏰ Time is over\n"
                "Your files has been deleted ✅"
                "</i></b>",
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            client.LOGGER(
                __name__,
                client.name
            ).warning(
                "Failed to edit completion "
                f"message: {e}"
            )
