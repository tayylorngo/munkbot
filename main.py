import datetime
import pytz
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient
import asyncio
import settings
import discord
from discord.ext import commands
import game_requests
from backend.game_db_functions import get_today_games, add_new_game, game_add_message_id, update_game_votes, \
    get_yesterday_games, update_game_results
from backend.server_db_functions import init_server_data, get_server_data
from backend.user_db_functions import get_user, add_new_user, update_user_on_vote, update_user_on_vote_remove, \
    update_user_results, get_user_by_name
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
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_daily_message, 'cron', hour=2, minute=0, timezone="US/Eastern")
        scheduler.add_job(update_game_results_message, 'cron', hour=2, minute=0, timezone="US/Eastern")
        scheduler.start()

    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")

    @bot.command()
    async def record(ctx):
        server_stats = get_server_data(server_db)
        if server_stats:
            await ctx.send("CURRENT RECORD: " + str(server_stats["wins"]) + "W-" + str(server_stats["losses"]) + "L-"
                           + str(server_stats["ties"]) + "T")
        else:
            await ctx.send("No stats available as of now")

    @bot.command()
    async def stats(ctx, username="server"):
        if username == "server":
            server_stats = get_server_data(server_db)
            if server_stats:
                await ctx.send("SERVER DATA: ")
                win_percent = round(server_stats["wins"]
                                    / (server_stats["wins"] + server_stats["losses"] + server_stats["ties"]), 2) * 100
                lose_percent = round(server_stats["losses"]
                                     / (server_stats["wins"] + server_stats["losses"] + server_stats["ties"]), 2) * 100
                tie_percent = 100 - win_percent - lose_percent
                await ctx.send("Win Percentage: " + str(win_percent) + "%")
                await ctx.send("Lose Percentage: " + str(lose_percent) + "%")
                await ctx.send("Tie Percentage: " + str(tie_percent) + "%")
                await ctx.send("Favorite Team: " + server_stats["favorite_team"]
                               + "(" + server_stats["voted_teams"][server_stats["favorite_team"]] + " votes)")
                await ctx.send("Least Favorite Team: " + server_stats["least_favorite_team"]
                               + "(" + server_stats["voted_teams"][server_stats["least_favorite_team"]] + " votes)")
            else:
                await ctx.send("No data available as of now")
        else:
            user = get_user_by_name(user_db, username)
            if user:
                # Display user stats
                await ctx.send(user['username'] + " DATA:")
                await ctx.send(str(user['betting_stats']['wins']) + "W-" + str(user['betting_stats']['losses']) + "L")
                await ctx.send("Win Percentage: " + str(round(user['betting_stats']['win_percent'], 2)) + "%")
                await ctx.send("Lose Percentage: " + str(round(user['betting_stats']['lose_percent'], 2)) + "%")
                await ctx.send("Favorite Team: " + user['betting_stats']['favorite_team']
                               + "(" + user['teams_voted_on'][user['betting_stats']['favorite_team']] + " votes)")
                await ctx.send("Least Favorite Team: " + user['betting_stats']['least_favorite_team']
                               + "(" + user['teams_voted_on'][user['betting_stats']['least_favorite_team']] + " votes)")
                await ctx.send("Average Odds Voted On: " + round(user['betting_stats']['average_betting_odds'], 2))
            else:
                await ctx.send("No user data available as of now")

    def get_game_data():
        return game_requests.filter_data(game_requests.get_data())

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            if "@everyone" in message.content or "NBA Games" in message.content:
                return
            if "@" in message.content:
                away_emoji = logo_table[get_away_team(message)]
                home_emoji = logo_table[get_home_team(message)]
                await message.add_reaction(away_emoji)
                await asyncio.sleep(1)
                await message.add_reaction(home_emoji)
        await bot.process_commands(message)

    @bot.event
    async def on_raw_reaction_remove(payload):
        channel = bot.get_channel(payload.channel_id)
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
    async def on_raw_reaction_add(payload):
        if str(payload.emoji) not in logo_table.values():
            return
        today_games = get_today_games(game_db)
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await bot.fetch_user(payload.user_id)
        if payload.user_id == bot.user.id:
            for game in today_games:
                if (game["home_team"] == get_home_team(message)
                        and game["away_team"] == get_away_team(message)):
                    game_add_message_id(game_db, game, payload.message_id)
            return
        voted_team = get_key(str(payload.emoji))
        team1_emoji = logo_table[get_away_team(message)]
        team2_emoji = logo_table[get_home_team(message)]
        now_date = datetime.datetime.utcnow()
        utc_timezone = pytz.timezone('UTC')
        est_timezone = pytz.timezone('America/New_York')
        est_now = utc_timezone.localize(now_date).astimezone(est_timezone)
        message_created_on = utc_timezone.localize(message.created_at).astimezone(est_timezone)
        if message_created_on.date() == est_now:
            for game in today_games:
                if game['message_id'] == payload.message_id:
                    voting_user = get_user(user_db, user.id)
                    if not voting_user:
                        add_new_user(user_db, game, user, payload.emoji, voted_team)
                        voting_user = get_user(user_db, user.id)
                    else:
                        update_user_on_vote(user_db, voting_user, game, voted_team)
                    update_game_votes(game_db, voting_user, voted_team, message, True)
                    break
        if str(payload.emoji) == team1_emoji:
            for r in message.reactions:
                if str(r) == team2_emoji:
                    await r.remove(user)
        else:
            for r in message.reactions:
                if str(r) == team1_emoji:
                    await r.remove(user)
        print(user.name + " voted for " + voted_team)

    async def send_daily_message():
        game_data = get_game_data()
        channel = bot.get_channel(1166613333630267412)
        # 1166613333630267412
        await channel.send("NBA Games for: " + datetime.datetime.now().date().__str__())
        for game in game_data:
            add_new_game(game_db, game)
            await channel.send(game)
            await asyncio.sleep(3)
        await channel.send("@everyone PLEASE VOTE!")

    async def update_game_results_message():
        yesterday_date = datetime.date.today() - datetime.timedelta(days=1)
        game_results = filter_results_data(get_game_results(), yesterday_date)

        for game in game_results:
            update_game_results(game_db, game)

        yesterday_games = get_yesterday_games(game_db)
        for game in yesterday_games:
            update_user_results(user_db, game)

        server_stats = server_db.games.find_one({"name": "red_army"})
        if not server_stats:
            init_server_data(server_db)
        server_stats = server_db.games.find_one({"name": "red_army"})
        channel = bot.get_channel(1166613333630267412)
        # 1166613333630267412 RED ARMY
        # 1181446708232716321 TEST
        yesterday_games = get_yesterday_games(game_db)
        for game in yesterday_games:
            if game['majority_team'] in server_stats['voted_teams']:
                if game['majority_team'] != "tie":
                    server_stats['voted_teams'].update(
                        {
                            game['majority_team']: (server_stats['voted_teams'][game['majority_team']]) + 1
                        }
                    )
            else:
                if game['majority_team'] != "tie":
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
            await asyncio.sleep(3)

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
