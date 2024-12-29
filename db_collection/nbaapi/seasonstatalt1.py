from nba_api.stats.endpoints import playercareerstats, playergamelog
import pandas as pd
from nba_api.stats.static import teams
import requests
import numpy as np
import pandas as pd

def get_team_abbreviation(team_id):
    all_teams = teams.get_teams()  # Get all teams
    for team in all_teams:
        if team['id'] == team_id:
            return team['abbreviation']
    return None



# Function to get a player's current season stats up to a specific game date
def get_player_season_stats(player_id, season_id):
    
 
    
    career = playercareerstats.PlayerCareerStats(player_id)
    c = career.get_data_frames()[0]
    #spec = c[(c['SEASON_ID'] == season_id)]
    return(c)

    

# Function to get the player's last 2 games average stats
def get_player_last_two_games_avg(player_id, season_id):
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
    player_stats = game_log.get_data_frames()[0]
    
    # Check if player has played at least two games
    if len(player_stats) < 2:
        return None
    
    # Take the stats from the last 2 games
    last_two_games = player_stats.head(2)
    
    # Compute average over last 2 games
    last_two_avg = last_two_games.mean(numeric_only=True)
    return last_two_avg


# Function to get a player's last 2 games stats against a specific team
def get_player_last_two_against_opponent(player_id, opponent_team_id, season_id):
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
    player_stats = game_log.get_data_frames()[0]
    
    mat = get_team_abbreviation(opponent_team_id)

    # Filter games where the player faced the opponent team
    opponent_games = player_stats[player_stats['MATCHUP'].str.contains(mat)]

    # Check if player has played at least two games against the opponent
    if opponent_games.shape[0] < 1:
        
        return None

    # Take the stats from the last 2 games against the opponent
    last_two_against_opponent = opponent_games.head(2)

    # Compute average over those two games
    last_two_opponent_avg = last_two_against_opponent.mean(numeric_only=True)
    return player_stats



player_id = 203076 
opponent_team_id = 1610612738
season_id = "2023-24"


print(get_player_season_stats(player_id,season_id))