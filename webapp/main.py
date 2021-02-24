#import datetime
from model import predicted_pointspread
from flask import Flask, render_template, request#, url_for, redirect
#import pandas as pd
#import numpy as np

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ChooseTeams')
def ChooseTeams():
    # For the sake of example, use static list of NBA teams
    # This will be replaced with real information in later steps.
    nba_teams = ['Atlanta Hawks',
                    'Boston Celtics',
                    'Brooklyn Nets',
                    'Charlotte Hornets',
                    'Chicago Bulls',
                    'Cleveland Cavaliers',
                    'Dallas Mavericks',
                    'Denver Nuggets',
                    'Detroit Pistons',
                    'Golden State Warriors',
                    'Houston Rockets',
                    'Indiana Pacers',
                    'Los Angeles Clippers',
                    'Los Angeles Lakers',
                    'Memphis Grizzlies',
                    'Miami Heat',
                    'Milwaukee Bucks',
                    'Minnesota Timberwolves',
                    'New Orleans Pelicans',
                    'New York Knicks',
                    'Oklahoma City Thunder',
                    'Orlando Magic',
                    'Philadelphia 76ers',
                    'Phoenix Suns',
                    'Portland Trail Blazers',
                    'Sacramento Kings',
                    'San Antonio Spurs',
                    'Toronto Raptors',
                    'Utah Jazz',
                    'Washington Wizards'
                   ]
    return render_template('ChooseTeams.html', teams=nba_teams)

@app.route('/ChooseTeams', methods=['POST'])
def ChooseTeamsPost():
    form_dict = {'HomeTeam':request.form['HomeTeam'], 'AwayTeam':request.form['AwayTeam']}
    final_output = predicted_pointspread(form_dict)
    return render_template('ChooseTeamsPost.html', final_output=final_output)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,s
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)