import pandas as pd

df = pd.read_csv('first.csv')

df = df.drop(columns=['COMMENT','RECENT_SEASON_ID', 'RECENT_Game_ID','RECENT_GAME_DATE', 'RECENT_MATCHUP', 'RECENT_WL'  ])

df_cleaned = df.dropna(how="any")

df_cleaned.to_csv('cleaned.csv', index=False)