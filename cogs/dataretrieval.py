"""
This is the library from which the main bot file will access all the commands that relate to retrieving the NBA data from the NBA API.
"""

# Futures
import discord
from discord.ext import commands
# imports the discord.py library 

import gspread
import oauth2client
from oauth2client.service_account import ServiceAccountCredentials
# imports the Google Sheets API 

from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import teamdashboardbygeneralsplits
from nba_api.stats.endpoints import playerdashboardbygeneralsplits
from nba_api.stats.endpoints import leaguestandings
# imports the libraries from which the data will be acquired
# "from nba_api.stats.endpoints import *" does not work, hence why I imported each module individually

from nba_api.stats.library.parameters import SeasonTypeAllStar
# imports the SeasonTypeAllStar class, which will be used in a few commands 

import pandas as pd
# imports the Pandas library, which enables the program to manipulate DataFrames in which the data is stored

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("nba_db").sheet1
# Gives the Google Sheets API access to the "nba_db" spreadsheet that is in the Google Drive of my personal account.
# This is where the all of the ID numbers for every player in league history and every team in the league is stored. 

class DataRetrieval(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    # initializes the class whenever it is called
    # class can't work without __init__ function

    @commands.command()
    async def player_info(self, ctx, *, object_search):
        
        try:
            object_row = (sheet.find(object_search).row)
            object_column = (sheet.find(object_search).col)
            # finds the coordinates of the cell containing the player name
            object_id = sheet.cell(object_row,object_column-1).value
            # assigns the data in the cell to the left of the player name as a variable 
            # this is the ID itself
            object_id = str(object_id)
            # NBA API cannot read the ID unless it's in string form

            player_info = commonplayerinfo.CommonPlayerInfo(player_id=object_id)

            df_player_info = player_info.get_data_frames()
            # Data appended to a DataFrame, from which it can easily be extracted

            t_id = df_player_info[0].iat[0,16]
            to_year = df_player_info[0].iat[0,23]

            jersey_number = df_player_info[0].iat[0,13]
            position = df_player_info[0].iat[0,14]
            height = df_player_info[0].iat[0,10]
            weight = df_player_info[0].iat[0,11]
        
            date_of_birth = df_player_info[0].iat[0,6]
            date_of_birth = date_of_birth.rstrip('T00:00:00')

            draft_position = df_player_info[0].iat[0,29]
            draft_round = df_player_info[0].iat[0,28]
            # Pulled various pieces of data regarding the player 
            # These will later be used by the bot 

            player_embed = discord.Embed(
            title = object_search,
            colour = discord.Colour(0x0e1cf5)
            ) 

            player_embed.set_footer(text='gimme help | RIP Kobe')
            player_embed.set_image(url='https://cdn.vox-cdn.com/thumbor/v1jR5XEgcDrnwTq_uSZt4ApiIqg=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/20025173/nba_covid_3_ringer_illo.jpg')
            player_embed.set_thumbnail(url=f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{t_id}/{to_year}/260x190/{object_id}.png')
            # thumbnail is used to display the player picture

            player_embed.set_author(name=f'Player info for `{object_search}')
            player_embed.add_field(name='Jersey Number', value=jersey_number)
            player_embed.add_field(name='Position', value=position)
            player_embed.add_field(name='Height', value=height)
            player_embed.add_field(name='Weight', value=f'{weight} lbs')
            player_embed.add_field(name='Date of Birth', value=date_of_birth)
            player_embed.add_field(name='Drafted', value=f'Round: {draft_round} Pick: {draft_position}')
            # all data is added to embedded message to be more visually appealing 
            
            await ctx.send(embed=player_embed)

        except (UnboundLocalError, gspread.exceptions.CellNotFound):
            await ctx.send("""
            I think you spelled it wrong hombre, make sure you're using this format: `gimme player_info Steph Curry`.
            Also, make sure you're not using shortened versions of names like `Steph Curry`.
            """)
        # The "try" and "except" run the code and look out for errors. 
        # If one of the listed errors is raised, then it runs the alternative code
        
    @commands.command()
    async def career_stats(self, ctx, *, object_search):

        try:
            object_row = (sheet.find(object_search).row)
            object_column = (sheet.find(object_search).col)

            object_id = sheet.cell(object_row,object_column-1).value

            object_id = str(object_id)

            career_stats = playercareerstats.PlayerCareerStats(player_id=object_id)

            df_career_stats = career_stats.get_data_frames()

            career_totals = df_career_stats[1].sum()
            # same process as before but this time all the columns are added up to later find career averages
            
            def get_per_game(metric):
                return round((career_totals.get(f'{metric}') / career_totals.get('GP')), 1)

            def get_percent(metric, attemped_metric):
                return round((career_totals.get(f'{metric}') / career_totals.get(f'{attemped_metric}') * 100), 1)
            # these functions calculate per-game stats and field goal efficiences respectively

            career_ppg = get_per_game('PTS')
            career_fgp = get_percent('FGM', 'FGA')
            career_tpp = get_percent('FG3M', 'FG3A')
            career_ftp = get_percent('FTM', 'FTA')
            career_rpg = get_per_game('REB')
            career_apg = get_per_game('AST')
            career_spg = get_per_game('STL')
            career_bpg = get_per_game('BLK')
            career_tpg = get_per_game('TOV')
            # all major stats are stored as variables to be used in embedded message later

            career_stats_embed = discord.Embed(
                title = object_search,
                colour = discord.Colour(0x0e1cf5)
            ) 

            player_info = commonplayerinfo.CommonPlayerInfo(player_id=object_id)

            df_player_info = player_info.get_data_frames()

            t_id = df_player_info[0].iat[0,16]
            to_year = df_player_info[0].iat[0,23]
            # this data is only being pulled for the sake of finding the player's picture for the thumbnail

            career_stats_embed.set_footer(text='gimme help | RIP Kobe')
            career_stats_embed.set_image(url='https://cdn.vox-cdn.com/thumbor/v1jR5XEgcDrnwTq_uSZt4ApiIqg=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/20025173/nba_covid_3_ringer_illo.jpg')
            career_stats_embed.set_thumbnail(url=f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{t_id}/{to_year}/260x190/{object_id}.png')

            career_stats_embed.set_author(name=f'Career stat averages for `{object_search}')
            career_stats_embed.add_field(name='PPG', value=career_ppg)
            career_stats_embed.add_field(name='FG%', value=f'{career_fgp}%')
            career_stats_embed.add_field(name='3P%', value=f'{career_tpp}%')
            career_stats_embed.add_field(name='FT%', value=f'{career_ftp}%')
            career_stats_embed.add_field(name='RPG', value=career_rpg)
            career_stats_embed.add_field(name='APG', value=career_apg)
            career_stats_embed.add_field(name='SPG', value=career_spg)
            career_stats_embed.add_field(name='BPG', value=career_bpg)
            career_stats_embed.add_field(name='TPG', value=career_tpg)
            # career stat averages added embedded message

            await ctx.send(embed=career_stats_embed)

        except (UnboundLocalError, gspread.exceptions.CellNotFound):
            await ctx.send("""
            I think you spelled it wrong hombre, make sure you're using this format: `gimme career_stats Steph Curry`.
            Also, make sure you're not using shortened versions of names like `Steph Curry`.
            """)

    @commands.command()
    async def roster(self, ctx, season_year, *, object_search):

        try:
            object_row = (sheet.find(object_search).row)
            object_column = (sheet.find(object_search).col)

            object_id = sheet.cell(object_row,object_column-1).value

            object_id = str(object_id)

            team_roster = commonteamroster.CommonTeamRoster(season=season_year, team_id=object_id)

            df_team_roster = team_roster.get_data_frames()
            # ID found and roster data found

            roster_player_name = df_team_roster[0]['PLAYER'].to_string(index=False)
            jersey_number = df_team_roster[0]['NUM'].to_string(index=False)
            player_position = df_team_roster[0]['POSITION'].to_string(index=False)
            # columns converted to strings so that they display in one large column in embedd message
            # embedd message limited in that they don't have table functionality and can only take 3 columns before formatting poorly

            roster_embed = discord.Embed(
                title = (f'{season_year} Roster for the {object_search}'),
                colour = discord.Colour(0x0e1cf5)
            )

            roster_embed.set_footer(text='gimme help | RIP Kobe')
            roster_embed.set_image(url='https://cdn.vox-cdn.com/thumbor/v1jR5XEgcDrnwTq_uSZt4ApiIqg=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/20025173/nba_covid_3_ringer_illo.jpg')

            roster_embed.set_author(name=f'Roster for the {season_year} {object_search}')
            roster_embed.add_field(name='Players', value=roster_player_name)
            roster_embed.add_field(name='Jersey #', value=jersey_number)
            roster_embed.add_field(name='Position', value=player_position)

            await ctx.send(embed=roster_embed)
            # once again, value of variables added to embedded message and sent to chat

        except (UnboundLocalError, gspread.exceptions.CellNotFound):
            await ctx.send("""
            I think you spelled it wrong hombre, make sure you're using this format: `gimme roster Toronto Raptors`.
            Also, make sure you're not using shortened versions of names like `Raptors`, `Toronto`, or `TOR`.
            """)

    @commands.command()
    async def team_stats(self, ctx, season_type, season_year, *, object_search):

        try:
            if season_type == ("RegularSeason"):
                season_type = SeasonTypeAllStar.regular
            elif season_type == ("PreSeason"):
                season_type = SeasonTypeAllStar.preseason
            elif season_type == ("Playoffs"):
                season_type == SeasonTypeAllStar.playoffs
            # Had issues with using the user input itself as a variable so had to use a conditional statement approach.

            object_row = (sheet.find(object_search).row)
            object_column = (sheet.find(object_search).col)

            object_id = sheet.cell(object_row,object_column-1).value

            object_id = str(object_id)

            stats_team = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(last_n_games=0, 
                measure_type_detailed_defense='Base', 
                month=0, 
                opponent_team_id=0, 
                pace_adjust='N',
                per_mode_detailed='PerGame',
                period=0,
                plus_minus='N',
                rank='N',
                season=season_year,
                season_type_all_star=season_type,
                team_id=object_id)

            df_stats_team = stats_team.get_data_frames()

            team_ppg = df_stats_team[0].iat[0,27]
            team_fgp = df_stats_team[0].iat[0,10]
            team_tpp = df_stats_team[0].iat[0,13]
            team_ftp = df_stats_team[0].iat[0,16]
            team_rpg = df_stats_team[0].iat[0,19]
            team_apg = df_stats_team[0].iat[0,20]
            team_spg = df_stats_team[0].iat[0,22]
            team_bpg = df_stats_team[0].iat[0,23]
            team_tpg = df_stats_team[0].iat[0,21]

            stats_team_embed = discord.Embed(
                title = (f'Team Stats for the {object_search}'),
                colour = discord.Colour(0x0e1cf5)
            )

            stats_team_embed.set_footer(text='gimme help | RIP Kobe')
            stats_team_embed.set_image(url='https://cdn.vox-cdn.com/thumbor/v1jR5XEgcDrnwTq_uSZt4ApiIqg=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/20025173/nba_covid_3_ringer_illo.jpg')

            stats_team_embed.set_author(name=f'{season_type} stats for the {season_year} {object_search}')
            stats_team_embed.add_field(name='PPG', value=team_ppg)
            stats_team_embed.add_field(name='FG%', value=f'{round((team_fgp * 100), 1)}%')
            stats_team_embed.add_field(name='3P%', value=f'{round((team_tpp * 100), 1)}%')
            stats_team_embed.add_field(name='FT%', value=f'{round((team_ftp * 100), 1)}%')
            stats_team_embed.add_field(name='RPG', value=team_rpg)
            stats_team_embed.add_field(name='APG', value=team_apg)
            stats_team_embed.add_field(name='SPG', value=team_spg)
            stats_team_embed.add_field(name='BPG', value=team_bpg)
            stats_team_embed.add_field(name='TPG', value=team_tpg)

            await ctx.send(embed=stats_team_embed)
            # With discord.py's implementation of classes, creating a function that would cut down the amount of code proved to be oddly difficult and not worth the time. 
        except (UnboundLocalError, gspread.exceptions.CellNotFound):
            await ctx.send("""
            I think you spelled it wrong hombre, make sure you're using this format: `gimme team_stats RegularSeason 2013-14 Toronto Raptors`.
            Also, make sure you're not using shortened versions of names like `Raptors`, `Toronto`, or `TOR`.
            """)

    @commands.command()
    async def season_stats(self, ctx, season_type, season_year, *, object_search):
        try:
            if season_type == ("RegularSeason"):
                season_type = SeasonTypeAllStar.regular
            elif season_type == ("PreSeason"):
                season_type = SeasonTypeAllStar.preseason
            elif season_type == ("Playoffs"):
                season_type == SeasonTypeAllStar.playoffs

            object_row = (sheet.find(object_search).row)
            object_column = (sheet.find(object_search).col)

            object_id = sheet.cell(object_row,object_column-1).value

            object_id = str(object_id)

            stats_player = playerdashboardbygeneralsplits.PlayerDashboardByGeneralSplits(last_n_games=0, 
                measure_type_detailed='Base', 
                month=0, 
                opponent_team_id=0, 
                pace_adjust='N',
                per_mode_detailed='PerGame',
                period=0,
                plus_minus='N',
                rank='N',
                season=season_year,
                season_type_playoffs=season_type,
                player_id=object_id)

            df_stats_player = stats_player.get_data_frames()

            t_id = df_stats_player[0].iat[0,16]
            to_year = df_stats_player[0].iat[0,23]

            player_ppg = df_stats_player[0].iat[0,26]
            player_fgp = df_stats_player[0].iat[0,9]
            player_tpp = df_stats_player[0].iat[0,12]
            player_ftp = df_stats_player[0].iat[0,15]
            player_rpg = df_stats_player[0].iat[0,18]
            player_apg = df_stats_player[0].iat[0,19]
            player_spg = df_stats_player[0].iat[0,21]
            player_bpg = df_stats_player[0].iat[0,22]
            player_tpg = df_stats_player[0].iat[0,20]

            stats_player_embed = discord.Embed(
                title = (f'{object_search} stats for the {season_year} season.'),
                colour = discord.Colour(0x0e1cf5)
            )

            stats_player_embed.set_footer(text='gimme help | RIP Kobe')
            stats_player_embed.set_image(url='https://cdn.vox-cdn.com/thumbor/v1jR5XEgcDrnwTq_uSZt4ApiIqg=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/20025173/nba_covid_3_ringer_illo.jpg')
            stats_player_embed.set_thumbnail(url=f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{t_id}/{to_year}/260x190/{object_id}.png')

            stats_player_embed.add_field(name='PPG', value=player_ppg)
            stats_player_embed.add_field(name='FG%', value=f'{round((player_fgp * 100), 1)}%')
            stats_player_embed.add_field(name='3P%', value=f'{round((player_tpp * 100), 1)}%')
            stats_player_embed.add_field(name='FT%', value=f'{round((player_ftp * 100), 1)}%')
            stats_player_embed.add_field(name='RPG', value=player_rpg)
            stats_player_embed.add_field(name='APG', value=player_apg)
            stats_player_embed.add_field(name='SPG', value=player_spg)
            stats_player_embed.add_field(name='BPG', value=player_bpg)
            stats_player_embed.add_field(name='TPG', value=player_tpg)    

            await ctx.send(embed=stats_player_embed)
        except (UnboundLocalError, gspread.exceptions.CellNotFound):
            await ctx.send("""
            I think you spelled it wrong hombre, make sure you're using this format: `gimme season_stats RegularSeason 2013-14 Stephen Curry`.
            Also, make sure you're not using shortened versions of names like `Steph Curry`.
            """)

    @commands.command()
    async def league_standings(self, ctx, season_year, type_of_season):

        try:
            if type_of_season == ("RegularSeason"):
                type_of_season = SeasonTypeAllStar.regular
            elif type_of_season == ("PreSeason"):
                type_of_season = SeasonTypeAllStar.preseason

            league_table = leaguestandings.LeagueStandings(league_id='00', season=season_year, season_type=type_of_season)

            df_league_table = league_table.get_data_frames()

            organized_standings = (df_league_table[0].sort_values('WinPCT', ascending=False))

            team_names = organized_standings['TeamName'].to_string(index=False)
            team_records = organized_standings['Record'].to_string(index=False)
            win_percentage = organized_standings['WinPCT'].to_string(index=False) 

            league_standings_embed = discord.Embed(
                title = (f'Standings for the {season_year} {type_of_season}'),
                colour = discord.Colour(0x0e1cf5)
            )

            league_standings_embed.set_footer(text='gimme help | RIP Kobe')
            league_standings_embed.set_image(url='https://cdn.vox-cdn.com/thumbor/v1jR5XEgcDrnwTq_uSZt4ApiIqg=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/20025173/nba_covid_3_ringer_illo.jpg')

            league_standings_embed.set_author(name=f'{type_of_season} standings for the {season_year} season.')
            league_standings_embed.add_field(name='Teams', value=team_names)
            league_standings_embed.add_field(name='Record', value=team_records)
            league_standings_embed.add_field(name='Win PCT', value=win_percentage)

            await ctx.send(embed=league_standings_embed)
        except (UnboundLocalError, gspread.exceptions.CellNotFound):
            await ctx.send("""
            I think you spelled it wrong hombre, make sure you're using this format: `gimme league_standings 2003-04 RegularSeason`.
            """)

def setup(bot):
    bot.add_cog(DataRetrieval(bot))
    # this is how this discord.py Cog (a type of special class) is able to communicate with the main bot file 
    # this allows the commands to be used from this file despite not being part of the main bot file.