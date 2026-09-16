# Made by @Awakeners_Bots
# link_generator.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.helper_func import encode, get_message_id
from helper.font_converter import to_small_caps as sc
from plugins.antibypass import send_masked_link


def _cancel_btn():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")
    ]])


def _build_bot_link(client: Client, file_token: str) -> str:
    """Return a PERMANENT plain Telegram bot link (no gateway, no expiry)."""
    return f"https://t.me/{client.username}?start={file_token}"


async def _build_and_reply(client, source_message, file_token, file_name,
                           is_batch=False, restricted=False, prefix=""):
    # Plain permanent bot link — no gateway, no expiry
    bot_link = _build_bot_link(client, file_token)

    head = f"<blockquote><b>📂 {file_name}</b></blockquote>\n\n" if file_name else ""
    body = (
        f"{prefix}{head}"
        f"<b>{sc('here is your link')}</b>\n\n"
        f'<a href="{bot_link}">🔗 {sc("Open Link")}</a>\n\n'
        f"<code>{bot_link}</code>"
    )
    if restricted:
        body += f"\n\n<i>{sc('non-premium users cannot forward or save')}</i>"

    buttons = [[InlineKeyboardButton(
        f"🔁 {sc('share url')}",
        url=f"https://telegram.me/share/url?url={bot_link}",
    )]]
    await source_message.reply_text(
        body, quote=True,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=False,
    )


# ══════════════════════════════════════════════════════════
#  /batch  →  multi-file batch, permanent link
# ══════════════════════════════════════════════════════════
@Client.on_message(filters.private & filters.command("batch"))
async def batch(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    cb = _cancel_btn()

    while True:
        try:
            ask = await message.reply(f"{sc('forward the')} **{sc('first message')}**..", reply_markup=cb)
            r = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        if isinstance(r, CallbackQuery):
            if r.data == "cancel_batch_process":
                await r.answer(sc("cancelled"), show_alert=True); await r.message.delete()
                return await message.reply(f"❌ {sc('cancelled')}")
            await r.answer(sc("wrong button"), show_alert=True); continue
        f_id, f_ch = await get_message_id(client, r)
        if f_id: await ask.delete(); break
        await r.reply(f"❌ {sc('not a db channel post')}")

    while True:
        try:
            ask = await message.reply(f"{sc('forward the')} **{sc('last message')}**..", reply_markup=cb)
            r = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        if isinstance(r, CallbackQuery):
            if r.data == "cancel_batch_process":
                await r.answer(sc("cancelled"), show_alert=True); await r.message.delete()
                return await message.reply(f"❌ {sc('cancelled')}")
            await r.answer(sc("wrong button"), show_alert=True); continue
        s_id, s_ch = await get_message_id(client, r)
        if s_id: await ask.delete(); break
        await r.reply(f"❌ {sc('not a db channel post')}")

    batch_name = ""
    try:
        fm = await client.get_messages(f_ch, f_id)
        if fm:
            if fm.document: batch_name = fm.document.file_name
            elif fm.caption: batch_name = fm.caption.split("\n")[0][:50] + "..."
    except Exception:
        pass

    try:
        token = await client.mongodb.create_file_token(f_ch, f_id, is_batch=True, end_msg_id=s_id)
    except Exception:
        token = await encode(f"get-{f_id * abs(f_ch)}-{s_id * abs(f_ch)}")

    info = f"<blockquote><b>📦 {sc('batch')}</b>\n"
    if batch_name: info += f"📄 {batch_name}\n"
    info += f"🔢 {sc('range')}: {f_id} - {s_id}</blockquote>\n\n"

    await _build_and_reply(client, r, token, batch_name, is_batch=True, prefix=info)


# ══════════════════════════════════════════════════════════
#  /rbatch  →  restricted batch, permanent link
# ══════════════════════════════════════════════════════════
@Client.on_message(filters.private & filters.command("rbatch"))
async def rbatch(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    cb = _cancel_btn()

    while True:
        try:
            ask = await message.reply(f"{sc('forward the')} **{sc('first message')}**..", reply_markup=cb)
            r = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        if isinstance(r, CallbackQuery):
            if r.data == "cancel_batch_process":
                await r.answer(sc("cancelled"), show_alert=True); await r.message.delete()
                return await message.reply(f"❌ {sc('cancelled')}")
            await r.answer(sc("wrong button"), show_alert=True); continue
        f_id, f_ch = await get_message_id(client, r)
        if f_id: await ask.delete(); break
        await r.reply(f"❌ {sc('not a db channel post')}")

    while True:
        try:
            ask = await message.reply(f"{sc('forward the')} **{sc('last message')}**..", reply_markup=cb)
            r = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        if isinstance(r, CallbackQuery):
            if r.data == "cancel_batch_process":
                await r.answer(sc("cancelled"), show_alert=True); await r.message.delete()
                return await message.reply(f"❌ {sc('cancelled')}")
            await r.answer(sc("wrong button"), show_alert=True); continue
        s_id, s_ch = await get_message_id(client, r)
        if s_id: await ask.delete(); break
        await r.reply(f"❌ {sc('not a db channel post')}")

    batch_name = ""
    try:
        fm = await client.get_messages(f_ch, f_id)
        if fm:
            if fm.document: batch_name = fm.document.file_name
            elif fm.caption: batch_name = fm.caption.split("\n")[0][:50] + "..."
    except Exception:
        pass

    try:
        token = await client.mongodb.create_file_token(f_ch, f_id, is_batch=True, end_msg_id=s_id, restricted=True)
    except Exception:
        token = await encode(f"rget-{str(f_ch).replace('-100','')}-{f_id}")

    info = f"<blockquote><b>🔒 {sc('restricted batch')}</b>\n"
    if batch_name: info += f"📄 {batch_name}\n"
    info += f"🔢 {sc('range')}: {f_id} - {s_id}</blockquote>\n\n"

    await _build_and_reply(client, r, token, batch_name, is_batch=True, restricted=True, prefix=info)


# ══════════════════════════════════════════════════════════
#  /genlink  →  single file, permanent link
# ══════════════════════════════════════════════════════════
@Client.on_message(filters.private & filters.command("genlink"))
async def genlink(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    cb = _cancel_btn()

    while True:
        try:
            ask = await message.reply(f"{sc('forward message from the db channel')}..", reply_markup=cb)
            r = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        if isinstance(r, CallbackQuery):
            if r.data == "cancel_batch_process":
                await r.answer(sc("cancelled"), show_alert=True); await r.message.delete()
                return await message.reply(f"❌ {sc('cancelled')}")
            await r.answer(sc("wrong button"), show_alert=True); continue
        msg_id, ch_id = await get_message_id(client, r)
        if msg_id: await ask.delete(); break
        await r.reply(f"❌ {sc('not a db channel post')}")

    file_name = ""
    try:
        fm = await client.get_messages(ch_id, msg_id)
        if fm:
            if fm.document: file_name = fm.document.file_name
            elif fm.caption: file_name = fm.caption.split("\n")[0][:50]
    except Exception:
        pass

    try:
        token = await client.mongodb.create_file_token(ch_id, msg_id)
    except Exception:
        token = await encode(f"get-{msg_id * abs(ch_id)}")

    await _build_and_reply(client, r, token, file_name)


# ══════════════════════════════════════════════════════════
#  /rgenlink  →  restricted single file, permanent link
# ══════════════════════════════════════════════════════════
@Client.on_message(filters.private & filters.command("rgenlink"))
async def rgenlink(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    cb = _cancel_btn()

    while True:
        try:
            ask = await message.reply(f"{sc('forward message from the db channel')}..", reply_markup=cb)
            r = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        if isinstance(r, CallbackQuery):
            if r.data == "cancel_batch_process":
                await r.answer(sc("cancelled"), show_alert=True); await r.message.delete()
                return await message.reply(f"❌ {sc('cancelled')}")
            await r.answer(sc("wrong button"), show_alert=True); continue
        msg_id, ch_id = await get_message_id(client, r)
        if msg_id: await ask.delete(); break
        await r.reply(f"❌ {sc('not a db channel post')}")

    file_name = ""
    try:
        fm = await client.get_messages(ch_id, msg_id)
        if fm:
            if fm.document: file_name = fm.document.file_name
            elif fm.caption: file_name = fm.caption.split("\n")[0][:50]
    except Exception:
        pass

    try:
        token = await client.mongodb.create_file_token(ch_id, msg_id, restricted=True)
    except Exception:
        token = await encode(f"rget-{str(ch_id).replace('-100','')}-{msg_id}")

    await _build_and_reply(client, r, token, file_name, restricted=True)


# ══════════════════════════════════════════════════════════
#  Auto handler → admin forwards a file, bot replies with link
# ══════════════════════════════════════════════════════════
@Client.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio)
    & ~filters.command(["start", "batch", "rbatch", "genlink", "rgenlink"])
)
async def single_file_gen_handler(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return
    if message.text and message.text.startswith("/"):
        return

    try:
        msg = await message.reply(f"🔄 {sc('processing')}...", quote=True)
        main_channel = getattr(client, "db_channel_id", client.db)
        ch_id = main_channel
        msg_id = None

        if hasattr(message, "forward_origin") and message.forward_origin \
                and message.forward_origin.type == "channel":
            fwd = message.forward_origin.chat.id
            extras = await client.mongodb.get_db_channels()
            if fwd in [main_channel] + extras:
                msg_id = message.forward_origin.message_id
                ch_id = fwd
        elif message.forward_from_chat:
            fwd = message.forward_from_chat.id
            extras = await client.mongodb.get_db_channels()
            if fwd in [main_channel] + extras:
                msg_id = message.forward_from_message_id
                ch_id = fwd

        if not msg_id:
            ch_id = await client.mongodb.get_next_db_channel(main_channel)
            post = await message.copy(chat_id=ch_id, caption=message.caption)
            msg_id = post.id

        file_name = ""
        if message.document: file_name = message.document.file_name
        elif message.caption: file_name = message.caption.split("\n")[0][:50]

        try:
            token = await client.mongodb.create_file_token(ch_id, msg_id)
        except Exception:
            token = await encode(f"get-{msg_id * abs(ch_id)}")

        bot_link = _build_bot_link(client, token)

        body = ""
        if file_name:
            body += f"<blockquote><b>📂 {file_name}</b></blockquote>\n\n"
        body += (
            f"<b>{sc('here is your link')}</b>\n\n"
            f'<a href="{bot_link}">🔗 {sc("Open Link")}</a>\n\n'
            f"<code>{bot_link}</code>"
        )

        await msg.edit_text(
            body,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"🔁 {sc('share url')}",
                                     url=f"https://telegram.me/share/url?url={bot_link}")
            ]]),
            disable_web_page_preview=False,
        )
    except Exception as e:
        print(f"[single_file_gen] {e}")
        await message.reply(f"❌ {sc('error')}: {e}")
