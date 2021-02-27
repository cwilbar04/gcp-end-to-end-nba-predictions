import pandas as pd
import numpy as np
from google.cloud import bigquery
import os

## Insert initial setup in entry point function: create_model_data

def convert_to_seconds(x):
    sp = int(x.split(':')[0]) * 60 + int(x.split(':')[1])
    return sp

def switch_key(key):
    new_key = key[:-1] + ('h' if key[-1] == 'a' else 'a')
    return new_key

def generate_streak_info(data,column):
    """
    Parameters
    ----------
    data:
      Dataframe with a specific column to generate streak data

    column:
      Stirng with specific column name to generate streak info

    Returns
    -------

    data_with_streak_counter:
        The original dataframe with a new column
        `streak_counter_[column]` containing integers with 
        counts for each streak.
    """
    
    data['start_of_streak'] = data[column].ne(data[column].shift())
    data['streak_id'] = data.start_of_streak.cumsum()
    data[f'streak_counter_{column}'] = data.groupby('streak_id').cumcount() + 1
    data_with_streak_counter = data.drop(columns = ['start_of_streak','streak_id'] )
    return data_with_streak_counter

def create_linear_weighted_moving_average(data,column,W):
    """
    Parameters
    ----------
    data:
      Dataframe with a specific column to generate weighted moving average.

    column:
      Stirng with specific column name to generate weighted moving average info.
      Column must be ready to be converted to float data type.

    Returns
    -------

    data_with_moving_average:
        The original dataframe with a new column
        `wma_[W]_[column]` containing float values with weighted moving average
        values for the provided value with a weight of W.
    """  
    data_with_moving_average = data.copy()
    data_with_moving_average[column] = data_with_moving_average[column].astype(float)
    weights = np.arange(1,W+1)
    data_with_moving_average[f'wma_{W}_{column}'] = data_with_moving_average[column].rolling(W).apply(lambda col: np.dot(col, weights)/weights.sum(), raw=True)
    return data_with_moving_average

def create_model_data(request):
    
 
    request_json = request.get_json()
    if request_json:
        print("Payload ignored. This function does not use a payload")
    
    
    ## Setup
    my_project_id = os.environ.get('GCP_PROJECT')
    client = bigquery.Client(project=my_project_id)
    raw_game_data_table = 'nba.raw_basketballreference_game'
    raw_player_data_table = 'nba.raw_basketballreference_playerbox'
    model_table_name = 'nba.model_game'

    # Enter columns to created linearly weighted moving average calculations and number of periods to use
    wma_columns = ['pace',
        'efg_pct', 'tov_pct', 'ft_rate', 'off_rtg',
        'opponent_efg_pct', 'opponent_tov_pct', 'opponent_ft_rate',
        'opponent_off_rtg', 'starter_minutes_played_proportion',
        'bench_plus_minus', 'opponnent_starter_minutes_played_proportion',
        'opponent_bench_plus_minus']
    W = 10
    
    ## Load tables to dataframe
    game = client.query('''
    SELECT
        *
    FROM
        `%s`
    ''' % (raw_game_data_table)).to_dataframe()

    player = client.query('''
    SELECT
        *
    FROM
        `%s`
    ''' % (raw_player_data_table)).to_dataframe()

    ## Create game variables needed for model
    game['home_spread'] = game['home_pts'].astype(int) - game['visitor_pts'].astype(int)
    game['season'] = ''
    for i in range(len(game)):
        if ((game['game_date'][i].year != 2020 and game['game_date'][i].month < 7) or (game['game_date'][i].year == 2020 and game['game_date'][i].month < 11)):
            game.loc[i,'season'] = game['game_date'][i].year
        else:
            game.loc[i,'season'] = game['game_date'][i].year + 1


    ## Create game by team variables - stack home and away to team vs. opponent
    games_by_team_home = pd.DataFrame()
    games_by_team_home['season'] = game['season']
    games_by_team_home['game_key'] = game['game_key'] + 'h'
    games_by_team_home['game_date'] = pd.to_datetime(game['game_date'])
    games_by_team_home['team'] = game['home_team_name']
    games_by_team_home['opponent'] = game['visitor_team_name']
    games_by_team_home['is_home_team'] = 1
    games_by_team_home['spread'] = game['home_spread']
    games_by_team_home['pace'] = game['h_ff_pace']
    games_by_team_home['efg_pct'] = game['h_ff_efg_pct']
    games_by_team_home['tov_pct'] = game['h_ff_tov_pct']
    games_by_team_home['ft_rate'] = game['h_ff_ft_rate']
    games_by_team_home['off_rtg'] = game['h_ff_off_rtg']
    games_by_team_home['opponent_efg_pct'] = game['a_ff_efg_pct']
    games_by_team_home['opponent_tov_pct'] = game['a_ff_tov_pct']
    games_by_team_home['opponent_ft_rate'] = game['a_ff_ft_rate']
    games_by_team_home['opponent_off_rtg'] = game['a_ff_off_rtg']


    games_by_team_home['is_win'] = ''
    for i in range(len(game)):
        games_by_team_home.loc[i,'is_win'] = 1 if game['home_spread'][i].astype(int) > 0 else 0


    games_by_team_visitor = pd.DataFrame()
    games_by_team_visitor ['season'] = game['season']
    games_by_team_visitor ['game_key'] = game['game_key'] + 'a'
    games_by_team_visitor ['game_date'] = pd.to_datetime(game['game_date'])
    games_by_team_visitor ['team'] = game['visitor_team_name']
    games_by_team_visitor ['opponent'] = game['home_team_name']
    games_by_team_visitor ['is_home_team'] = 0
    games_by_team_visitor ['spread'] = game['home_spread']*-1
    games_by_team_visitor ['pace'] = game['a_ff_pace']
    games_by_team_visitor ['efg_pct'] = game['a_ff_efg_pct']
    games_by_team_visitor ['tov_pct'] = game['a_ff_tov_pct']
    games_by_team_visitor ['ft_rate'] = game['a_ff_ft_rate']
    games_by_team_visitor ['off_rtg'] = game['a_ff_off_rtg']
    games_by_team_visitor['opponent_efg_pct'] = game['h_ff_efg_pct']
    games_by_team_visitor['opponent_tov_pct'] = game['h_ff_tov_pct']
    games_by_team_visitor['opponent_ft_rate'] = game['h_ff_ft_rate']
    games_by_team_visitor['opponent_off_rtg'] = game['h_ff_off_rtg']

    games_by_team_visitor['is_win'] = ''
    for i in range(len(game)):
        games_by_team_visitor.loc[i,'is_win'] = 1 if game['home_spread'][i].astype(int) < 0 else 0

    games_by_team = pd.concat([games_by_team_home,games_by_team_visitor])
    games_by_team.set_index('game_key', inplace=True)

    ## Create player variables needed for model
    # Make game key unique per home/away team
    player['game_key'] = player['game_key'] + player['h_or_a']

    #Only include players that actually played
    player = player.dropna(subset=['mp', 'plus_minus']).reset_index(drop=True)

    player['plus_minus'] = player['plus_minus'].astype(int)
    player['seconds_played'] = player['mp'].apply(convert_to_seconds)

    ## Create dataframe for aggregated player stats per game
    game_player_stats = pd.DataFrame()
    game_player_stats['game_key'] = player['game_key'].unique()

    total_seconds = player.groupby(['game_key'])['seconds_played'].sum()
    starter_seconds = player[player['starter_flag']==True].groupby(['game_key'])['seconds_played'].sum()
    seconds = pd.merge(total_seconds, starter_seconds, left_index=True, right_index=True, how='inner')
    seconds['starter_minutes_played_proportion'] = seconds['seconds_played_y']/seconds['seconds_played_x']

    game_player_stats.set_index('game_key',inplace=True)
    game_player_stats = pd.merge(game_player_stats,seconds['starter_minutes_played_proportion'],left_index=True,right_index=True,how='inner')

    bench_pl_min = player[player['starter_flag']==False].groupby(['game_key'])['plus_minus'].sum()
    game_player_stats = pd.merge(game_player_stats,bench_pl_min, left_index=True, right_index=True, how='inner')
    game_player_stats = game_player_stats.rename(columns={'plus_minus':'bench_plus_minus'})

    ## Merge aggregated stats in to games by team dataframe
    games_by_team = pd.merge(games_by_team,game_player_stats, left_index=True, right_index=True,how='inner')

    ## Create dataframe to capture opponent aggregated stats
    game_player_stats_opponent = game_player_stats.copy()
    
    # Reset index so it can be modified to temporarily swith 'h' with 'a'
    game_player_stats_opponent.reset_index(drop=False, inplace=True)
    game_player_stats_opponent['game_key'] = game_player_stats_opponent['game_key'].apply(switch_key)

    #Rename columns to opponent columns
    game_player_stats_opponent = game_player_stats_opponent.rename(columns={'starter_minutes_played_proportion':'opponnent_starter_minutes_played_proportion','bench_plus_minus':'opponent_bench_plus_minus'})

    #Reset index and merge
    game_player_stats_opponent.set_index('game_key', inplace=True)
    games_by_team = pd.merge(games_by_team,game_player_stats_opponent,left_index=True,right_index=True,how='inner')

    #Create win/loss streak and weighted average columns
    games_by_team_with_extras = pd.DataFrame()

    #Create data frame with stats needed for model
    for team in games_by_team['team'].unique():
        team_games = games_by_team.loc[games_by_team['team']==team].sort_values(by='game_date')
        team_games = generate_streak_info(team_games,'is_win')
        team_games['streak_counter_is_win'] = [x * -1 if y == 0 else x for x,y in zip(team_games['streak_counter_is_win'],team_games['is_win'])]
        team_games['incoming_is_win_streak'] = team_games['streak_counter_is_win'].shift()
        for col in wma_columns:
            team_games = create_linear_weighted_moving_average(team_games,col,W)
            team_games[f'incoming_wma_{W}_{col}'] = team_games[f'wma_{W}_{col}'].shift()
        games_by_team_with_streak = pd.concat([games_by_team_with_streak, team_games])

    games_by_team = games_by_team_with_extras.copy()

    #Drop first W rows for each team with no incoming weighted average
    model_game_data = games_by_team.dropna(subset=['incoming_wma_10_pace'])

    #Convert data types to prepare for load to bigquery
    model_game_data = model_game_data.astype({'season':int, 'is_win':int})
    
    #Reset index to load game_date
    model_game_data.reset_index(drop=False,inplace=True)

    #Create new client and load table to Big Query
    bqclient = bigquery.Client(project=my_project_id)
    #Publish model data
    job_config = bigquery.LoadJobConfig()
    job_config.autodetect='True'
    job_config.create_disposition = 'CREATE_IF_NEEDED'
    job_config.write_disposition = 'WRITE_APPEND'
    job_config.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="game_date")
    ## Set schema for specific columns where more information is needed (e.g. not NULLABLE or specific date/time)
    job_config.schema = [
        bigquery.SchemaField('game_key','STRING', 'REQUIRED'),
        bigquery.SchemaField('team','STRING', 'REQUIRED'),
        bigquery.SchemaField('opponent','STRING', 'REQUIRED'),
        bigquery.SchemaField('game_date','DATE'),
    ]
    job_model = bqclient.load_table_from_dataframe(model_game_data, model_table_name, job_config=job_config)

    model_result = job_model.result()
    model_message = (
        f'Job ID: {model_result.job_id} '
        f'was started {model_result.started} '
        f'and ended {model_result.ended} '
        f'loading {model_result.output_rows} row(s) '
        f'to {model_result.destination}')

    return model_message












