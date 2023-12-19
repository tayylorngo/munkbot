import discord
from discord.ui import Button, View


def create_message_view(game):
    button1 = Button(label=game.away_team, style=discord.ButtonStyle.primary, emoji="<:grizzlies:555506226901942273>")
    button2 = Button(label=game.home_team, style=discord.ButtonStyle.primary, emoji="<:grizzlies:555506226901942273>")
    view = View()
    view.add_item(button1)
    view.add_item(button2)
    return view
