import discord


def create_user_stats_embed(name, wins, losses, win_percent, lose_percent
                            , favorite_team, favorite_team_count
                            , least_favorite_team, least_favorite_team_count, avg_odds, pfp):
    embed = discord.Embed(title=f"Stats for: {name}", description=f"{wins}W-{losses}L")
    embed.set_author(name=f"{name}")
    embed.set_thumbnail(url=f"{pfp}")
    embed.add_field(name="Win Percentage", value=f"{win_percent}%")
    embed.add_field(name="Lose Percentage", value=f"{lose_percent}%", inline=True)
    embed.add_field(name="Favorite Team", value=f"{favorite_team} ({favorite_team_count} votes)", inline=False)
    embed.add_field(name="Least Favorite Team"
                    , value=f"{least_favorite_team} ({least_favorite_team_count} votes)", inline=False)
    embed.add_field(name="Average Betting Odds", value=f"{avg_odds}")
    embed.set_footer(text="munk Bot made this Embed")
    return embed
