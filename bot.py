# Made by @Awakeners_Bots
# bot.py

from aiohttp import web
import asyncio
import time
from plugins import web_server

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, RPCError
import sys
from datetime import datetime
from config import LOGGER, PORT, OWNER_ID
from helper import MongoDB


class Bot(Client):
    def __init__(self, session, workers, db, fsub, token, admins, messages,
                 auto_del, db_uri, db_name, api_id, api_hash, protect, disable_btn):
        super().__init__(
            name=session, api_hash=api_hash, api_id=api_id,
            plugins={"root": "plugins"}, workers=workers, bot_token=token
        )
        self.LOGGER = LOGGER
        self.name = session
        self.db = db
        self.fsub = fsub
        self.owner = OWNER_ID
        self.fsub_dict = {}
        self.admins = admins + [OWNER_ID] if OWNER_ID not in admins else admins
        self.messages = messages
        self.auto_del = auto_del
        self.protect = protect
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = messages.get('REPLY', 'Do not send any useless message in the bot.')
        self.mongodb = MongoDB(db_uri, db_name)
        self.db_uri = db_uri
        self.db_name = db_name
        self.req_channels = []

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if len(self.fsub) > 0:
            for channel in self.fsub:
                try:
                    chat = await self.get_chat(channel[0])
                    name = chat.title
                    link = None
                    if not channel[1]:
                        link = chat.invite_link
                    if not link and not channel[2]:
                        chat_link = await self.create_chat_invite_link(channel[0], creates_join_request=channel[1])
                        link = chat_link.invite_link
                    if not channel[1]:
                        self.fsub_dict[channel[0]] = [name, link, False, 0]
                    if channel[1]:
                        self.fsub_dict[channel[0]] = [name, link, True, 0]
                        self.req_channels.append(channel[0])
                    if channel[2] > 0:
                        self.fsub_dict[channel[0]] = [name, None, channel[1], channel[2]]
                except Exception as e:
                    self.LOGGER(__name__, self.name).warning("Bot can't Export Invite link from Force Sub Channel!")
                    self.LOGGER(__name__, self.name).warning("\nBot Stopped.")
                    await self.stop()
                    return
            await self.mongodb.set_channels(self.req_channels)

        # DB channel check
        try:
            db_channel = None
            for attempt in range(3):
                try:
                    db_channel = await self.get_chat(self.db)
                    break
                except (PeerIdInvalid, ChannelInvalid) as e:
                    self.LOGGER(__name__, self.name).warning(f"Attempt {attempt+1}/3 to load DB channel: {e}")
                    await asyncio.sleep(1)
                except RPCError as rpc_e:
                    self.LOGGER(__name__, self.name).warning(f"RPC error: {rpc_e}")
                    await asyncio.sleep(1)

            if not db_channel:
                self.LOGGER(__name__, self.name).warning(f"Unable to load DB channel: {self.db}")
                await self.stop()
                return

            self.db_channel = db_channel
            self.db_channel_id = db_channel.id

            test = None
            for attempt in range(3):
                try:
                    test = await self.send_message(chat_id=db_channel.id, text="Testing Message")
                    break
                except Exception as e:
                    self.LOGGER(__name__, self.name).warning(f"Test send attempt {attempt+1}: {e}")
                    await asyncio.sleep(1)

            if not test:
                self.LOGGER(__name__, self.name).warning("Failed to send test to DB channel.")
                await self.stop()
                return

            try:
                await test.delete()
            except Exception:
                pass
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(e)
            await self.stop()
            return

        self.LOGGER(__name__, self.name).info("Bot Started!!")
        self.username = usr_bot_me.username

        try:
            await self.mongodb.ensure_token_indexes()
            self.LOGGER(__name__, self.name).info("Token indexes ensured.")
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"Index create failed: {e}")

        try:
            stored_auto_del = await self.mongodb.get_bot_config('auto_del')
            if stored_auto_del is not None:
                self.auto_del = int(stored_auto_del)
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"Load auto_del failed: {e}")

        try:
            asyncio.create_task(self._broadcast_ttl_worker())
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"TTL worker failed: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped.")

    async def _broadcast_ttl_worker(self):
        while True:
            try:
                now_ts = int(time.time())
                jobs = await self.mongodb.get_due_broadcast_jobs(now_ts, limit=200)
                if not jobs:
                    await asyncio.sleep(5)
                    continue
                for job in jobs:
                    chat_id = job.get('chat_id')
                    msg_id = job.get('message_id')
                    job_id = job.get('_id')
                    try:
                        await self.delete_messages(chat_id=chat_id, message_ids=msg_id)
                    except Exception:
                        pass
                    finally:
                        try:
                            await self.mongodb.remove_broadcast_job(job_id)
                        except Exception:
                            pass
                await asyncio.sleep(1)
            except Exception as loop_err:
                self.LOGGER(__name__, self.name).warning(f"TTL worker error: {loop_err}")
                await asyncio.sleep(5)


async def web_app(bot_instance=None):
    from plugins.web_api import setup_routes
    from plugins import web_server as _ws

    aio_app = await _ws()

    if bot_instance is not None:
        try:
            setup_routes(aio_app, bot_instance)
            print("[web_api] API routes registered.")
        except Exception as e:
            print(f"[web_api] setup failed: {e}")

    runner = web.AppRunner(aio_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
