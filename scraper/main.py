import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from google.cloud import bigquery

def get_max_game_date():
    client = bigquery.Client()
    
    QUERY = (
    "SELECT date_add(max(game_date), INTERVAL 1 day) as max_game_date FROM `nba.raw_basketballreference_game`"
    )
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    
    for result in rows:
        load_date = result.max_game_date
    
    return load_date

def get_game_players(soup, player_game_data, id_string, game_key, stat_type, h_or_a, team_abbrev, game_date):
    rows = soup.find('table', id=id_string).find('tbody').find_all('tr')
    cnt = 1

    #print(str(rows))
    for player in rows:
        game_players = {}
        game_players['game_key'] = game_key
        game_players['game_date'] = game_date
        game_players['h_or_a'] = h_or_a
        game_players['team_abbrev'] = team_abbrev
        game_players['stat_period'] = stat_type
        game_players['player'] = player.find('th',{"data-stat": "player"}).text
        #print(game_players['player'])
        
        player_node = player.find('th',{"data-stat": "player"})
        
        # Ignore Header Line
        if game_players['player'] != 'Reserves' and player_node.has_attr('data-append-csv'):
        
            a = player.find('th',{"data-stat": "player"}).find('a',href=True)
            if a is not None:
                game_players['player_link'] = a['href']
            else:
                game_players['player_link'] = None
            
            game_players['player_key'] = player_node['data-append-csv']
            game_players['reason'] = get_text(player.find('td',{"data-stat": "reason"}))
            game_players['mp'] = get_text(player.find('td',{"data-stat": "mp"}))
            game_players['fg'] = get_text(player.find('td',{"data-stat": "fg"}))
            game_players['fga'] = get_text(player.find('td',{"data-stat": "fga"}))
            game_players['fg_pct'] = get_text(player.find('td',{"data-stat": "fg_pct"}))
            game_players['fg3'] = get_text(player.find('td',{"data-stat": "fg3"}))
            game_players['fg3a'] = get_text(player.find('td',{"data-stat": "fg3a"}))
            game_players['fg3_pct'] = get_text(player.find('td',{"data-stat": "fg3_pct"}))
            game_players['ft'] = get_text(player.find('td',{"data-stat": "ft"}))
            game_players['fta'] = get_text(player.find('td',{"data-stat": "fta"}))
            game_players['ft_pct'] = get_text(player.find('td',{"data-stat": "ft_pct"}))
            game_players['orb'] = get_text(player.find('td',{"data-stat": "orb"}))
            game_players['drb'] = get_text(player.find('td',{"data-stat": "drb"}))
            game_players['trb'] = get_text(player.find('td',{"data-stat": "trb"}))
            game_players['ast'] = get_text(player.find('td',{"data-stat": "ast"}))
            game_players['stl'] = get_text(player.find('td',{"data-stat": "stl"}))
            game_players['blk'] = get_text(player.find('td',{"data-stat": "blk"}))
            game_players['tov'] = get_text(player.find('td',{"data-stat": "tov"}))
            game_players['pf'] = get_text(player.find('td',{"data-stat": "pf"}))
            game_players['pts'] = get_text(player.find('td',{"data-stat": "pts"}))
            game_players['plus_minus'] = get_text(player.find('td',{"data-stat": "plus_minus"}))
            game_players['player_stat_key'] = game_players['game_key'] + '|' + game_players['player_key'] + '|' + game_players['stat_period'] 
            if cnt <= 5:
                game_players['starter_flag'] = True 
            else:
                game_players['starter_flag'] = False
            game_players['load_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            #print(game_players)
            player_game_data.append(game_players)
            cnt += 1

    return player_game_data
   
def get_text(stat):
    if stat is not None:
        if stat.text != "":
            txt = stat.text
        else:
            txt = None
    else:
        txt = None
    return txt

def  nba_basketballreference_scraper(request):
   
    # Config
    client = bigquery.Client()
    
    ##########################################################################
    # Input Data Check
    ##########################################################################
    
    try:
        request_json = request.get_json()
        if request_json and 'StartDate' not in request_json:  
            startDate = get_max_game_date().strftime("%Y-%m-%d").date()
        else:
            startDate = datetime.strptime(request_json['StartDate'], '%Y-%m-%d').date()
        if request_json and 'EndDate' not in request_json:  
            endDate = datetime.now().strftime("%Y-%m-%d").date() 
        else:
            endDate = datetime.strptime(request_json['EndDate'], '%Y-%m-%d').date()
    except Exception as e:
        raise ValueError("Start & End dates must be in YYYY-MM-DD format") from e
    
    # Distinct list of Months between start and end date
    delta = endDate - startDate       # as timedelta
    
    if delta.days < 0:
        raise ValueError("Start Date can't be before End Date") 
    
    ##########################################################################
    # Get Distinct Months for schedule to scrape
    ##########################################################################
    
    yearmonths = []
    for i in range(delta.days + 1):
        r = {}
        day = startDate + timedelta(days=i)
        r['monthname'] = day.strftime('%B').lower()
        if day.month > 9:
            r['year'] = day.year + 1
        else:
            r['year'] = day.year
        if r not in yearmonths: 
            yearmonths.append(r)
    #print(yearmonths)
    
    ##########################################################################
    # Scrape Schedule
    ##########################################################################
    player_game_rows_loaded = 0
    game_rows_loaded = 0
    
    try:

        schedule = []
        for v in yearmonths:
            year = str(v['year'])
            month = v['monthname']
            url = 'https://www.basketball-reference.com/leagues/NBA_' + year + '_games-' + month + '.html'
            #print(url)
        
            html = requests.get(url)
            
            if html.ok:
                soup = BeautifulSoup(html.content, 'html.parser')  
            else:
                print(f'No data for {month} {year} because enountered error code {html.status_code}')
                continue

            rows = soup.find('table', id="schedule").find('tbody').find_all('tr')
            #print(rows)
            
            for row in rows:
                game_date_node = row.find('th',{"data-stat": "date_game"})
                if game_date_node is not None:

                    game_date = datetime.strptime(game_date_node.text, '%a, %b %d, %Y').date()
                    if game_date >= startDate and game_date <= endDate:
                        #cells = row.find_all(['td', 'th'])
                        r = {}
                        #r.setdefault(game_start_time, []).append(value)

                        v1 = row.find('th',{"data-stat": "date_game"})
                        #r[k1] = v1.text
                        r['game_date'] = datetime.strptime(v1.text, '%a, %b %d, %Y').strftime("%Y-%m-%d")
                        
                        v2 = row.find('td',{"data-stat": "game_start_time"})
                        r['game_start_time'] = v2.text if v2 else None
                        
                        v3 = row.find('td',{"data-stat": "visitor_team_name"})
                        r['visitor_team_name'] = v3.text
                        r['away_abbr'] = v3['csk'].split('.')[0]
                        
                        v4 = row.find('td',{"data-stat": "visitor_pts"})
                        r['visitor_pts'] = v4.text if v4 else None
                        
                        v5 = row.find('td',{"data-stat": "home_team_name"})
                        r['home_team_name'] = v5.text
                        r['home_abbr'] = v5['csk'].split('.')[0]
                        
                        v6 = row.find('td',{"data-stat": "home_pts"})
                        r['home_pts'] = v6.text if v6 else None
                        
                        v7 = row.find('td',{"data-stat": "box_score_text"}).find('a',href=True)
                        r['box_score_url'] = v7['href'] if v7 else None
                            
                        v8 = row.find('td',{"data-stat": "attendance"})
                        r['attendance'] = v8.text if v8 else None
                        
                        v9 = row.find('td',{"data-stat": "overtimes"})
                        r['overtimes'] = v9.text if v9 else None
                        
                        if r['game_start_time']:
                            v12 = r['away_abbr'] + r['game_date'].replace('-','') + r['home_abbr'] + r['game_start_time'].replace(':','')
                        else:
                            v12 = r['away_abbr'] + r['game_date'].replace('-','') + r['home_abbr']
                        r['game_key'] = v12 if v12 else None
                    
                        schedule.append(r)
            #print(schedule)            
        
            ##########################################################################
            # Scrape Games in Schedule
            ##########################################################################
            games_data = []
            player_game_data = []

            for game in schedule:
                if 'box_score_url' in game and game['box_score_url'] != "" and game['box_score_url'] is not None:


                    url = "https://www.basketball-reference.com" + game['box_score_url']

                    #print(url)
                    r = requests.get(url)
                    #print('here2')
                    soup = BeautifulSoup(str(r.content).replace("<!--","").replace('-->',''), 'html.parser')

                    ##############################################
                    # Line Score
                    rows = soup.find('table', id="line_score").find_all('tr')

                    # Away Line Score
                    r_num = 1
                    for away in rows[2].find_all('td'):
                        test_strong = away.find('strong') # Strong represents the total score ... ignore
                        if test_strong is None: #and r_num > 0
                            k='a_g' + str(r_num) + '_score'
                            game[k] = away.text if away.text != "" else None
                        r_num+=1

                    # Home Line Score
                    r_num = 1
                    for home in rows[3].find_all('td'):
                        test_strong = home.find('strong') # Strong represents the total score ... ignore
                        if test_strong is None: #and r_num > 0
                            k='h_g' + str(r_num) + '_score'
                            game[k] = home.text if home.text != "" else None
                        r_num+=1    

                    ##############################################
                    # Four Facts
                    rows = soup.find('table', id="four_factors").find_all('tr')

                    # Away Four Factors
                    game['a_ff_pace'] = rows[2].find('td',{"data-stat": "pace"}).text
                    game['a_ff_efg_pct'] = rows[2].find('td',{"data-stat": "efg_pct"}).text
                    game['a_ff_tov_pct'] = rows[2].find('td',{"data-stat": "tov_pct"}).text
                    game['a_ff_orb_pct'] = rows[2].find('td',{"data-stat": "orb_pct"}).text
                    game['a_ff_ft_rate'] = rows[2].find('td',{"data-stat": "ft_rate"}).text
                    game['a_ff_off_rtg'] = rows[2].find('td',{"data-stat": "off_rtg"}).text

                    # Home Four Factors
                    game['h_ff_pace'] = rows[3].find('td',{"data-stat": "pace"}).text
                    game['h_ff_efg_pct'] = rows[3].find('td',{"data-stat": "efg_pct"}).text
                    game['h_ff_tov_pct'] = rows[3].find('td',{"data-stat": "tov_pct"}).text
                    game['h_ff_orb_pct'] = rows[3].find('td',{"data-stat": "orb_pct"}).text
                    game['h_ff_ft_rate'] = rows[3].find('td',{"data-stat": "ft_rate"}).text
                    game['h_ff_off_rtg'] = rows[3].find('td',{"data-stat": "off_rtg"}).text
                    game['load_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")        

                    #now = datetime.now() # current date and time
                    #now.strftime("%m/%d/%Y, %H:%M:%S")


                    #player_game_data = []
                    game_date = game['game_date']

                    ##############################################
                    # Game Box - Home
                    #box-WAS-q1-basic
                    stat_type = "game"
                    h_or_a = "h"
                    team_abbrev = game['home_abbr']
                    id_string = "box-" + game['home_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Game Box - Away
                    #box-WAS-q1-basic
                    stat_type = "game"
                    h_or_a = "a"
                    team_abbrev = game['away_abbr']
                    id_string = "box-" + game['away_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q1 Box - Home
                    stat_type = "q1"
                    h_or_a = "h"
                    team_abbrev = game['home_abbr']
                    id_string = "box-" + game['home_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q1 Box - Away
                    stat_type = "q1"
                    h_or_a = "a"
                    team_abbrev = game['away_abbr']
                    id_string = "box-" + game['away_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q2 Box - Home
                    stat_type = "q2"
                    h_or_a = "h"
                    team_abbrev = game['home_abbr']
                    id_string = "box-" + game['home_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q2 Box - Away
                    stat_type = "q2"
                    h_or_a = "a"
                    team_abbrev = game['away_abbr']
                    id_string = "box-" + game['away_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q3 Box - Home
                    stat_type = "q3"
                    h_or_a = "h"
                    team_abbrev = game['home_abbr']
                    id_string = "box-" + game['home_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q3 Box - Away
                    stat_type = "q3"
                    h_or_a = "a"
                    team_abbrev = game['away_abbr']
                    id_string = "box-" + game['away_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q4 Box - Home
                    stat_type = "q4"
                    h_or_a = "h"
                    team_abbrev = game['home_abbr']
                    id_string = "box-" + game['home_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    ##############################################
                    # Q4 Box - Away
                    stat_type = "q4"
                    h_or_a = "a"
                    team_abbrev = game['away_abbr']
                    id_string = "box-" + game['away_abbr'] + "-" + stat_type + "-basic"
                    player_game_data = get_game_players(soup, player_game_data, id_string, game['game_key'], stat_type, h_or_a, team_abbrev, game_date)

                    games_data.append(game)


            ##########################################################################
            # Save to BigQuery
            ##########################################################################

            # print(player_game_data)
            # print(games_data)

            print(f'Loading data for {month} {year}')
            #player game data
            pandas_player_game_data = pd.DataFrame(player_game_data)
            pandas_player_game_data['game_date'] = pandas_player_game_data['game_date'].astype('datetime64[ns]')
            pandas_player_game_data['load_datetime'] = pandas_player_game_data['load_datetime'].astype('datetime64[ns]')
            job_config = bigquery.LoadJobConfig()
            job_config.autodetect='True'
            job_config.create_disposition = 'CREATE_IF_NEEDED'
            job_config.write_disposition = 'WRITE_APPEND'
             ## Set schema for specific columns where more information is needed (e.g. not NULLABLE or specific date/time)
            job_config.schema = [
                bigquery.SchemaField('player_stat_key','STRING', 'REQUIRED'),
                bigquery.SchemaField('game_date','DATE'),
                bigquery.SchemaField('load_datetime','TIMESTAMP'),
                bigquery.SchemaField('starter_flag','BOOL')
            ]
            job_config.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="game_date")
            job_player = client.load_table_from_dataframe(pandas_player_game_data, 'nba.raw_basketballreference_playerbox', job_config=job_config)
            player_result = job_player.result()
            player_message = (
                f'Job ID: {player_result.job_id} '
                f'was started {player_result.started} '
                f'and ended {player_result.ended} '
                f'loading {player_result.output_rows} row(s) '
                f'to {player_result.destination}')
            print(player_message)
            player_game_rows_loaded = player_game_rows_loaded + player_result.output_rows

            #game data
            pandas_games_data = pd.DataFrame(games_data)
            pandas_games_data['game_date'] = pandas_games_data['game_date'].astype('datetime64[ns]')
            pandas_games_data['load_datetime'] = pandas_games_data['load_datetime'].astype('datetime64[ns]')
            pandas_games_data['game_start_time'] = pandas_games_data['game_start_time'].astype('datetime64[ns]')
            job_config = bigquery.LoadJobConfig()
            job_config.autodetect='True'
            job_config.create_disposition = 'CREATE_IF_NEEDED'
            job_config.write_disposition = 'WRITE_APPEND'
            ## Set schema for specific columns where more information is needed (e.g. not NULLABLE or specific date/time)
            job_config.schema = [
                bigquery.SchemaField('game_key','STRING', 'REQUIRED'),
                bigquery.SchemaField('game_date','STRING', 'REQUIRED'),
                bigquery.SchemaField('home_team_name','STRING', 'REQUIRED'),
                bigquery.SchemaField('home_abbr','STRING', 'REQUIRED'),
                bigquery.SchemaField('visitor_team_name','STRING', 'REQUIRED'),
                bigquery.SchemaField('away_abbr','STRING', 'REQUIRED'),
                bigquery.SchemaField('game_date','DATE'),
                bigquery.SchemaField('load_datetime','TIMESTAMP'),
                bigquery.SchemaField('game_start_time','TIMESTAMP')
            ]
            job_config.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="game_date")
            job_game = client.load_table_from_dataframe(pandas_games_data, 'nba.raw_basketballreference_game', job_config=job_config)
            game_result = job_game.result()
            game_message = (
                f'Job ID: {game_result.job_id} '
                f'was started {game_result.started} '
                f'and ended {game_result.ended} '
                f'loading {game_result.output_rows} row(s) '
                f'to {game_result.destination}')
            print(game_message)
            game_rows_loaded = game_rows_loaded + game_result.output_rows

        return f'Successfully loaded {player_game_rows_loaded} row(s) to raw_basketballreference_playerbox and {game_rows_loaded} to raw_basketballreference_game'

    except Exception as e: 
        raise ValueError("Load Job Failed - Check error log for specific details") from e