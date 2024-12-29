import pandas as pd
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2, teamgamelog, playergamelog
import time
import seasonstatalt1 

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



# Function to get team stats (offense, defense, etc.)
def get_team_stats(team_id, season_id):
    game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season_id)
    team_stats = game_log.get_data_frame()

    if team_stats.empty:
        return None
    
    # Compute team averages
    team_avg = team_stats.mean(numeric_only=True)
    
    # Add win/loss ratio
    wins = team_stats[team_stats['WL'] == 'W'].shape[0]
    losses = team_stats[team_stats['WL'] == 'L'].shape[0]
    win_loss_ratio = wins / (wins + losses) if (wins + losses) > 0 else None
    team_avg['WIN_LOSS_RATIO'] = win_loss_ratio
    
    return team_avg

# Function to loop through the season and collect data
def collect_season_data(start_date, end_date, season_id):
    all_players_data = []
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    while current_date <= end_date:
        game_date_str = current_date.strftime('%Y-%m-%d')
        print(f"Fetching games for {game_date_str}...")
        
        # Get the games for the current date
        games = get_games_for_date(game_date_str)
        
        # Loop through all games on that date
        for _, game in games.iterrows():
            game_id = game['GAME_ID']
            home_team_id = game['HOME_TEAM_ID']
            visitor_team_id = game['VISITOR_TEAM_ID']
            print(f"Processing game {game_id}...")

            try:
                # Get the box score for the game
                box_score_data = get_box_score_for_game(game_id)

                # Add the game date to the player stats DataFrame
                box_score_data['GAME_DATE'] = game_date_str
                box_score_data['GAME_ID'] = game_id
                
                # Get team stats for both home and visitor teams
                home_team_stats = get_team_stats(home_team_id, season_id)
                visitor_team_stats = get_team_stats(visitor_team_id, season_id)
                
                # Fetch current season stats, last two games average, and last two games vs opponent for each player
                for i, player_row in box_score_data.iterrows():
                    player_id = player_row['PLAYER_ID']
                    team_id = player_row['TEAM_ID']
                    print(f"Fetching stats for player {player_id}...")

                    try:
                        # Get current season stats
                        season_stats = seasonstatalt1.get_player_season_stats(player_id, season_id)

                        # Get last two games average stats
                        last_two_stats = seasonstatalt1.get_player_last_two_games_avg(player_id, season_id)

                        # Get last two games stats against opponent
                        opponent_team_id = visitor_team_id if team_id == home_team_id else home_team_id
                        last_two_against_opponent = seasonstatalt1.get_player_last_two_against_opponent(player_id, opponent_team_id, season_id)
                        
                        # Add season stats to the player's row
                        if season_stats is not None:
                            for stat in season_stats.index:
                                box_score_data.at[i, f'SEASON_{stat}'] = season_stats[stat]

                        # Add last two games stats
                        if last_two_stats is not None:
                            for stat in last_two_stats.index:
                                box_score_data.at[i, f'LAST_2_GAMES_{stat}'] = last_two_stats[stat]

                        # Add last two games vs opponent stats
                        if last_two_against_opponent is not None:
                            for stat in last_two_against_opponent.index:
                                box_score_data.at[i, f'LAST_2_AGAINST_OPPONENT_{stat}'] = last_two_against_opponent[stat]

                        # Add team stats
                        team_stats = home_team_stats if team_id == home_team_id else visitor_team_stats
                        if team_stats is not None:
                            for stat in team_stats.index:
                                box_score_data.at[i, f'TEAM_{stat}'] = team_stats[stat]
                        
                        # Add opponent team stats
                        opponent_team_stats = visitor_team_stats if team_id == home_team_id else home_team_stats
                        if opponent_team_stats is not None:
                            for stat in opponent_team_stats.index:
                                box_score_data.at[i, f'OPPONENT_TEAM_{stat}'] = opponent_team_stats[stat]

                    except Exception as e:
                        print(f"Error fetching stats for player {player_id}: {e}")

                # Append the player stats (with season, team, and opponent stats) to the list
                all_players_data.append(box_score_data)

                # Introduce a delay between requests to avoid rate limiting
                time.sleep(1)
            
            except Exception as e:
                print(f"Error fetching data for game {game_id}: {e}")
        
        # Move to the next day
        current_date += pd.Timedelta(days=1)

    # Combine all players' data into a single DataFrame
    all_players_df = pd.concat(all_players_data, ignore_index=True)
    return all_players_df

# Main function to collect season data
def main():
    start_date = '2023-10-24'  # Example start date (first day of the season)
    end_date = '2024-06-16'     # Example end date (last day of the season)
    season_id = '2023-24'       # Example season ID (2023-24 season)
    
    all_players_df = collect_season_data(start_date, end_date, season_id)
    
    # Save to CSV or process the DataFrame as needed
    all_players_df.to_csv('nba_player_stats_with_full_data_2023_2024.csv', index=False)
    print("Data collection complete. Saved to 'nba_player_stats_with_full_data_2023_2024.csv'.")

if __name__ == "__main__":
    main()
