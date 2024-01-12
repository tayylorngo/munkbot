import discord

from backend.server_db_functions import set_leaderboard, get_leaderboard_today, get_leaderboard_by_date


def create_server_stats_embed(win_percent, lose_percent, tie_percent,
                              favorite_team, favorite_team_count,
                              least_favorite_team, least_favorite_team_count):
    embed = discord.Embed(title=f"Server Data")
    embed.set_thumbnail(
        url="https://as2.ftcdn.net/v2/jpg/05/51/62/11/1000_F_551621197_S10xwpM2ZdotzGiS69GP0T1JrI66e9cs.jpg")
    embed.add_field(name="Win Percentage", value=f"{win_percent}%")
    embed.add_field(name="Lose Percentage", value=f"{lose_percent}%", inline=True)
    embed.add_field(name="Tie Percentage", value=f"{tie_percent}%", inline=True)
    embed.add_field(name="Favorite Team", value=f"{favorite_team} ({favorite_team_count} votes)", inline=False)
    embed.add_field(name="Least Favorite Team"
                    , value=f"{least_favorite_team} ({least_favorite_team_count} votes)", inline=False)
    embed.set_footer(text="munk Bot made this Embed")
    return embed


def create_user_stats_embed(name, wins, losses, win_percent, lose_percent
                            , favorite_team, favorite_team_count
                            , least_favorite_team, least_favorite_team_count, avg_odds, pfp):
    embed = discord.Embed(title=f"Stats for: {name}", description=f"{wins}W-{losses}L")
    # embed.set_author(name=f"{name}")
    embed.set_thumbnail(url=f"{pfp}")
    embed.add_field(name="Win Percentage", value=f"{win_percent}%")
    embed.add_field(name="Lose Percentage", value=f"{lose_percent}%", inline=True)
    embed.add_field(name="Favorite Team", value=f"{favorite_team} ({favorite_team_count} votes)", inline=False)
    embed.add_field(name="Least Favorite Team"
                    , value=f"{least_favorite_team} ({least_favorite_team_count} votes)", inline=False)
    embed.add_field(name="Average Betting Odds", value=f"{avg_odds}")
    embed.set_footer(text="munk Bot made this Embed")
    return embed


def create_leaderboard_embed(user_db, server_db, date):
    if date == "":
        leaderboard = get_leaderboard_today(server_db)
    else:
        leaderboard = get_leaderboard_by_date(server_db, date)
        if not leaderboard:
            return None
    if not leaderboard:
        set_leaderboard(user_db, server_db)
        leaderboard = get_leaderboard_today(server_db)
    users = leaderboard['leaderboard']
    embed = discord.Embed(title="Server Leaderboard " + leaderboard["date"] + " 🏆")
    for i in enumerate(users):
        num = i[0]
        user = i[1]
        wins = user["betting_stats"]["wins"]
        losses = user["betting_stats"]["losses"]
        win_percent = round(user["betting_stats"]["win_percent"] * 100, 2)
        lose_percent = round(user["betting_stats"]["lose_percent"] * 100, 2)
        emoji = ""
        if num == 0:
            emoji = " 🥇"
        elif num == 1:
            emoji = " 🥈"
        elif num == 2:
            emoji = " 🥉"
        elif num == len(users) - 1:
            emoji = " 🗑️"
        field_title = (str(num + 1) + ". " + user["display_name"] + emoji
                       + " (" + str(wins) + "W-" + str(losses) + "L)")
        field_value = "Win Rate: " + str(win_percent) + "%"
        embed.add_field(name=field_title, value="", inline=False)
    return embed
