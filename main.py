# Made by @Awakeners_Bots
# main.py

import asyncio
import json
from bot import Bot, web_app
from pyrogram import compose

default_messages = {
    'START': '<blockquote expandable>__Welcome!__</blockquote>',
    'FSUB': '',
    'ABOUT': 'ABOUT MSG',
    'REPLY': 'reply_text',
    'START_PHOTO': '',
    'FSUB_PHOTO': ''
}


async def main():
    app = []
    with open("setup.json", "r", encoding="utf-8") as f:
        setups = json.load(f)

    for config in setups:
        app.append(
            Bot(
                config["session"],
                config["workers"],
                config["db"],
                config["fsubs"],
                config["token"],
                config["admins"],
                config.get("messages", default_messages),
                config["auto_del"],
                config["db_uri"],
                config["db_name"],
                int(config["api_id"]),
                config["api_hash"],
                config["protect"],
                config["disable_btn"],
            )
        )
    return app


async def runner():
    bots = await main()
    await asyncio.gather(
        compose(bots),
        web_app(bots[0] if bots else None),
    )


asyncio.run(runner())
