import datetime
import pytz
import asyncio
import os

from pymongo import MongoClient

import settings
import discord
from discord.ext import commands
import game_requests
from backend.game_db_functions import get_today_games, add_new_game, game_add_message_id, update_game_votes, \
    get_yesterday_games, update_game_results
from backend.user_db_functions import get_user, add_new_user, update_user_on_vote, update_user_on_vote_remove, \
    update_user_results
from nba_logos import logo_table, get_key, get_away_team, get_home_team
from results_request import get_game_results, filter_results_data

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
        # await send_daily_message()
        await update_game_results_message()

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
        if reaction.created_at.date() != datetime.datetime.now().date():
            return
        user = get_user(user_db, payload.user_id)
        voted_team = get_key(str(payload.emoji))
        for game in get_today_games(game_db):
            if game["home_team"] == get_home_team(reaction) and game["away_team"] == get_away_team(reaction):
                update_user_on_vote_remove(user_db, user, game, str(payload.emoji), voted_team)
                update_game_votes(game_db, user, voted_team, reaction, False)
                break
        print(user["username"] + " un-voted for " + voted_team)

    @bot.event
    async def on_reaction_add(reaction, user):
        if str(reaction) not in logo_table.values():
            return
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
        created_on_date = reaction.message.created_at.astimezone(pytz.timezone('US/Eastern'))
        if created_on_date.date() != datetime.datetime.now().date():
            # print(reaction.message.created_at.date())
            # print(datetime.datetime.now().date())
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
                    update_user_on_vote(user_db, voting_user, game, voted_team)
                voting_user = get_user(user_db, user.id)
                update_game_votes(game_db, voting_user, voted_team, reaction.message, True)
                break

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

    async def update_game_results_message():
        now = datetime.datetime.now()
        # then = now + datetime.timedelta(days=1)
        # then.replace(hour=2, minute=0)
        then = now.replace(hour=0, minute=1)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        yesterday_date = datetime.date.today() - datetime.timedelta(days=1)
        game_results = filter_results_data(get_game_results(), yesterday_date)

        for game in game_results:
            update_game_results(game_db, game)

        yesterday_games = get_yesterday_games(game_db)
        for game in yesterday_games:
            update_user_results(game_db, game)

        server_stats = server_db.games.find_one({"name": "red_army"})
        if not server_stats:
            server_db.games.insert_one(
                {
                    "name": "red_army",
                    "wins": 0,
                    "losses": 0,
                    "ties": 0,
                    "favorite_team": "",
                    "least_favorite_team": "",
                    "voted_teams": {}
                }
            )
        server_stats = server_db.games.find_one({"name": "red_army"})
        channel = bot.get_channel(1181446708232716321)
        yesterday_games = get_yesterday_games(game_db)
        for game in yesterday_games:
            if game['majority_team'] in server_stats['voted_teams']:
                server_stats['voted_teams'].update(
                    {
                        game['majority_team']: (server_stats['voted_teams'][game['majority_team']]) + 1
                    }
                )
            else:
                server_stats['voted_teams'].update(
                    {
                        game['majority_team']: 1
                    }
                )
            message = await channel.fetch_message(game['message_id'])
            if game['winning_team'] == game['majority_team']:
                server_stats['wins'] += 1
                await message.add_reaction("✅")
            elif game['majority_team'] == "tie":
                server_stats['ties'] += 1
                await message.add_reaction("↔️")
            else:
                server_stats['losses'] += 1
                await message.add_reaction("❌")

        curr = 0
        curr2 = max(server_stats['voted_teams'].values(), default=0)
        favorite_team = ""
        least_favorite_team = ""
        for key in server_stats['voted_teams'].keys():
            if server_stats['voted_teams'][key] >= curr:
                curr = server_stats['voted_teams'][key]
                favorite_team = key
            if server_stats['voted_teams'][key] <= curr2:
                curr2 = server_stats['voted_teams'][key]
                least_favorite_team = key

        server_filter = {'name': "red_army"}
        new_values = {"$set": {
            "wins": server_stats["wins"],
            "losses": server_stats["losses"],
            "ties": server_stats["ties"],
            "favorite_team": favorite_team,
            "least_favorite_team": least_favorite_team,
            "voted_teams": server_stats["voted_teams"]
        }}
        server_db.games.update_one(server_filter, new_values)

    bot.run(settings.TOKEN, root_logger=True)


if __name__ == "__main__":
    run()
