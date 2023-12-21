import datetime
import asyncio
import os

from pymongo import MongoClient

import settings
import discord
from discord.ext import commands
import game_requests
from nba_logos import logo_table, get_key, get_away_team, get_home_team

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client.user_data
    db2 = client.server_data
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

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
            away_emoji = logo_table[get_away_team(message)]
            home_emoji = logo_table[get_home_team(message)]
            await message.add_reaction(away_emoji)
            await message.add_reaction(home_emoji)
        else:
            return

    @bot.event
    async def on_raw_reaction_remove(payload):
        user = await bot.fetch_user(payload.user_id)
        print(user.name + " un-voted for " + get_key(str(payload.emoji)))

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user:
            return
        team1_emoji = logo_table[get_away_team(reaction.message)]
        team2_emoji = logo_table[get_home_team(reaction.message)]
        if str(reaction) == team1_emoji:
            for r in reaction.message.reactions:
                if str(r) == team2_emoji:
                    await r.remove(user)
        else:
            for r in reaction.message.reactions:
                if str(r) == team1_emoji:
                    await r.remove(user)
        # db.users.insert_one(
        #     {
        #
        #     }
        # )
        print(user.name + " voted for " + get_key(str(reaction)))

    async def send_daily_message():
        now = datetime.datetime.now()
        # then = now + datetime.timedelta(days=1)
        # then.replace(hour=2, minute=0)
        then = now.replace(hour=12, minute=12)
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
