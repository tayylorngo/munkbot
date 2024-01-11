import math

import discord


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


def calculate_leaderboard_ranking(user):
    wins = user['betting_stats']['wins']
    total_games_played = user['betting_stats']['wins'] + user['betting_stats']['losses']
    win_percent = wins / total_games_played if total_games_played > 0 else 0
    weight_factor = math.sqrt(total_games_played)
    return win_percent * weight_factor


def create_leaderboard_embed(users):
    users = sorted(users, key=calculate_leaderboard_ranking, reverse=True)
    embed = discord.Embed(title="Server Leaderboard 🏆")
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
