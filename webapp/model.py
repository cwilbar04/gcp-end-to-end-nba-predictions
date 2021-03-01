import pandas as pd
import numpy as np
from google.cloud import firestore
from google.cloud import bigquery

def predicted_pointspread(teams):
    try:
        df = pd.DataFrame(teams, index=[0])


        db = firestore.Client()

        home_team_data = db.collection('team_model_data').document(df['HomeTeam'][0]).get().to_dict()
        away_team_data = db.collection('team_model_data').document(df['AwayTeam'][0]).get().to_dict()

        query = 'SELECT predicted_spread FROM ML.PREDICT(MODEL `nba.automl_regression`, (SELECT 1 as is_home_team,'
        for key in home_team_data.keys():
            if key == 'streak_counter_is_win':
                query = query + f'{home_team_data[key]} as incoming_is_win_streak,'
            elif key not in ['season', 'game_date']:
                query = query + f'{home_team_data[key]} as incoming_{key},'
        for key in away_team_data.keys():
            if key not in ['season', 'game_date', 'streak_counter_is_win']:
                query = query + f'{away_team_data[key]} as incoming_opponent_{key},'

        bq_query = query[:-1] + '))'

        client = bigquery.Client()

        game_bq = client.query('''
        %s
        ''' % (bq_query))

        game = game_bq.to_dataframe()

        pointspread = round(game['predicted_spread'][0],1)

        if pointspread > 0:
            winner = df['HomeTeam'][0]
            loser = df['AwayTeam'][0]
        else:
            winner = df['AwayTeam'][0]
            loser = df['HomeTeam'][0]
        return f'I predict the {winner} will beat the {loser} by {abs(pointspread)} points!'
    except Exception as e:
        raise ValueError('Sorry, there was a problem processing the data entered... Please try again with different teams') from e