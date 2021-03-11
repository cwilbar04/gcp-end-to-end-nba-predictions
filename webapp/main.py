from model import predicted_pointspread
from flask import Flask, render_template, request#, url_for, redirect
from google.cloud import storage
from google.cloud import firestore
from google.cloud import bigquery
import json
import os



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ChooseTeams')
def ChooseTeams():
    # For the sake of example, use static list of NBA teams
    # This will be replaced with real information in later steps.
    # nba_teams = ['Atlanta Hawks',
    #                 'Boston Celtics',
    #                 'Brooklyn Nets',
    #                 'Charlotte Hornets',
    #                 'Chicago Bulls',
    #                 'Cleveland Cavaliers',
    #                 'Dallas Mavericks',
    #                 'Denver Nuggets',
    #                 'Detroit Pistons',
    #                 'Golden State Warriors',
    #                 'Houston Rockets',
    #                 'Indiana Pacers',
    #                 'Los Angeles Clippers',
    #                 'Los Angeles Lakers',
    #                 'Memphis Grizzlies',
    #                 'Miami Heat',
    #                 'Milwaukee Bucks',
    #                 'Minnesota Timberwolves',
    #                 'New Orleans Pelicans',
    #                 'New York Knicks',
    #                 'Oklahoma City Thunder',
    #                 'Orlando Magic',
    #                 'Philadelphia 76ers',
    #                 'Phoenix Suns',
    #                 'Portland Trail Blazers',
    #                 'Sacramento Kings',
    #                 'San Antonio Spurs',
    #                 'Toronto Raptors',
    #                 'Utah Jazz',
    #                 'Washington Wizards'
    #                ]
    
    # Consider using static list to save resource cost and exclude old teams
    db = firestore.Client(project=os.environ.get('GOOGLE_CLOUD_PROJECT'))
    docs = db.collection('team_model_data').stream()
    nba_teams = []
    for doc in docs:
        nba_teams.append(doc.id)

    
    client = bigquery.Client(project=os.environ.get('GOOGLE_CLOUD_PROJECT'))
    dataset_id = 'nba'
    models = client.list_models(dataset_id) 
    model_names = [model.model_id for model in models] 

    return render_template('ChooseTeams.html', teams=nba_teams, models=model_names)

@app.route('/ChooseTeams', methods=['POST'])
def ChooseTeamsPost():
    teams = {'HomeTeam':request.form['HomeTeam'], 'AwayTeam':request.form['AwayTeam'], 'Model':request.form['Model']}
    final_output = predicted_pointspread(teams)
    return render_template('ChooseTeamsPost.html', final_output=final_output)

@app.route('/UpcomingGames')
def UpcomingGames():
    client = storage.Client(project=os.environ.get('GOOGLE_CLOUD_PROJECT'))
    bucket_name = f'{os.environ.get("GOOGLE_CLOUD_PROJECT")}.appspot.com' 
    bucket = client.bucket(bucket_name)
    blob = bucket.blob('static/upcoming.json').download_as_string()
    data = json.loads(blob.decode("utf-8").replace("'",'"'))
    home_teams = list(data['home_team_name'].values())
    away_teams = list(data['visitor_team_name'].values())
    game_day = list(data['game_day'].values())
    game_date = list(data['game_date'].values())
    game_start_time = list(data['game_start_time'].values())
    games = []
    for i in range(len(home_teams)):
        games.append(f'{away_teams[i]} vs. {home_teams[i]} at {game_start_time[i]} on {game_day[i]}, {game_date[i]}')
    return render_template('UpcomingGames.html', games=games, home_teams = home_teams, away_teams=away_teams, game_day=game_day, game_date = game_date, game_start_time = game_start_time)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,s
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)