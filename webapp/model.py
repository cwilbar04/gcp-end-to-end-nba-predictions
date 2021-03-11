import pandas as pd
from google.cloud import firestore
from google.cloud import bigquery
from datetime import datetime, timezone

def predicted_pointspread(teams):
    try:

        df = pd.DataFrame(teams, index=[0])

        model = df['Model'][0]

        client = bigquery.Client()

        inputs = client.query('''
            SELECT
            input
            FROM
            ML.FEATURE_INFO(MODEL `nba.%s`)
        ''' % (model)).to_dataframe()

        db = firestore.Client()

        home_team_data = db.collection('team_model_data').document(df['HomeTeam'][0]).get().to_dict()
        away_team_data = db.collection('team_model_data').document(df['AwayTeam'][0]).get().to_dict()

        query = f'SELECT predicted_spread FROM ML.PREDICT(MODEL `nba.{model}`, (SELECT '

        for column in inputs.input:
            key = column[9:]
            if column == 'is_home_team':
                query = query + '1 as is_home_team,'
            elif column == 'rest_days_difference':
                home_rest = (datetime.now(timezone.utc) - home_team_data['game_date']).days
                away_rest = (datetime.now(timezone.utc) - away_team_data['game_date']).days
                rest_days_difference = home_rest - away_rest
                query = query + f'{rest_days_difference} as {column},'
            elif column == 'incoming_is_win_streak':
                query = query + f'{home_team_data["streak_counter_is_win"]} as {column},'
            elif (column == 'opponent_incoming_is_win_streak') | (column == 'incoming_is_win_streak_opponent'):
                query = query + f'{away_team_data["streak_counter_is_win"]} as {column},'
            elif column[:12] == 'incoming_wma':
                if column.split('_')[3] == 'opponent':
                    query = query + f'{away_team_data[key]} as {column},'
                else:
                    query = query + f'{away_team_data[key]} as {column},'
            else:
                return f'Error: Model input column {column} not in team data in firestore or not in logic in App Engine. Please try a different model'

        bq_query = query[:-1] + '))'

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
        return f'I predict the {winner} will beat the {loser} by {abs(pointspread)} points using the {model} model!'
    except Exception as e:
        raise ValueError('Sorry, there was a problem processing the data entered... Please try again with different teams') from e