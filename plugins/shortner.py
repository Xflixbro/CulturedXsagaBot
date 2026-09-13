# URL Shortener System — single provider, alias-based API
# Format: https://{domain}/api?api={key}&url={url}&alias={random}

import requests
import random
import string
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InputMediaPhoto
)
from pyrogram.errors.pyromod import ListenerTimeout
from helper.font_converter import to_small_caps as sc

shortened_urls_cache = {}


def generate_random_alphanumeric(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_short(url: str, client) -> str:
    """Synchronous shortener — for use outside async contexts."""
    if not getattr(client, 'shortner_enabled', False):
        return url
    if not getattr(client, 'short_url', None) or not getattr(client, 'short_api', None):
        return url
    if url in shortened_urls_cache:
        return shortened_urls_cache[url]
    try:
        alias = generate_random_alphanumeric()
        api_url = f"https://{client.short_url}/api?api={client.short_api}&url={url}&alias={alias}"
        response = requests.get(api_url, timeout=5)
        rjson = response.json()
        if rjson.get("status") == "success" and response.status_code == 200:
            short_url = rjson.get("shortenedUrl", url)
            shortened_urls_cache[url] = short_url
            return short_url
    except Exception as e:
        print(f"[Shortener Error] {e}")
    return url


@Client.on_message(filters.command('shortner') & filters.private)
async def shortner_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    await shortner_panel(client, message)


async def shortner_panel(client, query_or_message):
    # ----- health check -----
    if not getattr(client, 'short_url', None) or not getattr(client, 'short_api', None):
        status = f"❌ {sc('not configured')}"
    elif not getattr(client, 'shortner_enabled', False):
        status = f"❌ {sc('disabled')}"
    else:
        try:
            test_url = (
                f"https://{client.short_url}/api?api={client.short_api}"
                f"&url=https://google.com&alias={generate_random_alphanumeric()}"
            )
            r = requests.get(test_url, timeout=5)
            if r.status_code == 200 and r.json().get("status") == "success":
                status = f"✅ {sc('working')}"
            else:
                status = f"⚠️ {sc('api not working')}"
        except Exception:
            status = f"⚠️ {sc('api not working')}"

    enabled_text = f"✅ {sc('enabled')}" if getattr(client, 'shortner_enabled', False) else f"❌ {sc('disabled')}"
    toggle_text = f"🔴 {sc('off')}" if getattr(client, 'shortner_enabled', False) else f"🟢 {sc('on')}"

    api_display = client.short_api or "Not Set"
    if len(api_display) > 20:
        api_display = f"{api_display[:20]}..."

    msg = f"""<blockquote>🔗 <b>{sc('url shortener settings')}</b></blockquote>

<blockquote>» **{sc('status')}:** {enabled_text}
» **{sc('domain')}:** <code>{client.short_url or 'Not Set'}</code>
» **{sc('api key')}:** <code>{api_display}</code>
» **{sc('api health')}:** {status}</blockquote>

<blockquote>**≡ {sc('use the buttons below to manage your shortener')}!**</blockquote>"""

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f'• {toggle_text} {sc("shortener")} •', 'toggle_shortner'),
            InlineKeyboardButton(f'• {sc("add shortener")} •', 'add_shortner')
        ],
        [InlineKeyboardButton(f'• {sc("test shortener")} •', 'test_shortner')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'settings')]
    ])

    image_url = client.messages.get(
        "SHORT",
        "https://graph.org/file/a7ef527466c5603e35200-902c9a04f46b1e06ca.jpg"
    )
    is_callback = hasattr(query_or_message, 'message')
    message = query_or_message.message if is_callback else query_or_message

    if is_callback and message.photo:
        try:
            await message.edit_media(
                media=InputMediaPhoto(media=image_url, caption=msg),
                reply_markup=reply_markup
            )
            return
        except Exception:
            pass

    if is_callback:
        try:
            await message.delete()
        except Exception:
            pass
    await client.send_photo(
        chat_id=message.chat.id,
        photo=image_url,
        caption=msg,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex("^shortner$"))
async def shortner_callback(client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("❌ Only admins can access this!", show_alert=True)
    await query.answer()
    await shortner_panel(client, query)


@Client.on_callback_query(filters.regex("^toggle_shortner$"))
async def toggle_shortner(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("❌ Only admins can access this!", show_alert=True)

    client.shortner_enabled = not getattr(client, 'shortner_enabled', False)
    await client.mongodb.set_bot_config('shortner_enabled', client.shortner_enabled)
    await query.answer(
        f"✅ Shortener {'enabled' if client.shortner_enabled else 'disabled'}!"
    )
    await shortner_panel(client, query)


@Client.on_callback_query(filters.regex("^add_shortner$"))
async def add_shortner(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("❌ Only admins can access this!", show_alert=True)
    await query.answer()

    prompt = await client.send_message(
        query.from_user.id,
        "<blockquote>**Format:** `url api_key`\n"
        "**Example:** `example.com abc123xyz`</blockquote>"
    )
    try:
        res = await client.listen(
            user_id=query.from_user.id, filters=filters.text, timeout=60
        )
        parts = res.text.strip().split()
        if len(parts) >= 2:
            client.short_url = (
                parts[0].replace('https://', '').replace('http://', '').strip('/')
            )
            client.short_api = ' '.join(parts[1:])
            await client.mongodb.set_bot_config('short_url', client.short_url)
            await client.mongodb.set_bot_config('short_api', client.short_api)
            await res.reply("**✅ Shortener updated successfully!**")
        else:
            await res.reply("**❌ Invalid format!**")
    except ListenerTimeout:
        await prompt.edit("**⌛ Timeout!**")

    dummy = await client.send_message(query.from_user.id, "Loading...")
    await shortner_panel(client, dummy)
    try:
        await dummy.delete()
    except Exception:
        pass


@Client.on_callback_query(filters.regex("^test_shortner$"))
async def test_shortner(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("❌ Only admins can access this!", show_alert=True)
    await query.answer()

    await query.message.edit_caption("**🔄 Testing shortener...**")

    if not getattr(client, 'short_api', None):
        return await query.message.edit_caption(
            "**❌ No API key set!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'shortner')]])
        )

    try:
        api_url = (
            f"https://{client.short_url}/api?api={client.short_api}"
            f"&url=https://google.com&alias={generate_random_alphanumeric()}"
        )
        response = requests.get(api_url, timeout=10)
        rjson = response.json()

        if rjson.get("status") == "success" and response.status_code == 200:
            msg = f"**✅ Shortener test successful!**\n\n**Short URL:** `{rjson.get('shortenedUrl', '')}`"
        else:
            msg = f"**❌ Shortener test failed!**\n\n**Error:** `{rjson.get('message', 'Unknown error')}`"
    except Exception as e:
        msg = f"**❌ Shortener test failed!**\n\n**Error:** `{str(e)}`"

    await query.message.edit_caption(
        msg,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'shortner')]])
    )
