# munk Bot
## Introduction
munk Bot is a Discord bot that sends NBA games daily to a specified 
channel and allows users to vote on teams that they think are
going to win via reactions. The bot displays data such as the game being played,
the date, the home/away team, and the betting odds for the game
(Fanduel). The games/results are updated at 2AM EST every day.

## How it works
Every at 2AM EST, the bot will send messages representing each
NBA game for that day. The message will include the match up,
which team is the home/away team and betting odds. Users will
then have the option to vote by reacting with the logo of
the team that they believe will win. At this time, the results
the previous day's game will be updated as well. 

The data is stored in a database and previous results'
messages are updated with reactions representing if
the server predicted the right team (majority votes).

## How to use for your server
For now, I am working on allowing every server to use this
bot without modifying the code. However for now, this is
how you can use the bot.

### 1. Download the code
- Make sure you have all the python files including all
the files in the backend folder and the logs folder as well.
### 2. Add a .env folder to the root folder
    TOKEN= "DISCORD_BOT_TOKEN"
    API_KEY="THE_ODDS_API_KEY"
    MONGO_URI="YOUR_MONGO_URI"
    RESULTS_API_KEY="RESULTS_API_KEY"

Here's how you get each access token:

TOKEN: https://discord.com/developers/applications

- Create a Discord bot application 
- Allow permissions for messaging and retrieving user/server data. 
- There you will get a bot token for the .env file.
    
API_KEY: https://the-odds-api.com/

- Sign up for a free API key using your email.

MONGO_URI: https://www.mongodb.com/

- Sign up for an account and create a cluster. 
- Create a database/database user and grab the corresponding URI. 

RESULTS_API_KEY: https://rapidapi.com/
- Sign up for an account and retrieve an API Key

### 3. Add the bot to your channel
- Through the Discord developer portal, add the bot to your desired channel

### 4. Specify the channel
- Grab the channel id of the text-channel you want the bot to send messages to
  - You have to enable developer mode in user settings > advanced > developer mode
  - You can then right-click on a text channel and copy the channel id
- Replace the channel id in main.py in the following functions
  - send_daily_message()
    -     channel = bot.get_channel(YOUR_CHANNEL_ID)
  - update_game_results_message()
    -     channel = bot.get_channel(YOUR_CHANNEL_ID)

### 5. Host and run the bot
There are many ways to host your bot so that it runs 24/7. Here are some options:
  - Google Cloud
  - Python Anywhere
  - Replit

## Commands
- !stats
  - Retrieves the stats of the server (wins, losses, and ties)

## Future Updates
-  Add a 'last_updated' property in the user/game database
  - Will fix potential errors if the bot goes down and update games from previous dates
  - Currently, the bot only updates games that were played the day before

- More commands
  - Command to check individual user stats
  - Command to retrieve game data (odds/schedule)
  - Command to show leaderboard
  - Update !stats command to show more server stats




    
