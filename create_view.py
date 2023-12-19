import discord
from discord.ui import Button, View


def create_message_view(game):
    button1 = Button(style=discord.ButtonStyle.grey, emoji="<:grizzlies:555506226901942273>")
    button2 = Button(style=discord.ButtonStyle.grey, emoji="<:grizzlies:555506226901942273>")
    view = View()
    view.add_item(button1)
    view.add_item(button2)
    return view
