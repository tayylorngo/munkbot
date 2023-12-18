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

    def get_game_data():
        return game_requests.filter_data(game_requests.get_data())

    async def send_daily_message():
        now = datetime.datetime.now()
        then = now + datetime.timedelta(days=1)
        then.replace(hour=2, minute=0)
        # then = now.replace(hour=13, minute=37)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        game_data = get_game_data()
        channel = bot.get_channel(1181446708232716321)
        for game in game_data:
            await channel.send(game)

    bot.run(settings.TOKEN, root_logger=True)


if __name__ == "__main__":
    run()
