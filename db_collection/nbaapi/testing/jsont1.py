import pandas as pd
from nba_api.stats.endpoints import playergamelog
import json

player = 203076  # Example player ID
season = "2023-24"  # Correct season format

def player_season_stats(player_id, season_id):
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
    
    # Check the raw response before converting to DataFrame
    raw_data = game_log.get_json()  # Raw JSON response



player_stats_df = player_season_stats(player, season)
print(type(player_stats_df))


