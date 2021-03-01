import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from google.cloud import storage
import os


def get_games(startDate,endDate):
    ##########################################################################
    # Get Distinct Months for schedule to scrape
    ##########################################################################

    delta = endDate - startDate
    
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
                    r['game_day'] = datetime.strptime(v1.text, '%a, %b %d, %Y').strftime("%A")

                    v2 = row.find('td',{"data-stat": "game_start_time"})
                    r['game_start_time'] = v2.text if v2 else None

                    v3 = row.find('td',{"data-stat": "visitor_team_name"})
                    r['visitor_team_name'] = v3.text
                    r['away_abbr'] = v3['csk'].split('.')[0]

                    v4 = row.find('td',{"data-stat": "home_team_name"})
                    r['home_team_name'] = v4.text
                    r['home_abbr'] = v4['csk'].split('.')[0]

                    if r['game_start_time']:
                        v12 = r['away_abbr'] + r['game_date'].replace('-','') + r['home_abbr'] + r['game_start_time'].replace(':','')
                    else:
                        v12 = r['away_abbr'] + r['game_date'].replace('-','') + r['home_abbr']
                    r['game_key'] = v12 if v12 else None

                    schedule.append(r)
                
    return schedule

def write_to_bucket(request):
    
    # Use schedule days if in request, otherwise default to 2 weeks (14 days)
    try:
        if type(request) == 'dict':
            request_json = request
        else:
            request_json = request.get_json()      
        if request_json and 'ScheduleDays' in request_json:
            schedule_days = request_json['ScheduleDays']
        else:
            schedule_days = 14
    except Exception as e:
        raise ValueError("Invalid input. Please provide ScheduleDays as an integer") from e
    
    startDate = (datetime.now()).date()
    endDate = (startDate + timedelta(days=schedule_days))
    schedule = get_games(startDate,endDate) 
    
    # Upload schedule to default app engine storage bucket
    game_date = pd.DataFrame(schedule)
    client = storage.Client()
    bucket_name = os.environ.get("CLOUD_STORAGE_BUCKET")
    bucket = client.bucket(bucket_name)
    bucket.blob('static/upcoming.json').upload_from_string(game_date.to_json(), 'text/json')

    return 'Successfully updated bucket with upcoming games'
