from nba_api.stats.endpoints import playercareerstats, playergamelog, teamdashboardbygeneralsplits, scoreboardv2, boxscoretraditionalv2
import pandas as pd
from nba_api.stats.static import teams
import requests
import numpy as np
import pandas as pd
import json
from datetime import date
import trial
import time


today = date.today()
team = "DEN"

player_id = 203999 #jokic
season_id = "2023-24"
team_id = 1610612738 
matchup = "DEN"

# Function to get all games for a specific date
def get_games_for_date(game_date):
    scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
    games = scoreboard.game_header.get_data_frame()
    return games

# Function to get box score for a specific game
def get_box_score_for_game(game_id):
    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    player_stats = boxscore.player_stats.get_data_frame()
    return player_stats

#get abbreviation for id
def get_abbreviation(id):
    nba_teams = teams.get_teams()

    # Create a mapping of team IDs to abbreviations
    team_id_to_abbreviation = {team['id']: team['abbreviation'] for team in nba_teams}  
    return team_id_to_abbreviation.get(id, 'Unknown')

"""def tenner():
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season_id)
    player_stats = game_log.get_data_frames()[0]
    player_stats['MATCHUP'] = player_stats['MATCHUP'].str.replace(team+' @ ', "")
    player_stats['MATCHUP'] = player_stats['MATCHUP'].str.replace(team+' vs. ', "")
    filtered = player_stats[player_stats['MATCHUP'] == matchup]
    print(player_stats)"""
    
def collect_season_data(start_date, end_date, season_id):
    all_players_data = []
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    while current_date <= end_date:                                          #iterate though dates
        game_date_str = current_date.strftime('%Y-%m-%d')
        print(f"Fetching games for {game_date_str}...")
        
        # Get the games for the current date
        games = get_games_for_date(game_date_str)
        
        # Loop through all games on that date
        for game in games.iterrows():                                       #iterate though games on date
            
            game_id = game[1]['GAME_ID']
            
            home_team_id = game[1]['HOME_TEAM_ID']
            home = get_abbreviation(home_team_id)
            
            visitor_team_id = game[1]['VISITOR_TEAM_ID']
            visitor = get_abbreviation(visitor_team_id)
            
            #collect team stats
            home_team_stats = trial.get_team_stats(home_team_id,season_id)
            visitor_team_stats = trial.get_team_stats(visitor_team_id, season_id)
            
            #message
            print("GAMEGAMEGAMEGAME ")
            print(visitor )
            print(home)
            #
            
            box_score_data = get_box_score_for_game(game_id)
            
            for i, player_row in box_score_data.iterrows():                #iterate though players in this game
                #
                pid = player_row['PLAYER_ID']
                tid = player_row['TEAM_ID']
                #print(player_row.to_frame().T)
                print('adding player...')
                #
                
                #get historical data for player i
                
                #season averages
                season_stats = trial.get_player_season_stats(pid, season_id)
                print('stats passed')
                
                #recent averages
                recent_stats = trial.get_recent_performance(pid, season_id, current_date)
                print('recent passed')
                
                #team averages
                if tid == home_team_id:
                    team_stats = home_team_stats
                    opponent_team_stats = visitor_team_stats
                else:
                    team_stats = visitor_team_stats
                    opponent_team_stats = home_team_stats
                print('teams passed')
                    
                #average against opponent
                team = home if tid == home_team_id else visitor
                opponent = home if tid == visitor_team_id else home
                stats_against_opp = trial.get_recent_against_team(pid, season_id, current_date, team, opponent )
                print('against opp passed')
                
                
                #add season averages
                for stat in season_stats.columns:
                    print(stat)
                    box_score_data.at[i, f'SEASON_{stat}'] = season_stats.loc[season_stats.index[0],stat]
                print('add stat passed')
                    
                #add recent averages
                for stat in recent_stats.columns:
                    print(stat)
                    box_score_data.at[i, f'RECENT_{stat}'] = recent_stats.loc[recent_stats.index[0],stat]
                print('add recent passed')
                    
                #add team averages
                for stat in team_stats.columns:
                    print(stat)
                    box_score_data.at[i,f'TEAM_{stat}'] = team_stats.loc[team_stats.index[0],stat]
                print('add team passed')
                
                #add opponent team averages
                for stat in opponent_team_stats.columns:
                    box_score_data.at[i,f'OPPONENT_{stat}'] = opponent_team_stats.loc[opponent_team_stats.index[0],stat]
                print('add opp passed')
                    
                #add averages against opponent
                for stat in stats_against_opp.columns:
                    print(stat)
                    box_score_data.at[i,f'AGAINT_OPP_{stat}'] = stats_against_opp.loc[stats_against_opp.index[0],stat]
                print('add against opp passed')    
                time.sleep(4)
            
                
                    
            #append player performances and data from this game
            all_players_data.append(box_score_data)
            #break
            
            # sleep to avoid rate limiting
            time.sleep(1)
            
        #increment day
        current_date += pd.Timedelta(days=1)
        
    #combine into single dataframe  
    all_player_final = pd.concat(all_players_data, ignore_index=True)
    return all_player_final
                    


all_players_df = collect_season_data('2024-3-05','2024-3-05',season_id)
    
 # Save to CSV or process the DataFrame as needed
all_players_df.to_csv('nba_player_stats_with_full_data_2023_2024.csv', index=False)
print("Data collection complete. Saved to 'nba_player_stats_with_full_data_2023_2024.csv'.")


# Main function to collect season data
"""def main():
    start_date = '2023-10-24'  # Example start date (first day of the season)
    end_date = '2024-06-16'     # Example end date (last day of the season)
    season_id = '2023-24'       # Example season ID (2023-24 season)
    
    all_players_df = collect_season_data(start_date, end_date, season_id)
    
    # Save to CSV or process the DataFrame as needed
    all_players_df.to_csv('nba_player_stats_with_full_data_2023_2024.csv', index=False)
    print("Data collection complete. Saved to 'nba_player_stats_with_full_data_2023_2024.csv'.")

if __name__ == "__main__":
    main()"""