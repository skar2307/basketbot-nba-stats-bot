"""
This is the main file of the bot. 
All of the cogs are imported to here and this is the file from which the actual bot runs.
"""

# Futures
import discord
from discord.ext import commands
# imports the discord.py library 

from cogs.dataretrieval import DataRetrieval
from cogs.misc import Miscellaneous
# imports the classes in which all of the commands are stored 

from credentials import token
# imports the token to run the bot

bot = commands.Bot(command_prefix = 'gimme ')
# creates the actual instance of the bot and sets the command prefix

bot.remove_command('help')
# I created my own help command as the one the comes with the library is sub-optimal

bot.load_extension(f'cogs.dataretrieval')
bot.load_extension(f'cogs.misc')
# this is where the actual classes are loaded

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
# this is to notify me when the bot is actually running, which really helps for testing commands and troubleshooting
# right now, I'm hosting this bot locally so this is very useful to have.

bot.run(token)
# this is the token from which the bot accesses Discord itself
# it is linked to the bot that is made on my account
