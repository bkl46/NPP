from nba_api.stats.endpoints import playercareerstats, playergamelog, teamdashboardbygeneralsplits
import pandas as pd
from nba_api.stats.static import teams
import requests
import numpy as np
import pandas as pd
import json
from datetime import date

tod = date.today().strftime("%Y-%m-%d")

# Function to get a player's current season stats up to a specific game date
def get_player_season_stats(player_id, season_id):
    career = playercareerstats.PlayerCareerStats(player_id).get_data_frames()[0]
    spec = career[(career['SEASON_ID'] == season_id)]
    return(spec)

#function to get a team's stats, takes team id
def get_team_stats(id,season):
    team_stats = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(
        team_id=id, season=season, season_type_all_star='Regular Season')

    # Step 3: Convert to pandas DataFrame
    overall_team_stats = team_stats.overall_team_dashboard.get_data_frame()
    return overall_team_stats

#function to get a player's performance from the last two games
def get_recent_performance(player_id, season_id,date):
    #get game log
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
    player_stats = game_log.get_data_frames()[0]
    
    #convert date to date object to allow for filtering by date
    player_stats['GAME_DATE'] = pd.to_datetime(player_stats['GAME_DATE'])
    #filter games to be before given date
    filtered_games = player_stats[player_stats['GAME_DATE'] < date]
    
    # Check if player has played at least two games
    if len(filtered_games) < 2:
        return filtered_games
    
    # Take the stats from the last 2 games
    last_two_games = filtered_games.head(2)
    
    # Compute average over last 2 games
    last_two_avg = last_two_games.mean(numeric_only=True)
    return last_two_avg.to_frame().T

#function to get a player's recent performance against a specific team, takes player id and team abbreviations
def get_recent_against_team(player_id, season_id, date, team, opponent):
    #get game log
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
    player_stats = game_log.get_data_frames()[0]
    
    #convert date to date object to allow for filtering by date
    player_stats['GAME_DATE'] = pd.to_datetime(player_stats['GAME_DATE'])
    #filter games to be before given date
    filtered_games = player_stats[player_stats['GAME_DATE'] < date]
    
    filtered_games.loc[:,'MATCHUP'] = filtered_games['MATCHUP'].str.replace(team+' @ ', "")
    filtered_games.loc[:,'MATCHUP'] = filtered_games['MATCHUP'].str.replace(team+' vs. ', "")
    filtered = filtered_games[filtered_games['MATCHUP'] == opponent]
    
    # Take the stats from the last 2 games
    #last_two_games = filtered.head(2)
    
    # Compute average over last 2 games
    avg = filtered.mean(numeric_only=True)
    return avg.to_frame().T
    


player_id = 203999 #jokic
season_id = "2023-24"
team_id = 1610612738 


#print(get_recent_performance(player_id,season_id,tod))
#print(get_player_season_stats(player_id,season_id).index[0])
#print(get_team_stats(team_id,season_id).T)
#game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
#player_stats = game_log.get_data_frames()[0]
#player_stats['GAME_DATE'] = pd.to_datetime(player_stats['GAME_DATE'],  errors='coerce')
#print(player_stats.head())
