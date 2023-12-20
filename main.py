import datetime
import asyncio

import settings
import discord
from discord.ext import commands
import game_requests
from nba_logos import logo_table, get_key

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

    @bot.event
    async def on_message(message):
        if "@" not in message.content or "@everyone" in message.content:
            return
        if message.author == bot.user:
            away_team = message.content[0: message.content.find("(") - 1]
            home_team = message.content[message.content.find("@"):]
            home_team = home_team[2:home_team.find("(") - 1]
            away_emoji = logo_table[away_team]
            home_emoji = logo_table[home_team]
            await message.add_reaction(away_emoji)
            await message.add_reaction(home_emoji)
        else:
            return

    @bot.event
    async def on_reaction_add(reaction, user):
        print(reaction)
        if user == bot.user:
            return
        print(user.name + " voted for " + get_key(str(reaction)))

    @bot.event
    async def on_reaction_remove(reaction, user):
        print(reaction)
        if user == bot.user:
            return
        print(user.name + " un-voted for " + get_key(str(reaction)))

    async def send_daily_message():
        now = datetime.datetime.now()
        # then = now + datetime.timedelta(days=1)
        # then.replace(hour=2, minute=0)
        then = now.replace(hour=20, minute=11)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        game_data = get_game_data()
        channel = bot.get_channel(1181446708232716321)
        await channel.send("NBA Games for: " + datetime.datetime.now().date().__str__())
        for game in game_data:
            await channel.send(game)
        await channel.send("@everyone PLEASE VOTE!")

    bot.run(settings.TOKEN, root_logger=True)


if __name__ == "__main__":
    run()
