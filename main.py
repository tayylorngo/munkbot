import datetime
import asyncio

import settings
import discord
from discord.ext import commands
import game_requests

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await send_daily_message()

    async def send_daily_message():
        now = datetime.datetime.now()
        then = now + datetime.timedelta(days=1)
        then.replace(hour=2, minute=0)
        # then = now.replace(hour=21, minute=5)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        channel = bot.get_channel(1181446708232716321)
        await channel.send("GOOD MORNING!")

    bot.run(settings.TOKEN, root_logger=True)


if __name__ == "__main__":
    run()
