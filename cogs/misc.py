"""
This is the cog in which all of the commands not related to NBA.
Things such as the help command and the invite link to invite the bot to your personal server. 
"""

# Futures
import discord
from discord.ext import commands
# imports the discord.py library 

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    #initializes the class whenever it is called
    # class can't work without __init__ function

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send('Enter `gimme help` in the server to get a full description of all the commands.')
    # whenever a new member joins, they are sent a direct message giving them instructions on how to use all the commands.

    @commands.command()
    async def invite_link(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=716825866511974442&permissions=8&scope=bot")
    # whenever this command is called, the bot sends its invite link to the server.
    # this link would allow other users to invite this bot to their own personal server.
    
    @commands.command()
    async def help(self, ctx):

        author = ctx.message.author 

        help_embed = discord.Embed(
            colour = discord.Colour(0x0e1cf5)
        )

        help_embed.set_author(name='Help')
        help_embed.add_field(name='Command Prefix', value='''
        `gimme` is the prefix when using commands. 
        Whenever you want to use a command, you enter `gimme [command_name] [parameters]`.
        For example, `gimme player_info Draymond Green`.
        ''')
        help_embed.add_field(name='invite_link', value='Returns the link to invite the bot to your own Discord server.')
        help_embed.add_field(name='player_info', value ='''
        Returns basic information on a player such as his jersey number, draft position, height, et cetera. 
        Requires you to enter the name of the player with proper capitalization. `Stephen Curry` as opposed to `stephen curry`.
        Shortened names for players, such as `Steph Curry`, also won't be accepted.
        For example `gimme player_info Stephen Curry` would be valid but not `gimme player_info steph curry`.
        ''', inline=False)
        help_embed.add_field(name='career_stats', value='''
        Returns career averages of a player in general statisitical fields such as points per game, assists per game, et cetera. 
        Requires you to enter the name of the player with proper capitalization. `Stephen Curry` as opposed to `stephen curry`.
        Shortened names for players, such as `Steph Curry`, also won't be accepted.
        For example `gimme career_stats Stephen Curry` would be valid but not `gimme career_stats steph curry`.
        ''', inline=False)
        help_embed.add_field(name='league_standings', value='''
        Returns the league standings for any given season. 
        Requires you to enter the season. For example `1999-00` in that format and the type of season, `RegularSeason` and `PreSeason` respectively.
        For example, `gimme league_standings 1999-00 RegularSeason` would be valid but `gimme league_standings 1999-00 Regular Season` wouldn't be.
        ''', inline=False)
        help_embed.add_field(name='roster', value='''
        Returns the roster for any given team in any given season.
        Requires you to enter the season, for example, `2003-04` in that format, and the full team name respectively. For example, `Toronto Raptors` would work but not `Raptors` or `Toronto`.
        You also have to properly capitalize the team name. `toronto raptors` wouldn't work but `Toronto Raptors` does. 
        For example, `gimme roster 2003-04 Toronto Raptors` would be valid.
        ''', inline=False)
        help_embed.add_field(name='team_stats', value='''
        Returns the general stats for an entire team in any given season. 
        Requires you to enter the season type, then the season, then the full team name.
        For example, `gimme team_stats PreSeason 2003-04 Golden State Warriors` would be valid.
        Requesting data that does not exist, for example playoff data for a team that didn't make the playoffs in any given season, will not return anything.
        ''', inline=False)
        help_embed.add_field(name='season_stats', value='''
        Returns the season stats for a player in any given season.
        Requires you to enter the season type, then the season, then the full name of the player.
        For example, `gimme season_stats RegularSeason 2018-19 Trae Young` would be valid.
        Requesting data that does not exist, for example playoff data for a player that didn't make the playoffs in any given season, will not return anything.
        ''')
        # this command sends a direct message to the user with thorough instructions on how to use each command.

        await author.send(embed=help_embed)

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
    # this is how this discord.py Cog (a type of special class) is able to communicate with the main bot file.
    # this allows the commands to be used from this file despite not being part of the main bot file.