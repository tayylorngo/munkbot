import datetime
import asyncio
import os

from pymongo import MongoClient

import settings
import discord
from discord.ext import commands
import game_requests
from backend.game_db_functions import get_today_games, add_new_game, game_add_message_id
from backend.user_db_functions import get_user, add_new_user, update_user_on_vote, update_user_on_vote_remove
from nba_logos import logo_table, get_key, get_away_team, get_home_team

logger = settings.logging.getLogger("bot")

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    game_db = client.game_data
    server_db = client.server_data
    user_db = client.user_data
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
        channel = bot.get_channel(1181446708232716321)
        reaction = await channel.fetch_message(payload.message_id)
        user = get_user(user_db, payload.user_id)
        voted_team = get_key(str(payload.emoji))
        for game in get_today_games(game_db):
            if game["home_team"] == get_home_team(reaction) and game["away_team"] == get_away_team(reaction):
                update_user_on_vote_remove(user_db, user, game, str(payload.emoji), voted_team)
        print(user["username"] + " un-voted for " + voted_team)

    @bot.event
    async def on_reaction_add(reaction, user):
        today_games = get_today_games(game_db)
        if user == bot.user:
            for game in today_games:
                if (game["home_team"] == get_home_team(reaction.message)
                        and game["away_team"] == get_away_team(reaction.message)):
                    game_add_message_id(game_db, game, reaction.message.id)
            return

        voted_team = get_key(str(reaction))
        team1_emoji = logo_table[get_away_team(reaction.message)]
        team2_emoji = logo_table[get_home_team(reaction.message)]
        # IF REACTION ON DATE OTHER THAN THE CREATED MESSAGE DATE
        if reaction.message.created_at.date() != datetime.datetime.now().date():
            for r in reaction.message.reactions:
                if str(r) == str(reaction):
                    await r.remove(user)
            return

        for game in today_games:
            if (game["home_team"] == get_home_team(reaction.message)
                    and game["away_team"] == get_away_team(reaction.message)):
                voting_user = get_user(user_db, user.id)
                if not voting_user:
                    add_new_user(user_db, game, user, reaction, voted_team)
                else:
                    update_user_on_vote(user_db, voting_user, game, reaction, voted_team)

        if str(reaction) == team1_emoji:
            for r in reaction.message.reactions:
                if str(r) == team2_emoji:
                    await r.remove(user)
        else:
            for r in reaction.message.reactions:
                if str(r) == team1_emoji:
                    await r.remove(user)
        print(user.name + " voted for " + voted_team)

    async def send_daily_message():
        now = datetime.datetime.now()
        # then = now + datetime.timedelta(days=1)
        # then.replace(hour=2, minute=0)
        then = now.replace(hour=0, minute=1)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        game_data = get_game_data()
        channel = bot.get_channel(1181446708232716321)
        await channel.send("NBA Games for: " + datetime.datetime.now().date().__str__())
        for game in game_data:
            add_new_game(game_db, game)
            await channel.send(game)
        await channel.send("@everyone PLEASE VOTE!")

    bot.run(settings.TOKEN, root_logger=True)


if __name__ == "__main__":
    run()
